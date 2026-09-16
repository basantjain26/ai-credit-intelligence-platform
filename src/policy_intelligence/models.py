from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PolicyStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    VIOLATION = "VIOLATION"
    ENHANCED_REVIEW = "ENHANCED_REVIEW"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass
class PolicyFacts:
    dscr: float | None
    debt_to_ebitda: float | None
    audited_financials_available: bool | None
    banking_relationship_years: float | None
    material_related_party_transaction: bool | None
    unusual_transaction_detected: bool | None


@dataclass
class PolicyEvaluation:
    policy_id: str
    policy_name: str
    status: PolicyStatus
    actual_value: Any
    requirement: str
    reason: str


@dataclass
class PolicyEvaluationResult:
    evaluations: list[PolicyEvaluation]

    @property
    def violations(
        self,
    ) -> list[PolicyEvaluation]:
        return [
            evaluation
            for evaluation in self.evaluations
            if evaluation.status
            == PolicyStatus.VIOLATION
        ]

    @property
    def enhanced_reviews(
        self,
    ) -> list[PolicyEvaluation]:
        return [
            evaluation
            for evaluation in self.evaluations
            if evaluation.status
            == PolicyStatus.ENHANCED_REVIEW
        ]