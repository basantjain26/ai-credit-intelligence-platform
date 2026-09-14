from typing import List

from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )


class BorrowerFinding(StrictBaseModel):
    title: str
    description: str

    severity: str
    category: str

    evidence_ids: List[str]


class BorrowerInconsistency(
    StrictBaseModel
):
    title: str
    description: str

    source_a: str
    source_b: str

    requires_follow_up: bool

    evidence_ids: List[str]


class InvestigationItem(
    StrictBaseModel
):
    issue: str
    reason: str

    priority: str

    evidence_ids: List[str]


class BorrowerIntelligenceOutput(
    StrictBaseModel
):
    borrower_summary: str

    relationship_summary: str

    application_summary: str

    key_findings: List[
        BorrowerFinding
    ]

    inconsistencies: List[
        BorrowerInconsistency
    ]

    missing_information: List[str]

    investigation_items: List[
        InvestigationItem
    ]

    overall_assessment: str