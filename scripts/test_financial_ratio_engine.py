from decimal import Decimal

from src.financial_analysis.ratio_engine import (
    FinancialRatioEngine,
)
from src.financial_analysis.reconciliation import (
    FinancialMetricObservation,
    FinancialValueReconciler,
)


def main():

    observations = [
        FinancialMetricObservation(
            canonical_name="revenue",
            value=Decimal(
                "790000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name="ebitda",
            value=Decimal(
                "95000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name="net_income",
            value=Decimal(
                "39000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name="total_debt",
            value=Decimal(
                "125000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name=(
                "operating_cash_flow"
            ),
            value=Decimal(
                "57000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name="equity",
            value=Decimal(
                "210000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name=(
                "current_assets"
            ),
            value=Decimal(
                "290000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name=(
                "current_liabilities"
            ),
            value=Decimal(
                "180000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name="ebit",
            value=Decimal(
                "78000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name=(
                "interest_expense"
            ),
            value=Decimal(
                "18000000"
            ),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
        ),
        FinancialMetricObservation(
            canonical_name=(
                "debt_service"
            ),
            value=Decimal(
                "50000000"
            ),
            source_type=(
                "DEBT_SERVICE_SCHEDULE"
            ),
            fiscal_year=2026,
        ),
    ]

    reconciler = (
        FinancialValueReconciler()
    )

    reconciled_metrics = (
        reconciler.reconcile(
            observations
        )
    )

    ratio_engine = (
        FinancialRatioEngine()
    )

    results = (
        ratio_engine.calculate_all(
            reconciled_metrics
        )
    )

    print(
        "\n========== "
        "FINANCIAL RATIOS "
        "==========\n"
    )

    for result in results:

        print(
            f"Ratio: {result.ratio_name}"
        )

        print(
            f"Fiscal Year: "
            f"{result.fiscal_year}"
        )

        print(
            f"Status: "
            f"{result.status.value}"
        )

        print(
            f"Value: "
            f"{result.value}"
        )

        print(
            f"Unit: "
            f"{result.unit}"
        )

        print(
            f"Formula: "
            f"{result.formula}"
        )

        print(
            f"Reason: "
            f"{result.reason}"
        )

        print(
            "Inputs:"
        )

        for ratio_input in (
            result.inputs
        ):
            print(
                "  ",
                ratio_input,
            )

        print(
            "-" * 70
        )


if __name__ == "__main__":
    main()