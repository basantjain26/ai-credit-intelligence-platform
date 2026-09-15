from __future__ import annotations

import os
from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import psycopg2
from dotenv import load_dotenv

from src.transaction_investigation.anomaly_detection import (
    TransactionAnomalyDetector,
    TransactionAnomalyResult,
)
from src.transaction_investigation.feature_engineering import (
    TransactionFeatureBaseline,
    TransactionFeatureEngineer,
)


load_dotenv()


TRAINING_END = datetime(
    2026,
    6,
    30,
    23,
    59,
    59,
)


def _get_connection():
    """
    Create PostgreSQL connection.

    Customer/application IDs are NOT accepted here.
    Case scope is bound by TransactionInvestigationContext.
    """

    return psycopg2.connect(
        host=os.getenv(
            "DB_HOST",
            "localhost",
        ),
        port=int(
            os.getenv(
                "DB_PORT",
                "5434",
            )
        ),
        dbname=os.getenv(
            "DB_NAME",
            "credit_intelligence",
        ),
        user=os.getenv(
            "DB_USER",
            "credit_user",
        ),
        password=os.getenv(
            "DB_PASSWORD",
            "credit_password",
        ),
    )


class TransactionInvestigationContext:
    """
    Trusted transaction-investigation state for one credit case.

    Expensive work is performed ONCE when the context is built:

        1. load transactions
        2. split training/inference windows
        3. fit feature baseline
        4. engineer features
        5. train Isolation Forest
        6. score inference transactions
        7. load related-party context

    Agent tools then read this already-prepared state.

    The LLM never controls customer_id or application_id.
    """

    def __init__(
        self,
        customer_id: str,
        application_id: str,
        training_transactions: list[dict[str, Any]],
        inference_transactions: list[dict[str, Any]],
        training_features: list[dict[str, Any]],
        inference_features: list[dict[str, Any]],
        anomaly_results: list[TransactionAnomalyResult],
        feature_baseline: TransactionFeatureBaseline,
        related_parties: list[dict[str, Any]],
        contamination: float,
        model_version: str,
    ) -> None:

        self.customer_id = customer_id
        self.application_id = application_id

        self.training_transactions = training_transactions
        self.inference_transactions = inference_transactions

        self.training_features = training_features
        self.inference_features = inference_features

        self.anomaly_results = anomaly_results

        self.feature_baseline = feature_baseline

        self.related_parties = related_parties

        self.contamination = contamination
        self.model_version = model_version

        self._feature_lookup = {
            row["transaction_id"]: row
            for row in inference_features
        }

        self._anomaly_lookup = {
            result.transaction_id: result
            for result in anomaly_results
        }

    # =========================================================
    # BUILD CONTEXT
    # =========================================================

    @classmethod
    def build(
        cls,
        customer_id: str,
        application_id: str,
        contamination: float = 0.05,
    ) -> "TransactionInvestigationContext":
        """
        Build the complete transaction investigation context.

        ML training happens here ONCE.

        It does not happen every time the agent calls a tool.
        """

        if not customer_id:
            raise ValueError(
                "customer_id is required"
            )

        if not application_id:
            raise ValueError(
                "application_id is required"
            )

        connection = _get_connection()

        try:
            cls._validate_case_scope(
                connection=connection,
                customer_id=customer_id,
                application_id=application_id,
            )

            transactions = cls._load_transactions(
                connection=connection,
                customer_id=customer_id,
            )

            related_parties = cls._load_related_parties(
                connection=connection,
                customer_id=customer_id,
            )

        finally:
            connection.close()

        if not transactions:
            raise RuntimeError(
                "No bank transactions found for "
                f"customer {customer_id}"
            )

        (
            training_transactions,
            inference_transactions,
        ) = cls._split_transactions(
            transactions
        )

        if len(training_transactions) < 20:
            raise RuntimeError(
                "Insufficient historical transactions "
                "for Isolation Forest training. "
                f"Found {len(training_transactions)}."
            )

        if not inference_transactions:
            raise RuntimeError(
                "No inference transactions found after "
                f"{TRAINING_END}."
            )

        related_party_names = {
            row["party_name"]
            for row in related_parties
            if row.get("party_name")
        }

        feature_engineer = (
            TransactionFeatureEngineer(
                home_country="India",
                related_party_names=related_party_names,
            )
        )

        training_features = (
            feature_engineer.fit_transform(
                training_transactions
            )
        )

        inference_features = (
            feature_engineer.transform(
                inference_transactions,
                training=False,
            )
        )

        detector = (
            TransactionAnomalyDetector(
                contamination=contamination,
                n_estimators=200,
                random_state=42,
            )
        )

        detector.fit(
            training_features
        )

        anomaly_results = detector.score(
            inference_features
        )

        return cls(
            customer_id=customer_id,
            application_id=application_id,
            training_transactions=training_transactions,
            inference_transactions=inference_transactions,
            training_features=training_features,
            inference_features=inference_features,
            anomaly_results=anomaly_results,
            feature_baseline=feature_engineer.get_baseline(),
            related_parties=related_parties,
            contamination=contamination,
            model_version=(
                anomaly_results[0].model_version
            ),
        )

    # =========================================================
    # DATABASE
    # =========================================================

    @staticmethod
    def _validate_case_scope(
        connection,
        customer_id: str,
        application_id: str,
    ) -> None:
        """
        Ensure the application actually belongs to the trusted
        customer before building the investigation.
        """

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM loan_applications
                WHERE application_id = %s
                  AND customer_id = %s
                LIMIT 1
                """,
                (
                    application_id,
                    customer_id,
                ),
            )

            row = cursor.fetchone()

        if not row:
            raise RuntimeError(
                "Application/customer scope validation failed "
                f"for application={application_id}, "
                f"customer={customer_id}"
            )

    @staticmethod
    def _load_transactions(
        connection,
        customer_id: str,
    ) -> list[dict[str, Any]]:

        sql = """
            SELECT
                transaction_id,
                account_id,
                customer_id,
                transaction_timestamp,
                direction,
                transaction_type,
                amount,
                currency,
                counterparty_name,
                counterparty_account,
                counterparty_bank,
                merchant_category,
                country,
                channel,
                description,
                balance_after_transaction
            FROM bank_transactions
            WHERE customer_id = %s
            ORDER BY
                transaction_timestamp,
                transaction_id
        """

        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                (customer_id,),
            )

            column_names = [
                description[0]
                for description in cursor.description
            ]

            rows = cursor.fetchall()

        return [
            dict(
                zip(
                    column_names,
                    row,
                    strict=True,
                )
            )
            for row in rows
        ]

    @staticmethod
    def _load_related_parties(
        connection,
        customer_id: str,
    ) -> list[dict[str, Any]]:

        sql = """
            SELECT
                related_party_id,
                customer_id,
                party_name,
                party_type,
                relationship_type,
                linked_director_id,
                registration_number,
                risk_level,
                effective_from,
                effective_to
            FROM related_parties
            WHERE customer_id = %s
            ORDER BY party_name
        """

        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                (customer_id,),
            )

            column_names = [
                description[0]
                for description in cursor.description
            ]

            rows = cursor.fetchall()

        return [
            dict(
                zip(
                    column_names,
                    row,
                    strict=True,
                )
            )
            for row in rows
        ]
    # =========================================================
    # SPLIT
    # =========================================================

    @staticmethod
    def _split_transactions(
        transactions: list[dict[str, Any]],
    ) -> tuple[
        list[dict[str, Any]],
        list[dict[str, Any]],
    ]:

        training = []
        inference = []

        for transaction in transactions:
            timestamp = transaction[
                "transaction_timestamp"
            ]

            if timestamp <= TRAINING_END:
                training.append(
                    transaction
                )
            else:
                inference.append(
                    transaction
                )

        return (
            training,
            inference,
        )

    # =========================================================
    # LOOKUPS
    # =========================================================

    def get_feature_row(
        self,
        transaction_id: str,
    ) -> dict[str, Any] | None:

        return self._feature_lookup.get(
            transaction_id
        )

    def get_anomaly_result(
        self,
        transaction_id: str,
    ) -> TransactionAnomalyResult | None:

        return self._anomaly_lookup.get(
            transaction_id
        )


class TransactionInvestigationTools:
    """
    Controlled tools exposed to the future LLM agent.

    Trusted scope is bound when this object is created.

    The model can NEVER supply:
        customer_id
        application_id
    """

    def __init__(
        self,
        context: TransactionInvestigationContext,
    ) -> None:

        self.context = context

    # =========================================================
    # TOOL 1
    # =========================================================

    def get_transaction_summary(
        self,
    ) -> dict[str, Any]:
        """
        Return deterministic transaction summary for the
        inference/investigation period.
        """

        rows = (
            self.context.inference_features
        )

        credits = [
            row
            for row in rows
            if row["direction"] == "CREDIT"
        ]

        debits = [
            row
            for row in rows
            if row["direction"] == "DEBIT"
        ]

        total_credits = sum(
            (
                row["absolute_amount"]
                for row in credits
            ),
            Decimal("0"),
        )

        total_debits = sum(
            (
                row["absolute_amount"]
                for row in debits
            ),
            Decimal("0"),
        )

        largest_credit = self._largest_transaction(
            credits
        )

        largest_debit = self._largest_transaction(
            debits
        )

        international = [
            row
            for row in rows
            if row["is_international"] == 1
        ]

        related_party = [
            row
            for row in rows
            if row["is_related_party"] == 1
        ]

        counterparty_stats: dict[
            str,
            dict[str, Any],
        ] = {}

        for row in rows:
            name = (
                row["counterparty_name"]
                or "UNKNOWN"
            )

            stats = counterparty_stats.setdefault(
                name,
                {
                    "counterparty_name": name,
                    "transaction_count": 0,
                    "total_amount": Decimal("0"),
                },
            )

            stats["transaction_count"] += 1
            stats["total_amount"] += (
                row["absolute_amount"]
            )

        top_counterparties = sorted(
            counterparty_stats.values(),
            key=lambda item: item[
                "total_amount"
            ],
            reverse=True,
        )[:5]

        anomaly_count = sum(
            1
            for result
            in self.context.anomaly_results
            if result.is_anomaly
        )

        return self._json_safe(
            {
                "customer_id": (
                    self.context.customer_id
                ),

                "application_id": (
                    self.context.application_id
                ),

                "investigation_period": {
                    "start": min(
                        row["transaction_timestamp"]
                        for row in rows
                    ),
                    "end": max(
                        row["transaction_timestamp"]
                        for row in rows
                    ),
                },

                "transaction_count": len(
                    rows
                ),

                "credit_transaction_count": len(
                    credits
                ),

                "debit_transaction_count": len(
                    debits
                ),

                "total_credits": (
                    total_credits
                ),

                "total_debits": (
                    total_debits
                ),

                "largest_credit": (
                    largest_credit
                ),

                "largest_debit": (
                    largest_debit
                ),

                "international_transaction_count": len(
                    international
                ),

                "related_party_transaction_count": len(
                    related_party
                ),

                "ml_anomaly_count": (
                    anomaly_count
                ),

                "top_counterparties_by_value": (
                    top_counterparties
                ),

                "model_version": (
                    self.context.model_version
                ),

                "feature_version": (
                    self.context
                    .feature_baseline
                    .feature_version
                ),
            }
        )

    # =========================================================
    # TOOL 2
    # =========================================================

    def get_anomalous_transactions(
        self,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Return inference transactions ranked by ML anomaly
        score.

        By default only actual model-classified anomalies are
        returned.

        limit is model-controlled later, but bounded here.
        """

        if limit < 1:
            raise ValueError(
                "limit must be at least 1"
            )

        limit = min(
            limit,
            20,
        )

        ranked_anomalies = sorted(
            (
                result
                for result
                in self.context.anomaly_results
                if result.is_anomaly
            ),
            key=lambda result: (
                result.anomaly_score
            ),
            reverse=True,
        )

        output = []

        for rank, result in enumerate(
            ranked_anomalies[:limit],
            start=1,
        ):
            row = (
                self.context.get_feature_row(
                    result.transaction_id
                )
            )

            if row is None:
                raise RuntimeError(
                    "Missing feature lineage for "
                    f"{result.transaction_id}"
                )

            output.append(
                {
                    "rank": rank,

                    "transaction_id": (
                        result.transaction_id
                    ),

                    "transaction_timestamp": (
                        row["transaction_timestamp"]
                    ),

                    "direction": (
                        row["direction"]
                    ),

                    "transaction_type": (
                        row["transaction_type"]
                    ),

                    "amount": (
                        row["amount"]
                    ),

                    "currency": (
                        row["currency"]
                    ),

                    "counterparty_name": (
                        row["counterparty_name"]
                    ),

                    "country": (
                        row["country"]
                    ),

                    "description": (
                        row["description"]
                    ),

                    "is_anomaly": (
                        result.is_anomaly
                    ),

                    "anomaly_score": (
                        result.anomaly_score
                    ),

                    "raw_model_score": (
                        result.raw_model_score
                    ),

                    "model_prediction": (
                        result.model_prediction
                    ),

                    "model_name": (
                        result.model_name
                    ),

                    "model_version": (
                        result.model_version
                    ),

                    "feature_version": (
                        result.feature_version
                    ),

                    "ml_features": (
                        result.features
                    ),

                    "rule_context": {
                        "is_related_party": bool(
                            row[
                                "is_related_party"
                            ]
                        ),

                        "is_international": bool(
                            row[
                                "is_international"
                            ]
                        ),

                        "is_round_amount": bool(
                            row[
                                "is_round_amount"
                            ]
                        ),
                    },
                }
            )

        return self._json_safe(
            {
                "customer_id": (
                    self.context.customer_id
                ),

                "application_id": (
                    self.context.application_id
                ),

                "anomaly_count": len(
                    ranked_anomalies
                ),

                "returned_count": len(
                    output
                ),

                "contamination": (
                    self.context.contamination
                ),

                "model_version": (
                    self.context.model_version
                ),

                "transactions": (
                    output
                ),
            }
        )

    # =========================================================
    # TOOL 3
    # =========================================================

    def get_counterparty_context(
        self,
        counterparty_name: str,
    ) -> dict[str, Any]:
        """
        Investigate one counterparty inside the trusted
        customer's transaction history.

        The model controls only counterparty_name.
        """

        if not counterparty_name:
            raise ValueError(
                "counterparty_name is required"
            )

        target = self._normalize_name(
            counterparty_name
        )

        all_feature_rows = (
            self.context.training_features
            + self.context.inference_features
        )

        matching_rows = [
            row
            for row in all_feature_rows
            if self._normalize_name(
                row["counterparty_name"]
            ) == target
        ]

        related_party_records = [
            row
            for row
            in self.context.related_parties
            if self._normalize_name(
                row.get(
                    "party_name"
                )
            ) == target
        ]

        if not matching_rows:
            return self._json_safe(
                {
                    "customer_id": (
                        self.context.customer_id
                    ),

                    "application_id": (
                        self.context.application_id
                    ),

                    "counterparty_name": (
                        counterparty_name
                    ),

                    "found": False,

                    "is_related_party": bool(
                        related_party_records
                    ),

                    "related_party_records": (
                        related_party_records
                    ),

                    "message": (
                        "No matching bank transactions "
                        "were found for this counterparty."
                    ),
                }
            )

        total_amount = sum(
            (
                row["absolute_amount"]
                for row in matching_rows
            ),
            Decimal("0"),
        )

        debit_amount = sum(
            (
                row["absolute_amount"]
                for row in matching_rows
                if row["direction"] == "DEBIT"
            ),
            Decimal("0"),
        )

        credit_amount = sum(
            (
                row["absolute_amount"]
                for row in matching_rows
                if row["direction"] == "CREDIT"
            ),
            Decimal("0"),
        )

        inference_rows = [
            row
            for row in matching_rows
            if (
                row["transaction_timestamp"]
                > TRAINING_END
            )
        ]

        inference_results = []

        for row in inference_rows:
            result = (
                self.context.get_anomaly_result(
                    row["transaction_id"]
                )
            )

            inference_results.append(
                {
                    "transaction_id": (
                        row["transaction_id"]
                    ),

                    "transaction_timestamp": (
                        row["transaction_timestamp"]
                    ),

                    "direction": (
                        row["direction"]
                    ),

                    "amount": (
                        row["amount"]
                    ),

                    "currency": (
                        row["currency"]
                    ),

                    "country": (
                        row["country"]
                    ),

                    "description": (
                        row["description"]
                    ),

                    "is_anomaly": (
                        result.is_anomaly
                        if result
                        else None
                    ),

                    "anomaly_score": (
                        result.anomaly_score
                        if result
                        else None
                    ),

                    "model_version": (
                        result.model_version
                        if result
                        else None
                    ),
                }
            )

        countries = sorted(
            {
                row["country"]
                for row in matching_rows
                if row["country"]
            }
        )

        first_seen = min(
            row["transaction_timestamp"]
            for row in matching_rows
        )

        last_seen = max(
            row["transaction_timestamp"]
            for row in matching_rows
        )

        return self._json_safe(
            {
                "customer_id": (
                    self.context.customer_id
                ),

                "application_id": (
                    self.context.application_id
                ),

                "counterparty_name": (
                    matching_rows[0][
                        "counterparty_name"
                    ]
                ),

                "found": True,

                "transaction_count": len(
                    matching_rows
                ),

                "historical_transaction_count": (
                    len(matching_rows)
                    - len(inference_rows)
                ),

                "inference_transaction_count": len(
                    inference_rows
                ),

                "total_amount": (
                    total_amount
                ),

                "total_debits": (
                    debit_amount
                ),

                "total_credits": (
                    credit_amount
                ),

                "first_seen": (
                    first_seen
                ),

                "last_seen": (
                    last_seen
                ),

                "countries": (
                    countries
                ),

                "is_related_party": bool(
                    related_party_records
                ),

                "related_party_records": (
                    related_party_records
                ),

                "inference_transactions": (
                    inference_results
                ),
            }
        )

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _largest_transaction(
        rows: list[dict[str, Any]],
    ) -> dict[str, Any] | None:

        if not rows:
            return None

        row = max(
            rows,
            key=lambda item: (
                item["absolute_amount"]
            ),
        )

        return {
            "transaction_id": (
                row["transaction_id"]
            ),

            "transaction_timestamp": (
                row["transaction_timestamp"]
            ),

            "amount": (
                row["amount"]
            ),

            "currency": (
                row["currency"]
            ),

            "counterparty_name": (
                row["counterparty_name"]
            ),

            "country": (
                row["country"]
            ),
        }

    @staticmethod
    def _normalize_name(
        value: str | None,
    ) -> str:

        if not value:
            return ""

        return " ".join(
            value
            .strip()
            .lower()
            .split()
        )

    @classmethod
    def _json_safe(
        cls,
        value: Any,
    ) -> Any:
        """
        Convert database/Python values into JSON-safe values
        suitable for LLM tool responses.
        """

        if isinstance(value, Decimal):
            return float(value)

        # datetime must come before date because
        # datetime is a subclass of date.
        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if hasattr(
            value,
            "__dataclass_fields__",
        ):
            return cls._json_safe(
                asdict(value)
            )

        if isinstance(value, dict):
            return {
                key: cls._json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                cls._json_safe(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return [
                cls._json_safe(item)
                for item in value
            ]

        return value