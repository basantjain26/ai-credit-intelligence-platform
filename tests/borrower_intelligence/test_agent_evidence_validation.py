import pytest

from src.borrower_intelligence.agent import (
    BorrowerIntelligenceAgent,
)
from src.borrower_intelligence.evidence import (
    EvidenceRecord,
)
from src.borrower_intelligence.schemas import (
    BorrowerFinding,
    BorrowerIntelligenceOutput,
)


def build_output(
    evidence_ids: list[str],
) -> BorrowerIntelligenceOutput:

    return BorrowerIntelligenceOutput(
        borrower_summary=(
            "ABC Manufacturing is an existing "
            "commercial banking customer."
        ),
        relationship_summary=(
            "The borrower has an established "
            "relationship with the bank."
        ),
        application_summary=(
            "The borrower has submitted a working "
            "capital facility request."
        ),
        key_findings=[
            BorrowerFinding(
                title=(
                    "Revenue reporting discrepancy"
                ),
                description=(
                    "Declared revenue differs from "
                    "audited revenue."
                ),
                severity="HIGH",
                category=(
                    "FINANCIAL_REPORTING"
                ),
                evidence_ids=evidence_ids,
            )
        ],
        inconsistencies=[],
        missing_information=[],
        investigation_items=[],
        overall_assessment=(
            "Further investigation is required."
        ),
    )


def build_evidence() -> list[EvidenceRecord]:

    return [
        EvidenceRecord(
            evidence_id="EVID-001",
            source_type="STRUCTURED_DATA",
            source_name=(
                "get_borrower_signals"
            ),
            tool_name=(
                "get_borrower_signals"
            ),
            content={
                "declared_revenue": (
                    "850000000"
                ),
                "audited_revenue": (
                    "790000000"
                ),
                "revenue_mismatch": True,
            },
        )
    ]


def test_valid_evidence_reference_passes():

    output = build_output(
        evidence_ids=[
            "EVID-001",
        ]
    )

    evidence = build_evidence()

    agent = (
        BorrowerIntelligenceAgent.__new__(
            BorrowerIntelligenceAgent
        )
    )

    agent._validate_evidence_references(
        output=output,
        evidence=evidence,
    )


def test_invalid_evidence_reference_fails():

    output = build_output(
        evidence_ids=[
            "EVID-001",
            "EVID-999",
        ]
    )

    evidence = build_evidence()

    agent = (
        BorrowerIntelligenceAgent.__new__(
            BorrowerIntelligenceAgent
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "Agent referenced invalid "
            "evidence IDs"
        ),
    ):

        agent._validate_evidence_references(
            output=output,
            evidence=evidence,
        )


def test_multiple_invalid_evidence_ids_fail():

    output = build_output(
        evidence_ids=[
            "EVID-777",
            "EVID-999",
        ]
    )

    evidence = build_evidence()

    agent = (
        BorrowerIntelligenceAgent.__new__(
            BorrowerIntelligenceAgent
        )
    )

    with pytest.raises(
        ValueError,
    ) as exc_info:

        agent._validate_evidence_references(
            output=output,
            evidence=evidence,
        )

    message = str(
        exc_info.value
    )

    assert "EVID-777" in message
    assert "EVID-999" in message


def test_empty_evidence_ids_are_allowed():

    output = build_output(
        evidence_ids=[]
    )

    evidence = build_evidence()

    agent = (
        BorrowerIntelligenceAgent.__new__(
            BorrowerIntelligenceAgent
        )
    )

    agent._validate_evidence_references(
        output=output,
        evidence=evidence,
    )