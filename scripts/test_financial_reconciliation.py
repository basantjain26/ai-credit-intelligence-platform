from decimal import Decimal
from pprint import pprint

from src.financial_analysis.reconciliation import (
    FinancialMetricObservation,
    FinancialValueReconciler,
)


def main():

    reconciler = FinancialValueReconciler()

    observations = [
        # -------------------------------------------------
        # Revenue conflict
        # -------------------------------------------------
        FinancialMetricObservation(
            canonical_name="revenue",
            value=Decimal("790000000"),
            source_type=(
                "AUDITED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
            source_id="FS2026",
            document_id="DOC_FIN_2026",
            document_name=(
                "ABC_FY2026_"
                "Audited_Financials.pdf"
            ),
            page_number=3,
            raw_name="Revenue",
            raw_value="790 Mn",
            unit="INR",
            currency="INR",
        ),
        FinancialMetricObservation(
            canonical_name="revenue",
            value=Decimal("850000000"),
            source_type=(
                "LOAN_APPLICATION"
            ),
            fiscal_year=2026,
            source_id="APP001",
            raw_name=(
                "declared_revenue"
            ),
            raw_value=850_000_000,
            currency="INR",
        ),

        # -------------------------------------------------
        # EBITDA match across two sources
        # -------------------------------------------------
        FinancialMetricObservation(
            canonical_name="ebitda",
            value=Decimal("95000000"),
            source_type=(
                "STRUCTURED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
            source_id="FS2026",
            raw_name="ebitda",
            raw_value=95_000_000,
        ),
        FinancialMetricObservation(
            canonical_name="ebitda",
            value=Decimal("95000000"),
            source_type=(
                "AUDITED_FINANCIAL_DOCUMENT"
            ),
            fiscal_year=2026,
            document_id="DOC_FIN_2026",
            page_number=3,
            raw_name="EBITDA",
            raw_value="95 Mn",
        ),

        # -------------------------------------------------
        # Total debt appears once
        # -------------------------------------------------
        FinancialMetricObservation(
            canonical_name="total_debt",
            value=Decimal("125000000"),
            source_type=(
                "STRUCTURED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
            source_id="FS2026",
            raw_name="total_debt",
            raw_value=125_000_000,
        ),

        # -------------------------------------------------
        # Missing value example
        # -------------------------------------------------
        FinancialMetricObservation(
            canonical_name=(
                "interest_expense"
            ),
            value=None,
            source_type=(
                "STRUCTURED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2026,
            source_id="FS2026",
            raw_name=(
                "interest_expense"
            ),
            raw_value=None,
        ),

        # -------------------------------------------------
        # Historical revenue
        # -------------------------------------------------
        FinancialMetricObservation(
            canonical_name="revenue",
            value=Decimal("860000000"),
            source_type=(
                "STRUCTURED_FINANCIAL_STATEMENT"
            ),
            fiscal_year=2025,
            source_id="FS2025",
            raw_name="revenue",
            raw_value=860_000_000,
        ),
    ]

    results = reconciler.reconcile(
        observations
    )

    print(
        "\n========== "
        "FINANCIAL RECONCILIATION "
        "==========\n"
    )

    for result in results:

        print(
            f"Metric: {result.canonical_name}"
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
            f"Resolved Value: "
            f"{result.resolved_value}"
        )

        print(
            f"Distinct Values: "
            f"{result.distinct_values}"
        )

        print(
            f"Conflict Difference: "
            f"{result.conflict_difference}"
        )

        print(
            "Conflict Difference %:",
            (
                result
                .conflict_difference_pct
            ),
        )

        print(
            "\nObservations:"
        )

        for observation in (
            result.observations
        ):
            pprint(
                observation
            )

        print(
            "\n"
            + "-" * 70
            + "\n"
        )


if __name__ == "__main__":
    main()