from dataclasses import asdict
from decimal import Decimal
from typing import Any

from src.financial_analysis.metric_mapping import (
    CanonicalMetricMapper,
)
from src.financial_analysis.reconciliation import (
    FinancialMetricObservation,
    FinancialValueReconciler,
)
from src.financial_analysis.repository import (
    FinancialRepository,
)
from src.financial_analysis.ratio_engine import (
    FinancialRatioEngine,
)
from src.financial_analysis.risk_signals import (
    FinancialRiskSignalEngine,
)
from src.financial_analysis.trend_analysis import (
    HistoricalTrendAnalyzer,
)
from src.financial_analysis.retrieval import (
    FinancialDocumentRetriever,
)


class FinancialAnalysisTools:
    """
    Controlled tool layer for the Financial Analysis Agent.

    Responsibilities:
    - retrieve financial case data
    - construct canonical financial observations
    - reconcile financial values
    - calculate deterministic ratios
    - calculate historical trends
    - generate deterministic financial risk signals
    - retrieve supporting financial-document evidence

    The LLM should interact with this layer rather than
    directly querying PostgreSQL or invoking calculation
    engines itself.
    """

    def __init__(
        self,
        customer_id: str,
        application_id: str,
        repository: FinancialRepository | None = None,
        document_retriever: FinancialDocumentRetriever | None = None,
    ):
        if not customer_id:
            raise ValueError(
                "customer_id is required"
            )

        if not application_id:
            raise ValueError(
                "application_id is required"
            )

        self.customer_id = customer_id
        self.application_id = application_id

        self.repository = (
            repository
            or FinancialRepository()
        )

        self.document_retriever = (
            document_retriever
            or FinancialDocumentRetriever()
        )

        self.metric_mapper = (
            CanonicalMetricMapper()
        )

        self.reconciler = (
            FinancialValueReconciler()
        )

        self.ratio_engine = (
            FinancialRatioEngine()
        )

        self.trend_analyzer = (
            HistoricalTrendAnalyzer()
        )

        self.risk_signal_engine = (
            FinancialRiskSignalEngine()
        )

        self._context = None
        self._reconciled_metrics = None
        self._ratios = None
        self._trends = None
        self._risk_assessment = None

    # ---------------------------------------------------------
    # PUBLIC TOOLS
    # ---------------------------------------------------------

    def get_financial_overview(
        self,
    ) -> dict[str, Any]:
        """
        Return the financial case context together with
        reconciled financial metrics.

        Intended agent use:
        Understand what financial information is available
        before requesting deeper calculations.
        """

        context = self._get_context()

        reconciled = (
            self._get_reconciled_metrics()
        )

        return {
            "customer_id": (
                self.customer_id
            ),
            "application_id": (
                self.application_id
            ),
            "customer": self._serialize(
                context.customer
            ),
            "application": self._serialize(
                context.application
            ),
            "financial_statements": self._serialize(
                context.financial_statements
            ),
            "existing_loans": self._serialize(
                context.existing_loans
            ),
            "financial_documents": self._serialize(
                context.financial_documents
            ),
            "reconciled_metrics": self._serialize(
                reconciled
            ),
        }

    def get_financial_ratios(
        self,
    ) -> dict[str, Any]:
        """
        Return deterministic financial ratios.

        The LLM must not recalculate these values itself.
        """

        ratios = self._get_ratios()

        return {
            "customer_id": (
                self.customer_id
            ),
            "application_id": (
                self.application_id
            ),
            "ratios": self._serialize(
                ratios
            ),
        }

    def get_financial_trends(
        self,
    ) -> dict[str, Any]:
        """
        Return deterministic historical financial trends.
        """

        trends = self._get_trends()

        return {
            "customer_id": (
                self.customer_id
            ),
            "application_id": (
                self.application_id
            ),
            "overall_direction": (
                trends.overall_direction.value
            ),
            "metric_trends": self._serialize(
                trends.metric_trends
            ),
            "ratio_trends": self._serialize(
                trends.ratio_trends
            ),
        }

    def get_financial_risk_signals(
        self,
    ) -> dict[str, Any]:
        """
        Return deterministic financial risk signals.

        These are general financial-risk heuristics,
        not lending-policy decisions.
        """

        assessment = (
            self._get_risk_assessment()
        )

        return {
            "customer_id": (
                self.customer_id
            ),
            "application_id": (
                self.application_id
            ),
            "high_count": (
                assessment.high_count
            ),
            "medium_count": (
                assessment.medium_count
            ),
            "low_count": (
                assessment.low_count
            ),
            "signals": self._serialize(
                assessment.signals
            ),
        }

    def search_financial_documents(
        self,
        query: str,
        limit: int = 5,
        fiscal_year: int | None = None,
    ) -> dict[str, Any]:
        """
        Search borrower/application-scoped financial
        documents for supporting evidence.

        customer_id and application_id are intentionally
        NOT accepted from the LLM.

        They are trusted values stored on this tool instance.
        """

        results = (
            self.document_retriever.search(
                query=query,
                customer_id=self.customer_id,
                application_id=self.application_id,
                limit=limit,
                fiscal_year=fiscal_year,
            )
        )

        return {
            "customer_id": (
                self.customer_id
            ),
            "application_id": (
                self.application_id
            ),
            "query": query,
            "result_count": len(
                results
            ),
            "results": self._serialize(
                results
            ),
        }

    # ---------------------------------------------------------
    # INTERNAL PIPELINE
    # ---------------------------------------------------------

    def _get_context(
        self,
    ):
        if self._context is None:

            self._context = (
                self.repository
                .get_analysis_context(
                    customer_id=(
                        self.customer_id
                    ),
                    application_id=(
                        self.application_id
                    ),
                )
            )

        return self._context

    def _get_reconciled_metrics(
        self,
    ):
        if self._reconciled_metrics is None:

            context = self._get_context()

            observations = (
                self._build_observations(
                    context
                )
            )

            self._reconciled_metrics = (
                self.reconciler.reconcile(
                    observations
                )
            )

        return self._reconciled_metrics

    def _get_ratios(
        self,
    ):
        if self._ratios is None:

            reconciled = (
                self._get_reconciled_metrics()
            )

            self._ratios = (
                self.ratio_engine
                .calculate_all(
                    reconciled
                )
            )

        return self._ratios

    def _get_trends(
        self,
    ):
        if self._trends is None:

            reconciled = (
                self._get_reconciled_metrics()
            )

            ratios = (
                self._get_ratios()
            )

            self._trends = (
                self.trend_analyzer.analyze(
                    metrics=reconciled,
                    ratios=ratios,
                )
            )

        return self._trends

    def _get_risk_assessment(
        self,
    ):
        if self._risk_assessment is None:

            trends = (
                self._get_trends()
            )

            ratios = (
                self._get_ratios()
            )

            self._risk_assessment = (
                self.risk_signal_engine
                .evaluate(
                    trend_analysis=trends,
                    ratios=ratios,
                )
            )

        return self._risk_assessment

    # ---------------------------------------------------------
    # FINANCIAL OBSERVATION CONSTRUCTION
    # ---------------------------------------------------------

    def _build_observations(
        self,
        context,
    ) -> list[FinancialMetricObservation]:
        """
        Convert structured financial statement records into
        canonical observations for reconciliation.

        This is the bridge between repository data and the
        deterministic financial calculation pipeline.
        """

        observations: list[
            FinancialMetricObservation
        ] = []

        for statement in (
            context.financial_statements
        ):

            fiscal_year = (
                statement.get(
                    "fiscal_year"
                )
            )

            source_id = (
                statement.get(
                    "financial_statement_id"
                )
                or statement.get("id")
            )

            for (
                raw_name,
                raw_value,
            ) in statement.items():

                if raw_name in {
                    "financial_statement_id",
                    "id",
                    "customer_id",
                    "fiscal_year",
                    "created_at",
                    "updated_at",
                }:
                    continue

                canonical_name = (
                    self.metric_mapper
                    .canonicalize_name(
                        raw_name
                    )
                )

                if canonical_name is None:
                    continue

                value = (
                    self._to_decimal(
                        raw_value
                    )
                )

                observations.append(
                    FinancialMetricObservation(
                        canonical_name=(
                            canonical_name
                        ),
                        value=value,
                        source_type=(
                            "STRUCTURED_FINANCIAL_STATEMENT"
                        ),
                        fiscal_year=(
                            fiscal_year
                        ),
                        raw_name=raw_name,
                        raw_value=raw_value,
                        source_id=(
                            str(source_id)
                            if source_id
                            is not None
                            else None
                        ),
                    )
                )

        self._add_application_observations(
            context=context,
            observations=observations,
        )

        return observations

    def _add_application_observations(
        self,
        context,
        observations: list[
            FinancialMetricObservation
        ],
    ) -> None:
        """
        Add borrower-declared financial values from the loan
        application when they can be mapped safely.

        This is important because reconciliation should expose
        discrepancies such as:

        audited revenue = 790M
        declared revenue = 850M

        rather than hiding the conflict.
        """

        application = context.application

        candidate_fields = {
            "declared_revenue": "revenue",
            "annual_revenue": "revenue",
            "revenue": "revenue",
            "declared_ebitda": "ebitda",
            "ebitda": "ebitda",
            "declared_net_income": (
                "net_income"
            ),
            "net_income": "net_income",
            "declared_total_debt": (
                "total_debt"
            ),
            "total_debt": "total_debt",
        }

        fiscal_year = (
            application.get(
                "financial_year"
            )
            or application.get(
                "fiscal_year"
            )
            or application.get(
                "declared_financial_year"
            )
        )

        # If the application schema does not explicitly
        # contain the financial year, do not invent one.
        if fiscal_year is None:
            return

        for (
            field_name,
            canonical_name,
        ) in candidate_fields.items():

            if field_name not in application:
                continue

            raw_value = application.get(
                field_name
            )

            if raw_value is None:
                continue

            observations.append(
                FinancialMetricObservation(
                    canonical_name=(
                        canonical_name
                    ),
                    value=self._to_decimal(
                        raw_value
                    ),
                    source_type=(
                        "LOAN_APPLICATION"
                    ),
                    fiscal_year=(
                        fiscal_year
                    ),
                    raw_name=(
                        field_name
                    ),
                    raw_value=(
                        raw_value
                    ),
                    source_id=(
                        self.application_id
                    ),
                )
            )

    # ---------------------------------------------------------
    # SERIALIZATION
    # ---------------------------------------------------------

    def _serialize(
        self,
        value: Any,
    ) -> Any:
        """
        Convert internal Python/domain objects into
        JSON-compatible structures suitable for LLM tools.
        """

        if value is None:
            return None

        if isinstance(
            value,
            Decimal,
        ):
            return str(value)

        if hasattr(
            value,
            "value",
        ) and isinstance(
            value.value,
            str,
        ):
            return value.value

        if isinstance(
            value,
            list,
        ):
            return [
                self._serialize(item)
                for item in value
            ]

        if isinstance(
            value,
            tuple,
        ):
            return [
                self._serialize(item)
                for item in value
            ]

        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): (
                    self._serialize(
                        item
                    )
                )
                for key, item
                in value.items()
            }

        if hasattr(
            value,
            "__dataclass_fields__",
        ):
            return self._serialize(
                asdict(value)
            )

        return value

    @staticmethod
    def _to_decimal(
        value: Any,
    ) -> Decimal | None:

        if value is None:
            return None

        if isinstance(
            value,
            Decimal,
        ):
            return value

        try:
            return Decimal(
                str(value)
            )

        except Exception:
            return None

    # ---------------------------------------------------------
    # RESOURCE MANAGEMENT
    # ---------------------------------------------------------

    def close(
        self,
    ) -> None:

        if self.repository:
            self.repository.close()

        if self.document_retriever:
            self.document_retriever.close()

    def __enter__(
        self,
    ):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()