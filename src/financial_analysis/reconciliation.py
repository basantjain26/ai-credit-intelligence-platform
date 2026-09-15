from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Iterable

from src.financial_analysis.metric_mapping import (
    CanonicalFinancialMetric,
)


class ReconciliationStatus(str, Enum):
    UNIQUE = "UNIQUE"
    MATCH = "MATCH"
    CONFLICT = "CONFLICT"
    MISSING_VALUE = "MISSING_VALUE"


@dataclass
class FinancialMetricObservation:
    """
    One financial metric observation coming from one source.

    Example:
        revenue = 790,000,000
        source = STRUCTURED_FINANCIAL_STATEMENT
        fiscal_year = 2026
    """

    canonical_name: str
    value: Decimal | None
    source_type: str

    fiscal_year: int | None = None
    raw_name: str | None = None
    raw_value: object | None = None

    source_id: str | None = None
    document_id: str | None = None
    document_name: str | None = None
    page_number: int | None = None

    unit: str | None = None
    currency: str | None = None


@dataclass
class ReconciledFinancialMetric:
    """
    Result of reconciling all observations for the same
    canonical metric and fiscal year.
    """

    canonical_name: str
    fiscal_year: int | None
    status: ReconciliationStatus

    observations: list[FinancialMetricObservation] = field(
        default_factory=list
    )

    distinct_values: list[Decimal] = field(
        default_factory=list
    )

    resolved_value: Decimal | None = None

    conflict_difference: Decimal | None = None
    conflict_difference_pct: Decimal | None = None


class FinancialValueReconciler:
    """
    Reconciles canonical financial observations across sources.

    Responsibilities:
    - group observations by metric and fiscal year
    - identify duplicate/equivalent values
    - identify genuine conflicts
    - preserve source provenance
    - avoid silently choosing conflicting values

    This layer does NOT:
    - decide which source is authoritative
    - calculate ratios
    - perform LLM reasoning
    - overwrite source observations
    """

    def reconcile(
        self,
        observations: Iterable[
            FinancialMetricObservation
        ],
    ) -> list[ReconciledFinancialMetric]:

        grouped: dict[
            tuple[str, int | None],
            list[FinancialMetricObservation],
        ] = {}

        for observation in observations:

            key = (
                observation.canonical_name,
                observation.fiscal_year,
            )

            grouped.setdefault(
                key,
                [],
            ).append(
                observation
            )

        results = []

        for (
            canonical_name,
            fiscal_year,
        ), metric_observations in grouped.items():

            result = self._reconcile_group(
                canonical_name=canonical_name,
                fiscal_year=fiscal_year,
                observations=metric_observations,
            )

            results.append(
                result
            )

        return sorted(
            results,
            key=lambda item: (
                item.fiscal_year
                if item.fiscal_year is not None
                else -1,
                item.canonical_name,
            ),
            reverse=True,
        )

    def reconcile_canonical_metrics(
        self,
        metrics: Iterable[
            CanonicalFinancialMetric
        ],
    ) -> list[ReconciledFinancialMetric]:
        """
        Convenience method for converting the output of
        CanonicalMetricMapper into reconciliation observations.
        """

        observations = []

        for metric in metrics:

            observations.append(
                FinancialMetricObservation(
                    canonical_name=(
                        metric.canonical_name
                    ),
                    value=metric.value,
                    source_type=metric.source_type,
                    fiscal_year=metric.fiscal_year,
                    raw_name=metric.raw_name,
                    raw_value=metric.raw_value,
                    unit=metric.unit,
                    currency=metric.currency,
                )
            )

        return self.reconcile(
            observations
        )

    def _reconcile_group(
        self,
        canonical_name: str,
        fiscal_year: int | None,
        observations: list[
            FinancialMetricObservation
        ],
    ) -> ReconciledFinancialMetric:

        available_values = [
            observation.value
            for observation in observations
            if observation.value is not None
        ]

        if not available_values:
            return ReconciledFinancialMetric(
                canonical_name=canonical_name,
                fiscal_year=fiscal_year,
                status=(
                    ReconciliationStatus
                    .MISSING_VALUE
                ),
                observations=observations,
                distinct_values=[],
                resolved_value=None,
            )

        distinct_values = sorted(
            set(
                available_values
            )
        )

        if len(observations) == 1:

            return ReconciledFinancialMetric(
                canonical_name=canonical_name,
                fiscal_year=fiscal_year,
                status=(
                    ReconciliationStatus
                    .UNIQUE
                ),
                observations=observations,
                distinct_values=distinct_values,
                resolved_value=(
                    distinct_values[0]
                ),
            )

        if len(distinct_values) == 1:

            return ReconciledFinancialMetric(
                canonical_name=canonical_name,
                fiscal_year=fiscal_year,
                status=(
                    ReconciliationStatus
                    .MATCH
                ),
                observations=observations,
                distinct_values=distinct_values,
                resolved_value=(
                    distinct_values[0]
                ),
            )

        difference = self._calculate_range(
            distinct_values
        )

        difference_pct = (
            self._calculate_difference_pct(
                distinct_values
            )
        )

        return ReconciledFinancialMetric(
            canonical_name=canonical_name,
            fiscal_year=fiscal_year,
            status=(
                ReconciliationStatus
                .CONFLICT
            ),
            observations=observations,
            distinct_values=distinct_values,
            resolved_value=None,
            conflict_difference=difference,
            conflict_difference_pct=(
                difference_pct
            ),
        )

    @staticmethod
    def _calculate_range(
        values: list[Decimal],
    ) -> Decimal | None:

        if len(values) < 2:
            return None

        return max(values) - min(values)

    @staticmethod
    def _calculate_difference_pct(
        values: list[Decimal],
    ) -> Decimal | None:
        """
        Measures conflict magnitude relative to the smallest
        absolute non-zero observed value.

        Example:
            790M vs 850M

            difference = 60M
            percentage = 60 / 790 * 100
                       ≈ 7.59%
        """

        if len(values) < 2:
            return None

        difference = (
            max(values)
            - min(values)
        )

        non_zero_values = [
            abs(value)
            for value in values
            if value != Decimal("0")
        ]

        if not non_zero_values:
            return None

        baseline = min(
            non_zero_values
        )

        return (
            difference
            / baseline
            * Decimal("100")
        )