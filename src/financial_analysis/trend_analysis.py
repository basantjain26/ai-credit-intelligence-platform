from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import Enum

from src.financial_analysis.ratio_engine import (
    FinancialRatioResult,
    RatioStatus,
)
from src.financial_analysis.reconciliation import (
    ReconciledFinancialMetric,
    ReconciliationStatus,
)


class TrendStatus(str, Enum):
    CALCULATED = "CALCULATED"
    NOT_CALCULABLE = "NOT_CALCULABLE"


class TrendDirection(str, Enum):
    IMPROVING = "IMPROVING"
    DETERIORATING = "DETERIORATING"
    STABLE = "STABLE"
    MIXED = "MIXED"
    NOT_AVAILABLE = "NOT_AVAILABLE"


@dataclass
class TrendPeriodValue:
    fiscal_year: int
    value: Decimal | None


@dataclass
class FinancialTrendResult:
    metric_name: str
    status: TrendStatus

    periods: list[TrendPeriodValue] = field(
        default_factory=list
    )

    latest_year: int | None = None
    previous_year: int | None = None

    latest_value: Decimal | None = None
    previous_value: Decimal | None = None

    absolute_change: Decimal | None = None
    percentage_change: Decimal | None = None

    direction: TrendDirection = (
        TrendDirection.NOT_AVAILABLE
    )

    reason: str | None = None


@dataclass
class FinancialTrendAnalysis:
    metric_trends: list[FinancialTrendResult] = field(
        default_factory=list
    )

    ratio_trends: list[FinancialTrendResult] = field(
        default_factory=list
    )

    overall_direction: TrendDirection = (
        TrendDirection.NOT_AVAILABLE
    )


class HistoricalTrendAnalyzer:
    """
    Deterministic historical financial trend analyzer.

    Responsibilities:
    - compare financial metrics across fiscal years
    - calculate year-over-year changes
    - calculate ratio movement
    - classify direction using explicit deterministic rules
    - summarize the overall financial trajectory

    This layer does NOT:
    - use an LLM
    - invent missing financial values
    - resolve conflicting source values
    - apply lending policy thresholds
    """

    GROWTH_METRICS = {
        "revenue",
        "ebitda",
        "net_income",
        "operating_cash_flow",
    }

    LOWER_IS_BETTER_METRICS = {
        "total_debt",
    }

    HIGHER_IS_BETTER_RATIOS = {
        "ebitda_margin",
        "net_profit_margin",
        "current_ratio",
        "interest_coverage",
        "dscr",
        "operating_cash_flow_to_debt",
    }

    LOWER_IS_BETTER_RATIOS = {
        "debt_to_ebitda",
        "debt_to_equity",
    }

    def analyze(
        self,
        metrics: list[ReconciledFinancialMetric],
        ratios: list[FinancialRatioResult],
    ) -> FinancialTrendAnalysis:

        metric_trends = (
            self.analyze_metrics(
                metrics
            )
        )

        ratio_trends = (
            self.analyze_ratios(
                ratios
            )
        )

        overall_direction = (
            self._calculate_overall_direction(
                metric_trends=metric_trends,
                ratio_trends=ratio_trends,
            )
        )

        return FinancialTrendAnalysis(
            metric_trends=metric_trends,
            ratio_trends=ratio_trends,
            overall_direction=overall_direction,
        )

    def analyze_metrics(
        self,
        metrics: list[ReconciledFinancialMetric],
    ) -> list[FinancialTrendResult]:

        metric_names = sorted(
            self.GROWTH_METRICS
            | self.LOWER_IS_BETTER_METRICS
        )

        results = []

        for metric_name in metric_names:

            metric_values = [
                metric
                for metric in metrics
                if metric.canonical_name
                == metric_name
            ]

            result = (
                self._analyze_reconciled_metric(
                    metric_name=metric_name,
                    metrics=metric_values,
                )
            )

            results.append(result)

        return results

    def analyze_ratios(
        self,
        ratios: list[FinancialRatioResult],
    ) -> list[FinancialTrendResult]:

        ratio_names = sorted(
            self.HIGHER_IS_BETTER_RATIOS
            | self.LOWER_IS_BETTER_RATIOS
        )

        results = []

        for ratio_name in ratio_names:

            ratio_values = [
                ratio
                for ratio in ratios
                if ratio.ratio_name
                == ratio_name
            ]

            result = (
                self._analyze_ratio(
                    ratio_name=ratio_name,
                    ratios=ratio_values,
                )
            )

            results.append(result)

        return results

    def _analyze_reconciled_metric(
        self,
        metric_name: str,
        metrics: list[ReconciledFinancialMetric],
    ) -> FinancialTrendResult:

        usable_metrics = [
            metric
            for metric in metrics
            if (
                metric.fiscal_year is not None
                and metric.resolved_value is not None
                and metric.status
                in {
                    ReconciliationStatus.UNIQUE,
                    ReconciliationStatus.MATCH,
                }
            )
        ]

        usable_metrics.sort(
            key=lambda item: item.fiscal_year,
            reverse=True,
        )

        periods = [
            TrendPeriodValue(
                fiscal_year=metric.fiscal_year,
                value=metric.resolved_value,
            )
            for metric in usable_metrics
        ]

        if len(usable_metrics) < 2:

            return FinancialTrendResult(
                metric_name=metric_name,
                status=(
                    TrendStatus.NOT_CALCULABLE
                ),
                periods=periods,
                direction=(
                    TrendDirection.NOT_AVAILABLE
                ),
                reason=(
                    "At least two usable fiscal "
                    "periods are required"
                ),
            )

        latest = usable_metrics[0]
        previous = usable_metrics[1]

        return self._build_trend_result(
            metric_name=metric_name,
            latest_year=latest.fiscal_year,
            latest_value=latest.resolved_value,
            previous_year=previous.fiscal_year,
            previous_value=previous.resolved_value,
            periods=periods,
            lower_is_better=(
                metric_name
                in self.LOWER_IS_BETTER_METRICS
            ),
        )

    def _analyze_ratio(
        self,
        ratio_name: str,
        ratios: list[FinancialRatioResult],
    ) -> FinancialTrendResult:

        usable_ratios = [
            ratio
            for ratio in ratios
            if (
                ratio.fiscal_year is not None
                and ratio.value is not None
                and ratio.status
                == RatioStatus.CALCULATED
            )
        ]

        usable_ratios.sort(
            key=lambda item: item.fiscal_year,
            reverse=True,
        )

        periods = [
            TrendPeriodValue(
                fiscal_year=ratio.fiscal_year,
                value=ratio.value,
            )
            for ratio in usable_ratios
        ]

        if len(usable_ratios) < 2:

            return FinancialTrendResult(
                metric_name=ratio_name,
                status=(
                    TrendStatus.NOT_CALCULABLE
                ),
                periods=periods,
                direction=(
                    TrendDirection.NOT_AVAILABLE
                ),
                reason=(
                    "At least two calculated fiscal "
                    "periods are required"
                ),
            )

        latest = usable_ratios[0]
        previous = usable_ratios[1]

        return self._build_trend_result(
            metric_name=ratio_name,
            latest_year=latest.fiscal_year,
            latest_value=latest.value,
            previous_year=previous.fiscal_year,
            previous_value=previous.value,
            periods=periods,
            lower_is_better=(
                ratio_name
                in self.LOWER_IS_BETTER_RATIOS
            ),
        )

    def _build_trend_result(
        self,
        metric_name: str,
        latest_year: int,
        latest_value: Decimal,
        previous_year: int,
        previous_value: Decimal,
        periods: list[TrendPeriodValue],
        lower_is_better: bool,
    ) -> FinancialTrendResult:

        absolute_change = (
            latest_value
            - previous_value
        )

        percentage_change = None

        if previous_value != Decimal("0"):
            percentage_change = (
                absolute_change
                / abs(previous_value)
                * Decimal("100")
            )

            percentage_change = self._round(
                percentage_change
            )

        direction = self._classify_direction(
            absolute_change=absolute_change,
            lower_is_better=lower_is_better,
        )

        return FinancialTrendResult(
            metric_name=metric_name,
            status=TrendStatus.CALCULATED,
            periods=periods,
            latest_year=latest_year,
            previous_year=previous_year,
            latest_value=latest_value,
            previous_value=previous_value,
            absolute_change=self._round(
                absolute_change
            ),
            percentage_change=(
                percentage_change
            ),
            direction=direction,
        )

    @staticmethod
    def _classify_direction(
        absolute_change: Decimal,
        lower_is_better: bool,
    ) -> TrendDirection:

        if absolute_change == Decimal("0"):
            return TrendDirection.STABLE

        if lower_is_better:

            if absolute_change < 0:
                return (
                    TrendDirection.IMPROVING
                )

            return (
                TrendDirection.DETERIORATING
            )

        if absolute_change > 0:
            return TrendDirection.IMPROVING

        return TrendDirection.DETERIORATING

    def _calculate_overall_direction(
        self,
        metric_trends: list[
            FinancialTrendResult
        ],
        ratio_trends: list[
            FinancialTrendResult
        ],
    ) -> TrendDirection:

        trends = (
            metric_trends
            + ratio_trends
        )

        calculated = [
            trend
            for trend in trends
            if trend.status
            == TrendStatus.CALCULATED
        ]

        if not calculated:
            return (
                TrendDirection.NOT_AVAILABLE
            )

        improving = sum(
            1
            for trend in calculated
            if trend.direction
            == TrendDirection.IMPROVING
        )

        deteriorating = sum(
            1
            for trend in calculated
            if trend.direction
            == TrendDirection.DETERIORATING
        )

        if (
            improving > 0
            and deteriorating > 0
        ):
            return TrendDirection.MIXED

        if improving > 0:
            return TrendDirection.IMPROVING

        if deteriorating > 0:
            return (
                TrendDirection.DETERIORATING
            )

        return TrendDirection.STABLE

    @staticmethod
    def _round(
        value: Decimal,
        places: int = 4,
    ) -> Decimal:

        try:
            quantizer = Decimal(
                "1"
            ).scaleb(
                -places
            )

            return value.quantize(
                quantizer
            )

        except InvalidOperation:
            return value