from pprint import pprint

from src.financial_analysis.metric_mapping import (
    CanonicalMetricMapper,
)


def main():

    mapper = CanonicalMetricMapper()

    print(
        "\n========== SUPPORTED METRICS ==========\n"
    )

    pprint(
        mapper.get_supported_metrics()
    )

    print(
        "\n========== NAME MAPPING ==========\n"
    )

    examples = [
        "Revenue",
        "Sales",
        "Turnover",
        "PAT",
        "Total Borrowings",
        "Finance Costs",
        "Cash Flow From Operations",
        "Trade Receivables",
        "Unknown Metric",
    ]

    for name in examples:
        print(
            f"{name:35} -> "
            f"{mapper.canonicalize_name(name)}"
        )

    print(
        "\n========== RECORD MAPPING ==========\n"
    )

    sample_financial_record = {
        "financial_statement_id": "FS001",
        "customer_id": "CUST_000001",
        "fiscal_year": 2026,
        "revenue": 790_000_000,
        "ebitda": 95_000_000,
        "net_income": 39_000_000,
        "total_debt": 125_000_000,
        "operating_cash_flow": 57_000_000,
    }

    mapped_metrics = mapper.map_record(
        record=sample_financial_record,
        source_type="STRUCTURED_FINANCIAL_STATEMENT",
        fiscal_year=2026,
        excluded_fields={
            "financial_statement_id",
            "customer_id",
            "fiscal_year",
        },
    )

    for metric in mapped_metrics:
        pprint(metric)


if __name__ == "__main__":
    main()