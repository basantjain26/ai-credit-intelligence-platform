from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any

from src.financial_analysis.reconciliation import (
    ReconciledFinancialMetric,
    ReconciliationStatus,
)


class RatioStatus(str, Enum):
    CALCULATED = "CALCULATED"
    NOT_CALCULABLE = "NOT_CALCULABLE"


@dataclass
class RatioInput:
    metric_name: str
    value: Decimal | None
    fiscal_year: int | None
    source_status: str | None = None


@dataclass
class FinancialRatioResult:
    ratio_name: str
    fiscal_year: int | None
    status: RatioStatus

    value: Decimal | None = None
    unit: str | None = None

    formula: str | None = None
    reason: str | None = None

    inputs: list[RatioInput] = field(
        default_factory=list
    )


class FinancialRatioEngine:
    """
    Deterministic financial ratio calculator.

    The engine never asks an LLM to perform financial arithmetic.

    It only calculates ratios when required inputs are reliable
    enough to use.

    A financial metric is considered usable when reconciliation
    status is:
        UNIQUE
        MATCH

    A metric is not usable when reconciliation status is:
        CONFLICT
        MISSING_VALUE
    """

    USABLE_STATUSES = {
        ReconciliationStatus.UNIQUE,
        ReconciliationStatus.MATCH,
    }

    def calculate_all(
        self,
        metrics: list[ReconciledFinancialMetric],
    ) -> list[FinancialRatioResult]:
        """
        Calculate all supported ratios for all fiscal years
        present in the reconciled metric collection.
        """

        years = sorted(
            {
                metric.fiscal_year
                for metric in metrics
                if metric.fiscal_year is not None
            },
            reverse=True,
        )

        results: list[
            FinancialRatioResult
        ] = []

        for fiscal_year in years:

            year_metrics = {
                metric.canonical_name: metric
                for metric in metrics
                if metric.fiscal_year
                == fiscal_year
            }

            results.extend(
                self.calculate_for_year(
                    year_metrics=year_metrics,
                    fiscal_year=fiscal_year,
                )
            )

        return results

    def calculate_for_year(
        self,
        year_metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> list[FinancialRatioResult]:
        """
        Calculate supported ratios for one fiscal year.
        """

        return [
            self.ebitda_margin(
                year_metrics,
                fiscal_year,
            ),
            self.net_profit_margin(
                year_metrics,
                fiscal_year,
            ),
            self.debt_to_ebitda(
                year_metrics,
                fiscal_year,
            ),
            self.debt_to_equity(
                year_metrics,
                fiscal_year,
            ),
            self.current_ratio(
                year_metrics,
                fiscal_year,
            ),
            self.interest_coverage(
                year_metrics,
                fiscal_year,
            ),
            self.dscr(
                year_metrics,
                fiscal_year,
            ),
            self.operating_cash_flow_to_debt(
                year_metrics,
                fiscal_year,
            ),
        ]

    def ebitda_margin(
        self,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:

        return self._calculate_percentage_ratio(
            ratio_name="ebitda_margin",
            numerator_name="ebitda",
            denominator_name="revenue",
            formula="EBITDA / Revenue × 100",
            metrics=metrics,
            fiscal_year=fiscal_year,
        )

    def net_profit_margin(
        self,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:

        return self._calculate_percentage_ratio(
            ratio_name="net_profit_margin",
            numerator_name="net_income",
            denominator_name="revenue",
            formula="Net Income / Revenue × 100",
            metrics=metrics,
            fiscal_year=fiscal_year,
        )

    def debt_to_ebitda(
        self,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:

        return self._calculate_multiple_ratio(
            ratio_name="debt_to_ebitda",
            numerator_name="total_debt",
            denominator_name="ebitda",
            formula="Total Debt / EBITDA",
            metrics=metrics,
            fiscal_year=fiscal_year,
        )

    def debt_to_equity(
        self,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:

        return self._calculate_multiple_ratio(
            ratio_name="debt_to_equity",
            numerator_name="total_debt",
            denominator_name="equity",
            formula="Total Debt / Equity",
            metrics=metrics,
            fiscal_year=fiscal_year,
        )

    def current_ratio(
        self,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:

        return self._calculate_multiple_ratio(
            ratio_name="current_ratio",
            numerator_name="current_assets",
            denominator_name="current_liabilities",
            formula=(
                "Current Assets / "
                "Current Liabilities"
            ),
            metrics=metrics,
            fiscal_year=fiscal_year,
        )

    def interest_coverage(
        self,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:
        """
        Uses EBIT / Interest Expense.

        If EBIT is unavailable, we intentionally do NOT derive
        EBIT from EBITDA unless that calculation is explicitly
        introduced as a deterministic rule later.
        """

        return self._calculate_multiple_ratio(
            ratio_name="interest_coverage",
            numerator_name="ebit",
            denominator_name="interest_expense",
            formula="EBIT / Interest Expense",
            metrics=metrics,
            fiscal_year=fiscal_year,
        )

    def dscr(
        self,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:
        """
        Simplified DSCR definition for this implementation:

            Operating Cash Flow / Debt Service

        Real lending organizations may use a different contractual
        definition, for example:

            EBITDA / (Principal + Interest)

        or

            CFADS / Debt Service

        That policy should eventually be configurable rather than
        hidden inside the LLM.
        """

        return self._calculate_multiple_ratio(
            ratio_name="dscr",
            numerator_name=(
                "operating_cash_flow"
            ),
            denominator_name=(
                "debt_service"
            ),
            formula=(
                "Operating Cash Flow / "
                "Debt Service"
            ),
            metrics=metrics,
            fiscal_year=fiscal_year,
        )

    def operating_cash_flow_to_debt(
        self,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:

        return self._calculate_percentage_ratio(
            ratio_name=(
                "operating_cash_flow_to_debt"
            ),
            numerator_name=(
                "operating_cash_flow"
            ),
            denominator_name="total_debt",
            formula=(
                "Operating Cash Flow / "
                "Total Debt × 100"
            ),
            metrics=metrics,
            fiscal_year=fiscal_year,
        )

    def _calculate_percentage_ratio(
        self,
        ratio_name: str,
        numerator_name: str,
        denominator_name: str,
        formula: str,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:

        inputs_result = (
            self._resolve_inputs(
                metrics=metrics,
                fiscal_year=fiscal_year,
                required_metrics=[
                    numerator_name,
                    denominator_name,
                ],
            )
        )

        if inputs_result["error"]:

            return FinancialRatioResult(
                ratio_name=ratio_name,
                fiscal_year=fiscal_year,
                status=(
                    RatioStatus
                    .NOT_CALCULABLE
                ),
                formula=formula,
                reason=inputs_result["error"],
                inputs=inputs_result[
                    "inputs"
                ],
                unit="PERCENT",
            )

        numerator = inputs_result[
            "values"
        ][numerator_name]

        denominator = inputs_result[
            "values"
        ][denominator_name]

        if denominator == Decimal("0"):

            return FinancialRatioResult(
                ratio_name=ratio_name,
                fiscal_year=fiscal_year,
                status=(
                    RatioStatus
                    .NOT_CALCULABLE
                ),
                formula=formula,
                reason=(
                    f"{denominator_name} "
                    "is zero"
                ),
                inputs=inputs_result[
                    "inputs"
                ],
                unit="PERCENT",
            )

        value = (
            numerator
            / denominator
            * Decimal("100")
        )

        return FinancialRatioResult(
            ratio_name=ratio_name,
            fiscal_year=fiscal_year,
            status=RatioStatus.CALCULATED,
            value=self._round(
                value
            ),
            unit="PERCENT",
            formula=formula,
            inputs=inputs_result[
                "inputs"
            ],
        )

    def _calculate_multiple_ratio(
        self,
        ratio_name: str,
        numerator_name: str,
        denominator_name: str,
        formula: str,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
    ) -> FinancialRatioResult:

        inputs_result = (
            self._resolve_inputs(
                metrics=metrics,
                fiscal_year=fiscal_year,
                required_metrics=[
                    numerator_name,
                    denominator_name,
                ],
            )
        )

        if inputs_result["error"]:

            return FinancialRatioResult(
                ratio_name=ratio_name,
                fiscal_year=fiscal_year,
                status=(
                    RatioStatus
                    .NOT_CALCULABLE
                ),
                formula=formula,
                reason=inputs_result["error"],
                inputs=inputs_result[
                    "inputs"
                ],
                unit="MULTIPLE",
            )

        numerator = inputs_result[
            "values"
        ][numerator_name]

        denominator = inputs_result[
            "values"
        ][denominator_name]

        if denominator == Decimal("0"):

            return FinancialRatioResult(
                ratio_name=ratio_name,
                fiscal_year=fiscal_year,
                status=(
                    RatioStatus
                    .NOT_CALCULABLE
                ),
                formula=formula,
                reason=(
                    f"{denominator_name} "
                    "is zero"
                ),
                inputs=inputs_result[
                    "inputs"
                ],
                unit="MULTIPLE",
            )

        value = (
            numerator
            / denominator
        )

        return FinancialRatioResult(
            ratio_name=ratio_name,
            fiscal_year=fiscal_year,
            status=RatioStatus.CALCULATED,
            value=self._round(
                value
            ),
            unit="MULTIPLE",
            formula=formula,
            inputs=inputs_result[
                "inputs"
            ],
        )

    def _resolve_inputs(
        self,
        metrics: dict[
            str,
            ReconciledFinancialMetric,
        ],
        fiscal_year: int,
        required_metrics: list[str],
    ) -> dict[str, Any]:

        values: dict[
            str,
            Decimal,
        ] = {}

        inputs: list[
            RatioInput
        ] = []

        errors: list[str] = []

        for metric_name in required_metrics:

            metric = metrics.get(
                metric_name
            )

            if metric is None:

                inputs.append(
                    RatioInput(
                        metric_name=(
                            metric_name
                        ),
                        value=None,
                        fiscal_year=(
                            fiscal_year
                        ),
                        source_status=(
                            "MISSING"
                        ),
                    )
                )

                errors.append(
                    f"{metric_name} "
                    "is missing"
                )

                continue

            inputs.append(
                RatioInput(
                    metric_name=(
                        metric_name
                    ),
                    value=(
                        metric.resolved_value
                    ),
                    fiscal_year=(
                        fiscal_year
                    ),
                    source_status=(
                        metric.status.value
                    ),
                )
            )

            if (
                metric.status
                not in self.USABLE_STATUSES
            ):

                errors.append(
                    f"{metric_name} "
                    "is not usable because "
                    f"reconciliation status "
                    f"is {metric.status.value}"
                )

                continue

            if metric.resolved_value is None:

                errors.append(
                    f"{metric_name} "
                    "has no resolved value"
                )

                continue

            values[
                metric_name
            ] = metric.resolved_value

        error = None

        if errors:
            error = "; ".join(
                errors
            )

        return {
            "values": values,
            "inputs": inputs,
            "error": error,
        }

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