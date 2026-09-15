from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

class CalculationInputReference(BaseModel):
    """
    One deterministic input used in a financial calculation.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    metric_name: str

    value: str | None

    fiscal_year: int | None

    source_status: str | None


class CalculationProvenance(BaseModel):
    """
    Provenance for a deterministic financial calculation.

    The LLM does not create the calculation. It references
    calculation information returned by the deterministic
    ratio tool.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    formula: str | None

    inputs: list[
        CalculationInputReference
    ]


class DocumentEvidenceReference(BaseModel):
    """
    Reference to documentary evidence retrieved during the
    current agent execution.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    chunk_id: str

    document_id: str

    document_name: str

    page_number: int | None

class CalculatedRatioFinding(BaseModel):
    """
    Ratio reported by the Financial Analysis Agent.

    Every reported ratio must match a deterministic ratio
    returned during the current agent execution.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    ratio_name: str

    fiscal_year: int | None

    status: Literal[
        "CALCULATED",
        "NOT_CALCULABLE",
    ]

    value: str | None

    unit: str | None

    interpretation: str

    calculation_provenance: (
        CalculationProvenance
        | None
    ) = Field(
        description=(
            "Deterministic calculation provenance. "
            "Null when no calculation provenance "
            "is available."
        )
    )


class FinancialTrendFinding(BaseModel):
    """
    Material historical financial trend identified during
    financial analysis.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    metric_name: str

    direction: Literal[
        "IMPROVING",
        "DETERIORATING",
        "STABLE",
        "MIXED",
        "NOT_AVAILABLE",
    ]

    latest_year: int | None
    previous_year: int | None

    latest_value: str | None
    previous_value: str | None

    percentage_change: str | None

    interpretation: str = Field(
        description=(
            "Interpretation grounded in deterministic "
            "trend-tool results."
        )
    )


class FinancialStrength(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    title: str
    description: str

    supporting_tool: str | None

    evidence: list[
        DocumentEvidenceReference
    ] = Field(
        default_factory=list
    )


class FinancialConcern(BaseModel):
    """
    Material financial concern identified by the agent.
    """
    model_config = ConfigDict(
        extra="forbid"
    )

    title: str
    description: str

    severity: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
    ]

    supporting_tool: str | None

    evidence: list[
        DocumentEvidenceReference
    ] = Field(
        default_factory=list
    )

    

class FinancialInconsistency(BaseModel):
    """
    Conflicting financial information that should be
    reviewed by a human analyst.
    """
    
    model_config = ConfigDict(
        extra="forbid"
    )

    metric_name: str

    fiscal_year: int | None

    description: str

    source_values: list[str]

    requires_review: bool

    evidence: list[
        DocumentEvidenceReference
    ] = Field(
        default_factory=list
    )


class MissingFinancialInformation(BaseModel):
    """
    Financial information that is missing or insufficient
    for reliable analysis.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    item: str

    reason: str

    impact: str = Field(
        description=(
            "How the missing information limits the analysis."
        )
    )


class FinancialInvestigationItem(BaseModel):
    """
    Follow-up item for a human credit analyst or subsequent
    investigation workflow.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
    ]

    question: str

    rationale: str


class FinancialAnalysisOutput(BaseModel):
    """
    Strict final output contract for the Financial Analysis
    Agent.

    This schema intentionally does not contain an approve/reject
    recommendation. Final credit decisions remain human-owned.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    customer_id: str
    application_id: str

    financial_summary: str = Field(
        description=(
            "Concise overall summary of the borrower's "
            "financial condition."
        )
    )

    overall_financial_condition: Literal[
        "STRONG",
        "ADEQUATE",
        "WEAK",
        "DETERIORATING",
        "MIXED",
        "INSUFFICIENT_DATA",
    ]

    calculated_ratios: list[
        CalculatedRatioFinding
    ]

    trend_findings: list[
        FinancialTrendFinding
    ]

    strengths: list[
        FinancialStrength
    ]

    concerns: list[
        FinancialConcern
    ]

    inconsistencies: list[
        FinancialInconsistency
    ]

    missing_information: list[
        MissingFinancialInformation
    ]

    investigation_items: list[
        FinancialInvestigationItem
    ]