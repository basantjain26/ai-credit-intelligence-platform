from src.financial_analysis.provenance import (
    FinancialProvenanceValidator,
)
from src.financial_analysis.schemas import (
    CalculatedRatioFinding,
    CalculationInputReference,
    CalculationProvenance,
    DocumentEvidenceReference,
    FinancialAnalysisOutput,
    FinancialConcern,
)


class FakeToolExecution:
    def __init__(
        self,
        tool_name,
        success,
        result,
    ):
        self.tool_name = tool_name
        self.success = success
        self.result = result


def main():

    customer_id = "CUST_000001"
    application_id = "APP_2026_00001"

    ratio_execution = FakeToolExecution(
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
                    "status": "CALCULATED",
                    "value": "1.3158",
                    "unit": "x",
                    "formula": (
                        "Total Debt / EBITDA"
                    ),
                    "inputs": [
                        {
                            "metric_name": (
                                "total_debt"
                            ),
                            "value": (
                                "125000000"
                            ),
                            "fiscal_year": 2026,
                            "source_status": (
                                "UNIQUE"
                            ),
                        },
                        {
                            "metric_name": (
                                "ebitda"
                            ),
                            "value": (
                                "95000000"
                            ),
                            "fiscal_year": 2026,
                            "source_status": (
                                "UNIQUE"
                            ),
                        },
                    ],
                }
            ]
        },
    )

    retrieval_execution = FakeToolExecution(
        tool_name=(
            "search_financial_documents"
        ),
        success=True,
        result={
            "results": [
                {
                    "chunk_id": "CHUNK_001",
                    "document_id": "DOC_001",
                    "document_name": (
                        "ABC_FY2026_"
                        "Audited_Financials.pdf"
                    ),
                    "page_number": 2,
                    "chunk_text": (
                        "Revenue and financial "
                        "performance..."
                    ),
                }
            ]
        },
    )

    analysis = FinancialAnalysisOutput(
        customer_id=customer_id,
        application_id=application_id,
        financial_summary=(
            "Financial performance shows "
            "areas requiring review."
        ),
        overall_financial_condition=(
            "MIXED"
        ),
        calculated_ratios=[
            CalculatedRatioFinding(
                ratio_name=(
                    "debt_to_ebitda"
                ),
                fiscal_year=2026,
                status="CALCULATED",
                value="1.3158",
                unit="x",
                interpretation=(
                    "Leverage remains measurable "
                    "against EBITDA."
                ),
                calculation_provenance=(
                    CalculationProvenance(
                        formula=(
                            "Total Debt / EBITDA"
                        ),
                        inputs=[
                            CalculationInputReference(
                                metric_name=(
                                    "total_debt"
                                ),
                                value=(
                                    "125000000"
                                ),
                                fiscal_year=2026,
                                source_status=(
                                    "UNIQUE"
                                ),
                            ),
                            CalculationInputReference(
                                metric_name=(
                                    "ebitda"
                                ),
                                value=(
                                    "95000000"
                                ),
                                fiscal_year=2026,
                                source_status=(
                                    "UNIQUE"
                                ),
                            ),
                        ],
                    )
                ),
            )
        ],
        trend_findings=[],
        strengths=[],
        concerns=[
            FinancialConcern(
                title=(
                    "Financial performance "
                    "requires review"
                ),
                description=(
                    "Audited financial evidence "
                    "was reviewed."
                ),
                severity="MEDIUM",
                supporting_tool=(
                    "search_financial_documents"
                ),
                evidence=[
                    DocumentEvidenceReference(
                        chunk_id="CHUNK_001",
                        document_id="DOC_001",
                        document_name=(
                            "ABC_FY2026_"
                            "Audited_Financials.pdf"
                        ),
                        page_number=2,
                    )
                ],
            )
        ],
        inconsistencies=[],
        missing_information=[],
        investigation_items=[],
    )

    validator = (
        FinancialProvenanceValidator()
    )

    result = validator.validate(
        analysis=analysis,
        tool_executions=[
            ratio_execution,
            retrieval_execution,
        ],
    )

    print(
        "\nVALID PROVENANCE TEST"
    )

    print(
        "Valid:",
        result.valid,
    )

    print(
        "Verified ratios:",
        result.verified_ratio_count,
    )

    print(
        "Verified evidence:",
        result.verified_evidence_count,
    )

    print(
        "Issues:",
        result.issues,
    )

    # -----------------------------------------------------
    # Deliberately corrupt the ratio
    # -----------------------------------------------------

    analysis.calculated_ratios[
        0
    ].value = "9.9999"

    bad_result = validator.validate(
        analysis=analysis,
        tool_executions=[
            ratio_execution,
            retrieval_execution,
        ],
    )

    print(
        "\nINVALID RATIO TEST"
    )

    print(
        "Valid:",
        bad_result.valid,
    )

    for issue in (
        bad_result.issues
    ):
        print(
            issue.issue_type,
            "->",
            issue.message,
        )


if __name__ == "__main__":
    main()