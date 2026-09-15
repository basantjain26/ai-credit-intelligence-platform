from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal[
    "LOW",
    "MODERATE",
    "ELEVATED",
    "HIGH",
]


FindingSeverity = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
]


EvidenceType = Literal[
    "TRANSACTION",
    "ML_ANOMALY",
    "RELATED_PARTY",
    "BUSINESS_RULE",
]


class TransactionEvidence(BaseModel):
    """
    Evidence supporting one investigation finding.

    This is evidence/reference information, not an LLM-created
    database record.
    """

    evidence_type: EvidenceType

    transaction_id: str | None = None

    description: str

    anomaly_score: float | None = None

    model_version: str | None = None

    feature_version: str | None = None


class TransactionFinding(BaseModel):
    """
    One material transaction-risk finding.
    """

    finding_id: str

    title: str

    severity: FindingSeverity

    explanation: str

    credit_risk_relevance: str

    transaction_ids: list[str] = Field(
        default_factory=list
    )

    evidence: list[TransactionEvidence] = Field(
        default_factory=list
    )

    analyst_follow_up: str | None = None


class TransactionInvestigationResult(BaseModel):
    """
    Final structured output produced by the transaction agent.
    """

    customer_id: str

    application_id: str

    overall_transaction_risk: RiskLevel

    summary: str

    findings: list[TransactionFinding]

    transactions_requiring_review: list[str] = Field(
        default_factory=list
    )

    additional_information_required: list[str] = Field(
        default_factory=list
    )

    limitations: list[str] = Field(
        default_factory=list
    )