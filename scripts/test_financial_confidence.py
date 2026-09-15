from src.financial_analysis.confidence import (
    FinancialConfidenceEngine,
)


class FakeToolExecution:

    def __init__(
        self,
        tool_name,
        success,
        result=None,
        error=None,
    ):
        self.tool_name = (
            tool_name
        )

        self.success = (
            success
        )

        self.result = (
            result
        )

        self.error = (
            error
        )


class FakeProvenanceValidation:

    def __init__(
        self,
    ):
        self.verified_ratio_count = 3
        self.verified_evidence_count = 1


def main():

    customer_id = "CUST_000001"
    application_id = "APP_2026_00001"

    print(
        "Customer:",
        customer_id,
    )

    print(
        "Application:",
        application_id,
    )

    executions = [

        FakeToolExecution(
            tool_name=(
                "get_financial_overview"
            ),
            success=True,
            result={
                "financial_statements": [
                    {
                        "fiscal_year": 2026,
                    },
                    {
                        "fiscal_year": 2025,
                    },
                ],
                "reconciled_metrics": [
                    {
                        "canonical_name": (
                            "revenue"
                        ),
                        "fiscal_year": 2026,
                        "status": "CONFLICT",
                        "distinct_values": [
                            "790000000",
                            "850000000",
                        ],
                    },
                    {
                        "canonical_name": (
                            "ebitda"
                        ),
                        "fiscal_year": 2026,
                        "status": "MATCH",
                    },
                ],
            },
        ),

        FakeToolExecution(
            tool_name=(
                "get_financial_ratios"
            ),
            success=True,
            result={
                "ratios": [
                    {
                        "ratio_name": (
                            "debt_to_ebitda"
                        ),
                        "fiscal_year": 2026,
                        "status": (
                            "CALCULATED"
                        ),
                    },
                    {
                        "ratio_name": (
                            "dscr"
                        ),
                        "fiscal_year": 2026,
                        "status": (
                            "NOT_CALCULABLE"
                        ),
                        "reason": (
                            "debt_service "
                            "is unavailable"
                        ),
                    },
                ]
            },
        ),

        FakeToolExecution(
            tool_name=(
                "get_financial_trends"
            ),
            success=True,
            result={
                "metric_trends": [
                    {
                        "metric_name": (
                            "revenue"
                        ),
                        "status": (
                            "CALCULATED"
                        ),
                    }
                ],
                "ratio_trends": [],
            },
        ),

        FakeToolExecution(
            tool_name=(
                "search_financial_documents"
            ),
            success=True,
            result={
                "result_count": 2,
                "results": [
                    {
                        "chunk_id": (
                            "CHUNK_001"
                        )
                    },
                    {
                        "chunk_id": (
                            "CHUNK_002"
                        )
                    },
                ],
            },
        ),
    ]

    engine = (
        FinancialConfidenceEngine()
    )

    assessment = engine.assess(
        tool_executions=(
            executions
        ),
        provenance_validation=(
            FakeProvenanceValidation()
        ),
    )

    print(
        "\n"
        + "=" * 80
    )

    print(
        "FINANCIAL CONFIDENCE"
    )

    print(
        "=" * 80
    )

    print(
        "Level:",
        assessment
        .confidence_level
        .value,
    )

    print(
        "Score:",
        assessment
        .confidence_score,
    )

    print(
        "Summary:",
        assessment.summary,
    )

    print(
        "Successful tools:",
        assessment
        .successful_tool_count,
    )

    print(
        "Failed tools:",
        assessment
        .failed_tool_count,
    )

    print(
        "Verified ratios:",
        assessment
        .verified_ratio_count,
    )

    print(
        "Verified evidence:",
        assessment
        .verified_evidence_count,
    )

    print(
        "\nDATA QUALITY ISSUES"
    )

    for issue in (
        assessment
        .data_quality_issues
    ):

        print(
            "\nCode:",
            issue.issue_code,
        )

        print(
            "Severity:",
            issue.severity.value,
        )

        print(
            "Title:",
            issue.title,
        )

        print(
            "Description:",
            issue.description,
        )

        print(
            "Source:",
            issue.source,
        )


if __name__ == "__main__":
    main()