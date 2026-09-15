from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from src.financial_analysis.ratio_engine import (
    FinancialRatioResult,
    RatioStatus,
)
from src.financial_analysis.trend_analysis import (
    FinancialTrendAnalysis,
    FinancialTrendResult,
    TrendStatus,
)


class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SignalCategory(str, Enum):
    REVENUE = "REVENUE"
    PROFITABILITY = "PROFITABILITY"
    LEVERAGE = "LEVERAGE"
    LIQUIDITY = "LIQUIDITY"
    CASH_FLOW = "CASH_FLOW"
    DEBT_SERVICE = "DEBT_SERVICE"


@dataclass(frozen=True)
class FinancialRiskThresholds:
    """
    General financial-risk heuristics.

    These are NOT lending-policy rules.

    Policy-specific thresholds belong to the Policy Compliance
    Agent later in the project.
    """

    revenue_decline_medium_pct: Decimal = Decimal("-5")
    revenue_decline_high_pct: Decimal = Decimal("-15")

    ebitda_decline_medium_pct: Decimal = Decimal("-10")
    ebitda_decline_high_pct: Decimal = Decimal("-20")

    net_income_decline_medium_pct: Decimal = Decimal("-10")
    net_income_decline_high_pct: Decimal = Decimal("-25")

    debt_growth_medium_pct: Decimal = Decimal("10")
    debt_growth_high_pct: Decimal = Decimal("25")

    cash_flow_decline_medium_pct: Decimal = Decimal("-10")
    cash_flow_decline_high_pct: Decimal = Decimal("-20")

    debt_to_ebitda_medium: Decimal = Decimal("3")
    debt_to_ebitda_high: Decimal = Decimal("4")

    current_ratio_medium: Decimal = Decimal("1.25")
    current_ratio_high: Decimal = Decimal("1")

    interest_coverage_medium: Decimal = Decimal("2")
    interest_coverage_high: Decimal = Decimal("1.5")

    dscr_medium: Decimal = Decimal("1.25")
    dscr_high: Decimal = Decimal("1")


@dataclass
class FinancialRiskSignal:
    signal_code: str
    category: SignalCategory
    severity: RiskSeverity

    title: str
    description: str

    metric_name: str

    fiscal_year: int | None = None

    observed_value: Decimal | None = None
    threshold_value: Decimal | None = None
    unit: str | None = None

    source_type: str | None = None

    metadata: dict = field(
        default_factory=dict
    )


@dataclass
class FinancialRiskAssessment:
    signals: list[FinancialRiskSignal] = field(
        default_factory=list
    )

    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0


class FinancialRiskSignalEngine:
    """
    Converts deterministic financial ratios and historical trends
    into deterministic financial risk signals.

    This engine does NOT:
    - use an LLM
    - approve/reject credit
    - calculate probability of default
    - enforce lending policy
    - invent missing values

    It converts already-calculated financial facts into explicit
    risk indicators using transparent rules.
    """

    def __init__(
        self,
        thresholds: FinancialRiskThresholds | None = None,
    ):
        self.thresholds = (
            thresholds
            or FinancialRiskThresholds()
        )

    def evaluate(
        self,
        trend_analysis: FinancialTrendAnalysis,
        ratios: list[FinancialRatioResult],
    ) -> FinancialRiskAssessment:

        signals: list[FinancialRiskSignal] = []

        signals.extend(
            self._evaluate_trends(
                trend_analysis
            )
        )

        signals.extend(
            self._evaluate_latest_ratios(
                ratios
            )
        )

        return FinancialRiskAssessment(
            signals=signals,
            high_count=sum(
                1
                for signal in signals
                if signal.severity
                == RiskSeverity.HIGH
            ),
            medium_count=sum(
                1
                for signal in signals
                if signal.severity
                == RiskSeverity.MEDIUM
            ),
            low_count=sum(
                1
                for signal in signals
                if signal.severity
                == RiskSeverity.LOW
            ),
        )

    def _evaluate_trends(
        self,
        analysis: FinancialTrendAnalysis,
    ) -> list[FinancialRiskSignal]:

        trends = {
            trend.metric_name: trend
            for trend in analysis.metric_trends
        }

        signals: list[FinancialRiskSignal] = []

        revenue = trends.get("revenue")

        if self._has_percentage_change(revenue):
            signal = self._decline_signal(
                trend=revenue,
                signal_code="REVENUE_DECLINE",
                category=SignalCategory.REVENUE,
                title="Revenue decline",
                medium_threshold=(
                    self.thresholds
                    .revenue_decline_medium_pct
                ),
                high_threshold=(
                    self.thresholds
                    .revenue_decline_high_pct
                ),
            )

            if signal:
                signals.append(signal)

        ebitda = trends.get("ebitda")

        if self._has_percentage_change(ebitda):
            signal = self._decline_signal(
                trend=ebitda,
                signal_code="EBITDA_DECLINE",
                category=(
                    SignalCategory.PROFITABILITY
                ),
                title="EBITDA deterioration",
                medium_threshold=(
                    self.thresholds
                    .ebitda_decline_medium_pct
                ),
                high_threshold=(
                    self.thresholds
                    .ebitda_decline_high_pct
                ),
            )

            if signal:
                signals.append(signal)

        net_income = trends.get("net_income")

        if self._has_percentage_change(
            net_income
        ):
            signal = self._decline_signal(
                trend=net_income,
                signal_code=(
                    "NET_INCOME_DECLINE"
                ),
                category=(
                    SignalCategory.PROFITABILITY
                ),
                title="Net income deterioration",
                medium_threshold=(
                    self.thresholds
                    .net_income_decline_medium_pct
                ),
                high_threshold=(
                    self.thresholds
                    .net_income_decline_high_pct
                ),
            )

            if signal:
                signals.append(signal)

        debt = trends.get("total_debt")

        if self._has_percentage_change(debt):
            signal = self._increase_signal(
                trend=debt,
                signal_code="RISING_DEBT",
                category=SignalCategory.LEVERAGE,
                title="Increasing debt",
                medium_threshold=(
                    self.thresholds
                    .debt_growth_medium_pct
                ),
                high_threshold=(
                    self.thresholds
                    .debt_growth_high_pct
                ),
            )

            if signal:
                signals.append(signal)

        cash_flow = trends.get(
            "operating_cash_flow"
        )

        if self._has_percentage_change(
            cash_flow
        ):
            signal = self._decline_signal(
                trend=cash_flow,
                signal_code=(
                    "OPERATING_CASH_FLOW_DECLINE"
                ),
                category=SignalCategory.CASH_FLOW,
                title=(
                    "Operating cash flow deterioration"
                ),
                medium_threshold=(
                    self.thresholds
                    .cash_flow_decline_medium_pct
                ),
                high_threshold=(
                    self.thresholds
                    .cash_flow_decline_high_pct
                ),
            )

            if signal:
                signals.append(signal)

        return signals

    def _evaluate_latest_ratios(
        self,
        ratios: list[FinancialRatioResult],
    ) -> list[FinancialRiskSignal]:

        latest = self._latest_ratios(
            ratios
        )

        signals: list[FinancialRiskSignal] = []

        debt_to_ebitda = latest.get(
            "debt_to_ebitda"
        )

        if self._usable_ratio(
            debt_to_ebitda
        ):
            signal = self._high_value_ratio_signal(
                ratio=debt_to_ebitda,
                signal_code="HIGH_DEBT_TO_EBITDA",
                category=SignalCategory.LEVERAGE,
                title="Elevated leverage",
                medium_threshold=(
                    self.thresholds
                    .debt_to_ebitda_medium
                ),
                high_threshold=(
                    self.thresholds
                    .debt_to_ebitda_high
                ),
            )

            if signal:
                signals.append(signal)

        current_ratio = latest.get(
            "current_ratio"
        )

        if self._usable_ratio(
            current_ratio
        ):
            signal = self._low_value_ratio_signal(
                ratio=current_ratio,
                signal_code="WEAK_CURRENT_RATIO",
                category=SignalCategory.LIQUIDITY,
                title="Weak liquidity",
                medium_threshold=(
                    self.thresholds
                    .current_ratio_medium
                ),
                high_threshold=(
                    self.thresholds
                    .current_ratio_high
                ),
            )

            if signal:
                signals.append(signal)

        interest_coverage = latest.get(
            "interest_coverage"
        )

        if self._usable_ratio(
            interest_coverage
        ):
            signal = self._low_value_ratio_signal(
                ratio=interest_coverage,
                signal_code=(
                    "WEAK_INTEREST_COVERAGE"
                ),
                category=(
                    SignalCategory.DEBT_SERVICE
                ),
                title="Weak interest coverage",
                medium_threshold=(
                    self.thresholds
                    .interest_coverage_medium
                ),
                high_threshold=(
                    self.thresholds
                    .interest_coverage_high
                ),
            )

            if signal:
                signals.append(signal)

        dscr = latest.get("dscr")

        if self._usable_ratio(dscr):
            signal = self._low_value_ratio_signal(
                ratio=dscr,
                signal_code="WEAK_DSCR",
                category=(
                    SignalCategory.DEBT_SERVICE
                ),
                title=(
                    "Weak debt service capacity"
                ),
                medium_threshold=(
                    self.thresholds.dscr_medium
                ),
                high_threshold=(
                    self.thresholds.dscr_high
                ),
            )

            if signal:
                signals.append(signal)

        return signals

    def _decline_signal(
        self,
        trend: FinancialTrendResult,
        signal_code: str,
        category: SignalCategory,
        title: str,
        medium_threshold: Decimal,
        high_threshold: Decimal,
    ) -> FinancialRiskSignal | None:

        change = trend.percentage_change

        if change is None:
            return None

        if change <= high_threshold:
            severity = RiskSeverity.HIGH
            threshold = high_threshold

        elif change <= medium_threshold:
            severity = RiskSeverity.MEDIUM
            threshold = medium_threshold

        else:
            return None

        return FinancialRiskSignal(
            signal_code=signal_code,
            category=category,
            severity=severity,
            title=title,
            description=(
                f"{trend.metric_name} changed "
                f"{change}% from FY"
                f"{trend.previous_year} to FY"
                f"{trend.latest_year}."
            ),
            metric_name=trend.metric_name,
            fiscal_year=trend.latest_year,
            observed_value=change,
            threshold_value=threshold,
            unit="PERCENT",
            source_type="HISTORICAL_TREND",
            metadata={
                "previous_year": (
                    trend.previous_year
                ),
                "previous_value": (
                    trend.previous_value
                ),
                "latest_value": (
                    trend.latest_value
                ),
            },
        )

    def _increase_signal(
        self,
        trend: FinancialTrendResult,
        signal_code: str,
        category: SignalCategory,
        title: str,
        medium_threshold: Decimal,
        high_threshold: Decimal,
    ) -> FinancialRiskSignal | None:

        change = trend.percentage_change

        if change is None:
            return None

        if change >= high_threshold:
            severity = RiskSeverity.HIGH
            threshold = high_threshold

        elif change >= medium_threshold:
            severity = RiskSeverity.MEDIUM
            threshold = medium_threshold

        else:
            return None

        return FinancialRiskSignal(
            signal_code=signal_code,
            category=category,
            severity=severity,
            title=title,
            description=(
                f"{trend.metric_name} increased "
                f"{change}% from FY"
                f"{trend.previous_year} to FY"
                f"{trend.latest_year}."
            ),
            metric_name=trend.metric_name,
            fiscal_year=trend.latest_year,
            observed_value=change,
            threshold_value=threshold,
            unit="PERCENT",
            source_type="HISTORICAL_TREND",
            metadata={
                "previous_year": (
                    trend.previous_year
                ),
                "previous_value": (
                    trend.previous_value
                ),
                "latest_value": (
                    trend.latest_value
                ),
            },
        )

    def _high_value_ratio_signal(
        self,
        ratio: FinancialRatioResult,
        signal_code: str,
        category: SignalCategory,
        title: str,
        medium_threshold: Decimal,
        high_threshold: Decimal,
    ) -> FinancialRiskSignal | None:

        value = ratio.value

        if value is None:
            return None

        if value >= high_threshold:
            severity = RiskSeverity.HIGH
            threshold = high_threshold

        elif value >= medium_threshold:
            severity = RiskSeverity.MEDIUM
            threshold = medium_threshold

        else:
            return None

        return self._build_ratio_signal(
            ratio=ratio,
            signal_code=signal_code,
            category=category,
            severity=severity,
            title=title,
            threshold=threshold,
        )

    def _low_value_ratio_signal(
        self,
        ratio: FinancialRatioResult,
        signal_code: str,
        category: SignalCategory,
        title: str,
        medium_threshold: Decimal,
        high_threshold: Decimal,
    ) -> FinancialRiskSignal | None:

        value = ratio.value

        if value is None:
            return None

        if value < high_threshold:
            severity = RiskSeverity.HIGH
            threshold = high_threshold

        elif value < medium_threshold:
            severity = RiskSeverity.MEDIUM
            threshold = medium_threshold

        else:
            return None

        return self._build_ratio_signal(
            ratio=ratio,
            signal_code=signal_code,
            category=category,
            severity=severity,
            title=title,
            threshold=threshold,
        )

    @staticmethod
    def _build_ratio_signal(
        ratio: FinancialRatioResult,
        signal_code: str,
        category: SignalCategory,
        severity: RiskSeverity,
        title: str,
        threshold: Decimal,
    ) -> FinancialRiskSignal:

        return FinancialRiskSignal(
            signal_code=signal_code,
            category=category,
            severity=severity,
            title=title,
            description=(
                f"{ratio.ratio_name} is "
                f"{ratio.value} for FY"
                f"{ratio.fiscal_year}."
            ),
            metric_name=ratio.ratio_name,
            fiscal_year=ratio.fiscal_year,
            observed_value=ratio.value,
            threshold_value=threshold,
            unit=ratio.unit,
            source_type="FINANCIAL_RATIO",
            metadata={
                "formula": ratio.formula,
            },
        )

    @staticmethod
    def _has_percentage_change(
        trend: FinancialTrendResult | None,
    ) -> bool:

        return bool(
            trend
            and trend.status
            == TrendStatus.CALCULATED
            and trend.percentage_change
            is not None
        )

    @staticmethod
    def _usable_ratio(
        ratio: FinancialRatioResult | None,
    ) -> bool:

        return bool(
            ratio
            and ratio.status
            == RatioStatus.CALCULATED
            and ratio.value is not None
        )

    @staticmethod
    def _latest_ratios(
        ratios: list[FinancialRatioResult],
    ) -> dict[str, FinancialRatioResult]:

        latest: dict[
            str,
            FinancialRatioResult,
        ] = {}

        for ratio in ratios:

            if ratio.fiscal_year is None:
                continue

            existing = latest.get(
                ratio.ratio_name
            )

            if (
                existing is None
                or existing.fiscal_year is None
                or ratio.fiscal_year
                > existing.fiscal_year
            ):
                latest[
                    ratio.ratio_name
                ] = ratio

        return latest