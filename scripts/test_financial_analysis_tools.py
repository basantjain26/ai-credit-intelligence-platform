from pprint import pprint

from src.financial_analysis.tools import (
    FinancialAnalysisTools,
)


def print_section(
    title: str,
):
    print(
        "\n"
        + "=" * 80
    )

    print(title)

    print(
        "=" * 80
    )


def main():

    customer_id = "CUST_000001"
    application_id = "APP_2026_00001"

    with FinancialAnalysisTools(
        customer_id=customer_id,
        application_id=application_id,
    ) as tools:

        # -------------------------------------------------
        # 1. FINANCIAL OVERVIEW
        # -------------------------------------------------

        print_section(
            "FINANCIAL OVERVIEW"
        )

        overview = (
            tools.get_financial_overview()
        )

        print(
            "Customer:",
            overview["customer_id"],
        )

        print(
            "Application:",
            overview["application_id"],
        )

        print(
            "\nReconciled Metrics:"
        )

        pprint(
            overview[
                "reconciled_metrics"
            ]
        )

        # -------------------------------------------------
        # 2. FINANCIAL RATIOS
        # -------------------------------------------------

        print_section(
            "FINANCIAL RATIOS"
        )

        ratios = (
            tools.get_financial_ratios()
        )

        pprint(
            ratios["ratios"]
        )

        # -------------------------------------------------
        # 3. HISTORICAL TRENDS
        # -------------------------------------------------

        print_section(
            "FINANCIAL TRENDS"
        )

        trends = (
            tools.get_financial_trends()
        )

        print(
            "Overall Direction:",
            trends[
                "overall_direction"
            ],
        )

        print(
            "\nMetric Trends:"
        )

        pprint(
            trends[
                "metric_trends"
            ]
        )

        print(
            "\nRatio Trends:"
        )

        pprint(
            trends[
                "ratio_trends"
            ]
        )

        # -------------------------------------------------
        # 4. RISK SIGNALS
        # -------------------------------------------------

        print_section(
            "FINANCIAL RISK SIGNALS"
        )

        risk = (
            tools
            .get_financial_risk_signals()
        )

        print(
            "High:",
            risk["high_count"],
        )

        print(
            "Medium:",
            risk["medium_count"],
        )

        print(
            "Low:",
            risk["low_count"],
        )

        print(
            "\nSignals:"
        )

        pprint(
            risk["signals"]
        )

        # -------------------------------------------------
        # 5. DOCUMENT RETRIEVAL
        # -------------------------------------------------

        print_section(
            "FINANCIAL DOCUMENT SEARCH"
        )

        evidence = (
            tools.search_financial_documents(
                query=(
                    "revenue EBITDA debt "
                    "and financial performance"
                ),
                limit=5,
            )
        )

        print(
            "Query:",
            evidence["query"],
        )

        print(
            "Results:",
            evidence[
                "result_count"
            ],
        )

        pprint(
            evidence["results"]
        )


if __name__ == "__main__":
    main()