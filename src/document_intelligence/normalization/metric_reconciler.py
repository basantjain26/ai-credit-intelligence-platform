from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional

from src.document_intelligence.normalization.financial_value import (
    FinancialValueNormalizer,
)
from src.document_intelligence.schemas import (
    FinancialMetric,
)


class ReconciliationStatus(str, Enum):
    UNIQUE = "UNIQUE"
    DUPLICATE_MATCH = "DUPLICATE_MATCH"
    CONFLICT = "CONFLICT"
    UNNORMALIZABLE = "UNNORMALIZABLE"


@dataclass
class MetricObservation:
    metric_name: str
    canonical_metric_name: str

    raw_value: str
    normalized_value: Optional[Decimal]

    raw_unit: Optional[str]
    normalized_unit: Optional[str]

    period: Optional[str]
    page_number: int

    source_text: Optional[str]

    successfully_normalized: bool


@dataclass
class ReconciledMetric:
    canonical_metric_name: str
    period: Optional[str]

    status: ReconciliationStatus

    resolved_value: Optional[Decimal]

    observations: list[MetricObservation]


class FinancialMetricReconciler:

    METRIC_ALIASES = {
        "revenue": "revenue",
        "total revenue": "revenue",
        "net revenue": "revenue",
        "sales": "revenue",
        "net sales": "revenue",

        "ebitda": "ebitda",
        "adjusted ebitda": "ebitda",

        "net income": "net_income",
        "net profit": "net_income",
        "profit after tax": "net_income",
        "pat": "net_income",

        "total debt": "total_debt",
        "debt": "total_debt",
        "borrowings": "total_debt",
        "total borrowings": "total_debt",

        "operating cash flow": "operating_cash_flow",
        "cash flow from operations": "operating_cash_flow",
        "cash flow from operating activities": "operating_cash_flow",
        "net cash from operating activities": "operating_cash_flow",
    }

    def __init__(self):
        self.value_normalizer = (
            FinancialValueNormalizer()
        )

    def reconcile(
        self,
        metrics: list[FinancialMetric],
    ) -> list[ReconciledMetric]:

        grouped_observations: dict[
            tuple[str, Optional[str]],
            list[MetricObservation],
        ] = {}

        for metric in metrics:

            observation = (
                self._build_observation(
                    metric
                )
            )

            group_key = (
                observation.canonical_metric_name,
                self._normalize_period(
                    observation.period
                ),
            )

            grouped_observations.setdefault(
                group_key,
                [],
            ).append(
                observation
            )

        reconciled_metrics = []

        for (
            canonical_metric_name,
            normalized_period,
        ), observations in grouped_observations.items():

            reconciled = (
                self._reconcile_group(
                    canonical_metric_name=(
                        canonical_metric_name
                    ),
                    period=normalized_period,
                    observations=observations,
                )
            )

            reconciled_metrics.append(
                reconciled
            )

        return reconciled_metrics

    def _build_observation(
        self,
        metric: FinancialMetric,
    ) -> MetricObservation:

        canonical_name = (
            self._canonicalize_metric_name(
                metric.metric_name
            )
        )

        normalized = (
            self.value_normalizer.normalize(
                raw_value=metric.value,
                unit=metric.unit,
            )
        )

        return MetricObservation(
            metric_name=metric.metric_name,
            canonical_metric_name=canonical_name,

            raw_value=metric.value,
            normalized_value=(
                normalized.numeric_value
            ),

            raw_unit=metric.unit,
            normalized_unit=(
                normalized.normalized_unit
            ),

            period=metric.period,
            page_number=metric.page_number,

            source_text=metric.source_text,

            successfully_normalized=(
                normalized.successfully_normalized
            ),
        )

    def _reconcile_group(
        self,
        canonical_metric_name: str,
        period: Optional[str],
        observations: list[MetricObservation],
    ) -> ReconciledMetric:

        normalized_observations = [
            observation
            for observation in observations
            if (
                observation.successfully_normalized
                and observation.normalized_value
                is not None
            )
        ]

        # No observation could be normalized.
        if not normalized_observations:

            return ReconciledMetric(
                canonical_metric_name=(
                    canonical_metric_name
                ),
                period=period,
                status=(
                    ReconciliationStatus
                    .UNNORMALIZABLE
                ),
                resolved_value=None,
                observations=observations,
            )

        # Only one observation exists.
        if len(observations) == 1:

            return ReconciledMetric(
                canonical_metric_name=(
                    canonical_metric_name
                ),
                period=period,
                status=(
                    ReconciliationStatus.UNIQUE
                ),
                resolved_value=(
                    normalized_observations[
                        0
                    ].normalized_value
                ),
                observations=observations,
            )

        normalized_values = {
            observation.normalized_value
            for observation
            in normalized_observations
        }

        # Multiple observations normalize
        # to exactly the same value.
        if (
            len(normalized_values) == 1
            and len(normalized_observations)
            == len(observations)
        ):

            resolved_value = next(
                iter(normalized_values)
            )

            return ReconciledMetric(
                canonical_metric_name=(
                    canonical_metric_name
                ),
                period=period,
                status=(
                    ReconciliationStatus
                    .DUPLICATE_MATCH
                ),
                resolved_value=resolved_value,
                observations=observations,
            )

        # Multiple normalized values exist,
        # therefore there is a real conflict.
        if len(normalized_values) > 1:

            return ReconciledMetric(
                canonical_metric_name=(
                    canonical_metric_name
                ),
                period=period,
                status=(
                    ReconciliationStatus.CONFLICT
                ),
                resolved_value=None,
                observations=observations,
            )

        # Some values normalized but others did not.
        return ReconciledMetric(
            canonical_metric_name=(
                canonical_metric_name
            ),
            period=period,
            status=(
                ReconciliationStatus
                .UNNORMALIZABLE
            ),
            resolved_value=None,
            observations=observations,
        )

    def _canonicalize_metric_name(
        self,
        metric_name: str,
    ) -> str:

        normalized_name = (
            metric_name
            .strip()
            .lower()
        )

        normalized_name = " ".join(
            normalized_name.split()
        )

        return self.METRIC_ALIASES.get(
            normalized_name,
            normalized_name.replace(
                " ",
                "_",
            ),
        )

    @staticmethod
    def _normalize_period(
        period: Optional[str],
    ) -> Optional[str]:

        if not period:
            return None

        normalized = (
            period
            .strip()
            .upper()
        )

        normalized = (
            normalized
            .replace(" ", "")
        )

        return normalized