import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from statistics import median
from typing import Any


FEATURE_VERSION = "transaction_features_v2"


ML_FEATURES = [
    "log_amount",
    "amount_vs_median",
    "is_debit",
    "counterparty_frequency",
    "counterparty_amount_ratio",
    "hours_since_previous_txn",
    "day_of_week",
]


@dataclass(frozen=True)
class TransactionFeatureBaseline:
    """
    Statistics learned ONLY from the historical training window.

    These values must be reused during inference so that
    training and serving use the same behavioral baseline.
    """

    median_amount: Decimal
    total_transaction_value: Decimal
    counterparty_frequency: dict[str, int]
    counterparty_total_amount: dict[str, Decimal]
    last_training_timestamp: datetime
    training_transaction_count: int
    feature_version: str


class TransactionFeatureEngineer:
    """
    Stateful transaction feature engineer.

    Lifecycle:

        fit(training_transactions)
                ↓
        learn historical baseline
                ↓
        transform(training_transactions)
                ↓
        train ML model

    Later:

        transform(new_transactions)
                ↓
        reuse historical baseline
                ↓
        ML inference

    This avoids recalculating behavioral statistics from the
    inference batch.
    """

    def __init__(
        self,
        home_country: str = "India",
        related_party_names: set[str] | None = None,
    ) -> None:

        self.home_country = self._normalize_name(
            home_country
        )

        self.related_party_names = {
            self._normalize_name(name)
            for name in (
                related_party_names or set()
            )
            if name
        }

        self.baseline: (
            TransactionFeatureBaseline | None
        ) = None

    # =========================================================
    # FIT
    # =========================================================

    def fit(
        self,
        transactions: list[dict[str, Any]],
    ) -> "TransactionFeatureEngineer":
        """
        Learn behavioral baseline statistics from historical
        training transactions.

        IMPORTANT:
        Only historical training data should be passed here.
        """

        if not transactions:
            raise ValueError(
                "Cannot fit feature engineer on "
                "an empty transaction dataset."
            )

        normalized_transactions = [
            self._normalize_transaction(
                transaction
            )
            for transaction in transactions
        ]

        normalized_transactions.sort(
            key=lambda row: (
                row["transaction_timestamp"],
                row["transaction_id"],
            )
        )

        absolute_amounts = [
            row["absolute_amount"]
            for row in normalized_transactions
        ]

        median_amount = Decimal(
            str(
                median(
                    absolute_amounts
                )
            )
        )

        total_transaction_value = sum(
            absolute_amounts,
            Decimal("0"),
        )

        frequency_counter = Counter(
            row["normalized_counterparty"]
            for row in normalized_transactions
            if row["normalized_counterparty"]
        )

        counterparty_total_amount: dict[
            str,
            Decimal,
        ] = defaultdict(
            lambda: Decimal("0")
        )

        for row in normalized_transactions:

            counterparty = (
                row["normalized_counterparty"]
            )

            if counterparty:
                counterparty_total_amount[
                    counterparty
                ] += row["absolute_amount"]

        self.baseline = (
            TransactionFeatureBaseline(
                median_amount=median_amount,

                total_transaction_value=(
                    total_transaction_value
                ),

                counterparty_frequency=dict(
                    frequency_counter
                ),

                counterparty_total_amount=dict(
                    counterparty_total_amount
                ),

                last_training_timestamp=(
                    normalized_transactions[-1][
                        "transaction_timestamp"
                    ]
                ),

                training_transaction_count=len(
                    normalized_transactions
                ),

                feature_version=FEATURE_VERSION,
            )
        )

        return self

    # =========================================================
    # TRANSFORM
    # =========================================================

    def transform(
        self,
        transactions: list[dict[str, Any]],
        *,
        training: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Transform transactions using the fitted historical
        baseline.

        training=True:
            Used when transforming the historical training
            dataset itself.

        training=False:
            Used for new inference transactions.

            Counterparty statistics and median amount still
            come ONLY from the historical training baseline.
        """

        self._require_fitted()

        if not transactions:
            return []

        normalized_transactions = [
            self._normalize_transaction(
                transaction
            )
            for transaction in transactions
        ]

        normalized_transactions.sort(
            key=lambda row: (
                row["transaction_timestamp"],
                row["transaction_id"],
            )
        )

        if training:
            previous_timestamp: datetime | None = None
        else:
            previous_timestamp = (
                self.baseline.last_training_timestamp
            )

        feature_rows: list[
            dict[str, Any]
        ] = []

        for row in normalized_transactions:

            feature_row = (
                self._build_feature_row(
                    row=row,
                    previous_timestamp=(
                        previous_timestamp
                    ),
                )
            )

            feature_rows.append(
                feature_row
            )

            previous_timestamp = (
                row["transaction_timestamp"]
            )

        return feature_rows

    # =========================================================
    # FIT + TRANSFORM
    # =========================================================

    def fit_transform(
        self,
        transactions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Fit historical baseline and transform the same
        historical training transactions.
        """

        self.fit(
            transactions
        )

        return self.transform(
            transactions,
            training=True,
        )

    # =========================================================
    # FEATURE CONSTRUCTION
    # =========================================================

    def _build_feature_row(
        self,
        row: dict[str, Any],
        previous_timestamp: datetime | None,
    ) -> dict[str, Any]:

        baseline = self.baseline

        amount = row[
            "absolute_amount"
        ]

        timestamp = row[
            "transaction_timestamp"
        ]

        counterparty = row[
            "normalized_counterparty"
        ]

        # -----------------------------------------------------
        # ML FEATURE 1
        # Log-transformed amount
        # -----------------------------------------------------

        log_amount = math.log1p(
            float(amount)
        )

        # -----------------------------------------------------
        # ML FEATURE 2
        # Amount relative to HISTORICAL median
        # -----------------------------------------------------

        if baseline.median_amount > 0:

            amount_vs_median = (
                amount
                / baseline.median_amount
            )

        else:

            amount_vs_median = (
                Decimal("0")
            )

        # -----------------------------------------------------
        # ML FEATURE 3
        # Debit / credit
        # -----------------------------------------------------

        is_debit = int(
            row["direction"] == "DEBIT"
        )

        # -----------------------------------------------------
        # ML FEATURE 4
        # HISTORICAL counterparty frequency
        #
        # New counterparty => 0
        # -----------------------------------------------------

        if counterparty:

            counterparty_frequency = (
                baseline
                .counterparty_frequency
                .get(
                    counterparty,
                    0,
                )
            )

        else:

            counterparty_frequency = 0

        # -----------------------------------------------------
        # ML FEATURE 5
        # HISTORICAL counterparty concentration
        #
        # New counterparty => 0
        # -----------------------------------------------------

        historical_counterparty_amount = (
            baseline
            .counterparty_total_amount
            .get(
                counterparty,
                Decimal("0"),
            )
            if counterparty
            else Decimal("0")
        )

        if (
            baseline.total_transaction_value
            > 0
        ):

            counterparty_amount_ratio = (
                historical_counterparty_amount
                / baseline.total_transaction_value
            )

        else:

            counterparty_amount_ratio = (
                Decimal("0")
            )

        # -----------------------------------------------------
        # ML FEATURE 6
        # Hours since previous transaction
        # -----------------------------------------------------

        if previous_timestamp is None:

            hours_since_previous = 0.0

        else:

            difference = (
                timestamp
                - previous_timestamp
            )

            hours_since_previous = (
                difference.total_seconds()
                / 3600.0
            )

            if hours_since_previous < 0:
                raise ValueError(
                    "Transactions must not occur before "
                    "the historical baseline timestamp."
                )

        # -----------------------------------------------------
        # ML FEATURE 7
        # Day of week
        # -----------------------------------------------------

        day_of_week = (
            timestamp.weekday()
        )

        # -----------------------------------------------------
        # RULE FEATURES
        # -----------------------------------------------------

        is_round_amount = int(
            self._is_round_amount(
                amount
            )
        )

        is_related_party = int(
            bool(
                counterparty
                and counterparty
                in self.related_party_names
            )
        )

        normalized_country = (
            row["normalized_country"]
        )

        is_international = int(
            bool(
                normalized_country
                and self.home_country
                and normalized_country
                != self.home_country
            )
        )

        return {
            # =============================================
            # SOURCE METADATA
            # =============================================

            "transaction_id": (
                row["transaction_id"]
            ),

            "account_id": (
                row["account_id"]
            ),

            "customer_id": (
                row["customer_id"]
            ),

            "transaction_timestamp": (
                timestamp
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

            "absolute_amount": (
                amount
            ),

            "currency": (
                row["currency"]
            ),

            "counterparty_name": (
                row["counterparty_name"]
            ),

            "counterparty_account": (
                row["counterparty_account"]
            ),

            "counterparty_bank": (
                row["counterparty_bank"]
            ),

            "merchant_category": (
                row["merchant_category"]
            ),

            "country": (
                row["country"]
            ),

            "channel": (
                row["channel"]
            ),

            "description": (
                row["description"]
            ),

            "balance_after_transaction": (
                row[
                    "balance_after_transaction"
                ]
            ),

            # =============================================
            # ML FEATURES
            # =============================================

            "log_amount": (
                log_amount
            ),

            "amount_vs_median": float(
                amount_vs_median
            ),

            "is_debit": (
                is_debit
            ),

            "counterparty_frequency": (
                counterparty_frequency
            ),

            "counterparty_amount_ratio": float(
                counterparty_amount_ratio
            ),

            "hours_since_previous_txn": (
                hours_since_previous
            ),

            "day_of_week": (
                day_of_week
            ),

            # =============================================
            # RULE FEATURES
            # =============================================

            "is_round_amount": (
                is_round_amount
            ),

            "is_related_party": (
                is_related_party
            ),

            "is_international": (
                is_international
            ),

            # =============================================
            # LINEAGE
            # =============================================

            "feature_version": (
                FEATURE_VERSION
            ),
        }

    # =========================================================
    # ML MATRIX
    # =========================================================

    @staticmethod
    def get_ml_matrix(
        feature_rows: list[
            dict[str, Any]
        ],
    ) -> list[list[float]]:

        return [
            [
                float(
                    row[feature_name]
                )
                for feature_name
                in ML_FEATURES
            ]
            for row in feature_rows
        ]

    # =========================================================
    # BASELINE INSPECTION
    # =========================================================

    def get_baseline(
        self,
    ) -> TransactionFeatureBaseline:

        self._require_fitted()

        return self.baseline

    # =========================================================
    # SOURCE NORMALIZATION
    # =========================================================

    def _normalize_transaction(
        self,
        transaction: dict[
            str,
            Any,
        ],
    ) -> dict[str, Any]:

        transaction_id = (
            transaction.get(
                "transaction_id"
            )
        )

        if not transaction_id:
            raise ValueError(
                "transaction_id is required"
            )

        account_id = (
            transaction.get(
                "account_id"
            )
        )

        if not account_id:
            raise ValueError(
                "account_id is required for "
                f"{transaction_id}"
            )

        customer_id = (
            transaction.get(
                "customer_id"
            )
        )

        if not customer_id:
            raise ValueError(
                "customer_id is required for "
                f"{transaction_id}"
            )

        timestamp = (
            self._to_datetime(
                transaction.get(
                    "transaction_timestamp"
                )
            )
        )

        amount = (
            self._to_decimal(
                transaction.get(
                    "amount"
                ),
                "amount",
            )
        )

        direction = str(
            transaction.get(
                "direction",
                "",
            )
        ).strip().upper()

        if direction not in {
            "DEBIT",
            "CREDIT",
        }:

            raise ValueError(
                "direction must be DEBIT or CREDIT "
                f"for {transaction_id}"
            )

        transaction_type = str(
            transaction.get(
                "transaction_type",
                "",
            )
        ).strip().upper()

        if not transaction_type:
            raise ValueError(
                "transaction_type is required "
                f"for {transaction_id}"
            )

        currency = str(
            transaction.get(
                "currency",
                "INR",
            )
        ).strip().upper()

        counterparty_name = (
            self._optional_string(
                transaction.get(
                    "counterparty_name"
                )
            )
        )

        country = (
            self._optional_string(
                transaction.get(
                    "country"
                )
            )
        )

        balance_value = (
            transaction.get(
                "balance_after_transaction"
            )
        )

        if balance_value is None:

            balance_after_transaction = (
                None
            )

        else:

            balance_after_transaction = (
                self._to_decimal(
                    balance_value,
                    "balance_after_transaction",
                )
            )

        return {
            "transaction_id": str(
                transaction_id
            ),

            "account_id": str(
                account_id
            ),

            "customer_id": str(
                customer_id
            ),

            "transaction_timestamp": (
                timestamp
            ),

            "direction": (
                direction
            ),

            "transaction_type": (
                transaction_type
            ),

            "amount": (
                amount
            ),

            "absolute_amount": abs(
                amount
            ),

            "currency": (
                currency
            ),

            "counterparty_name": (
                counterparty_name
            ),

            "normalized_counterparty": (
                self._normalize_name(
                    counterparty_name
                )
            ),

            "counterparty_account": (
                self._optional_string(
                    transaction.get(
                        "counterparty_account"
                    )
                )
            ),

            "counterparty_bank": (
                self._optional_string(
                    transaction.get(
                        "counterparty_bank"
                    )
                )
            ),

            "merchant_category": (
                self._optional_string(
                    transaction.get(
                        "merchant_category"
                    )
                )
            ),

            "country": (
                country
            ),

            "normalized_country": (
                self._normalize_name(
                    country
                )
            ),

            "channel": (
                self._optional_string(
                    transaction.get(
                        "channel"
                    )
                )
            ),

            "description": (
                self._optional_string(
                    transaction.get(
                        "description"
                    )
                )
            ),

            "balance_after_transaction": (
                balance_after_transaction
            ),
        }

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _to_decimal(
        value: Any,
        field_name: str,
    ) -> Decimal:

        if value is None:
            raise ValueError(
                f"{field_name} is required"
            )

        try:

            result = Decimal(
                str(value)
            )

        except Exception as exc:

            raise ValueError(
                f"Invalid {field_name}: "
                f"{value}"
            ) from exc

        if not result.is_finite():
            raise ValueError(
                f"{field_name} must be finite"
            )

        return result

    @staticmethod
    def _to_datetime(
        value: Any,
    ) -> datetime:

        if value is None:
            raise ValueError(
                "transaction_timestamp "
                "is required"
            )

        if isinstance(
            value,
            datetime,
        ):
            return value

        if isinstance(
            value,
            date,
        ):

            return datetime.combine(
                value,
                datetime.min.time(),
            )

        if isinstance(
            value,
            str,
        ):

            cleaned = (
                value.strip()
            )

            if not cleaned:
                raise ValueError(
                    "transaction_timestamp "
                    "cannot be empty"
                )

            try:

                return datetime.fromisoformat(
                    cleaned.replace(
                        "Z",
                        "+00:00",
                    )
                )

            except ValueError as exc:

                raise ValueError(
                    "Unsupported timestamp: "
                    f"{value}"
                ) from exc

        raise ValueError(
            "Unsupported timestamp value: "
            f"{value}"
        )

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        cleaned = str(
            value
        ).strip()

        return cleaned or None

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

    @staticmethod
    def _is_round_amount(
        amount: Decimal,
    ) -> bool:

        minimum_amount = Decimal(
            "100000"
        )

        round_multiple = Decimal(
            "100000"
        )

        if amount < minimum_amount:
            return False

        return (
            amount % round_multiple
            == 0
        )

    def _require_fitted(
        self,
    ) -> None:

        if self.baseline is None:
            raise RuntimeError(
                "Feature engineer has not been "
                "fitted. Call fit() first."
            )