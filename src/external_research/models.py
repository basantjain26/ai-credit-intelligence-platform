from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


EntityMatch = Literal[
    "MATCH",
    "POSSIBLE_MATCH",
    "NO_MATCH",
]


RiskRelevance = Literal[
    "HIGH",
    "MEDIUM",
    "LOW",
    "INFORMATIONAL",
]


class ResearchFinding(BaseModel):
    finding: str = Field(
        description=(
            "Concise factual finding supported "
            "by external evidence."
        )
    )

    entity_match: EntityMatch = Field(
        description=(
            "Whether the external evidence refers "
            "to the borrower being investigated."
        )
    )

    risk_relevance: RiskRelevance = Field(
        description=(
            "Potential relevance of the finding "
            "to credit-risk investigation."
        )
    )

    evidence: str = Field(
        description=(
            "Short evidence summary supporting "
            "the finding."
        )
    )

    source_title: str = Field(
        description="Title of the external source."
    )

    source_url: str = Field(
        description="URL of the external source."
    )


class ExternalResearchResult(BaseModel):
    borrower_name: str

    research_summary: str

    findings: list[ResearchFinding]

    unresolved_entity_matches: list[str]

    research_limitations: list[str]