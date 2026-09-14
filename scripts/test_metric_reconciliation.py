from src.document_intelligence.normalization.metric_reconciler import (
    FinancialMetricReconciler,
)
from src.document_intelligence.schemas import (
    FinancialMetric,
)


def main():

    metrics = [
        FinancialMetric(
            metric_name="Revenue",
            value="₹790 Mn",
            unit=None,
            period="FY2026",
            page_number=2,
            source_text="Revenue ₹790 Mn",
        ),

        FinancialMetric(
            metric_name="Total Revenue",
            value="790",
            unit="INR million",
            period="FY 2026",
            page_number=5,
            source_text="Total Revenue 790",
        ),

        FinancialMetric(
            metric_name="EBITDA",
            value="95",
            unit="INR million",
            period="FY2026",
            page_number=2,
            source_text="EBITDA 95",
        ),

        FinancialMetric(
            metric_name="Net Income",
            value="39",
            unit="INR million",
            period="FY2026",
            page_number=2,
            source_text="Net Income 39",
        ),

        FinancialMetric(
            metric_name="Net Profit",
            value="41",
            unit="INR million",
            period="FY2026",
            page_number=6,
            source_text="Net Profit 41",
        ),

        FinancialMetric(
            metric_name="Total Debt",
            value="125",
            unit="INR million",
            period="FY2026",
            page_number=3,
            source_text="Total Debt 125",
        ),
    ]

    reconciler = (
        FinancialMetricReconciler()
    )

    results = reconciler.reconcile(
        metrics
    )

    print(
        "\n========== RECONCILIATION ==========\n"
    )

    for result in results:

        print(
            f"{result.canonical_metric_name} "
            f"| {result.period} "
            f"| {result.status.value}"
        )

        print(
            "Resolved value:",
            result.resolved_value,
        )

        print(
            "Observations:"
        )

        for observation in (
            result.observations
        ):

            print(
                "  "
                f"page={observation.page_number}, "
                f"name={observation.metric_name}, "
                f"raw={observation.raw_value}, "
                f"normalized="
                f"{observation.normalized_value}"
            )

        print()
        

if __name__ == "__main__":
    main()
    