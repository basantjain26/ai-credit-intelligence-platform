from __future__ import annotations

from src.policy_intelligence.models import (
    PolicyEvaluation,
    PolicyEvaluationResult,
    PolicyFacts,
    PolicyStatus,
)


MINIMUM_DSCR = 1.25
MAXIMUM_DEBT_TO_EBITDA = 4.00
MINIMUM_RELATIONSHIP_YEARS = 2.0


class LendingPolicyEngine:

    def evaluate(
        self,
        facts: PolicyFacts,
    ) -> PolicyEvaluationResult:

        evaluations = [
            self._evaluate_dscr(
                facts.dscr
            ),
            self._evaluate_leverage(
                facts.debt_to_ebitda
            ),
            self._evaluate_documentation(
                facts.audited_financials_available
            ),
            self._evaluate_relationship(
                facts.banking_relationship_years
            ),
            self._evaluate_related_party(
                facts.material_related_party_transaction
            ),
            self._evaluate_unusual_transaction(
                facts.unusual_transaction_detected
            ),
        ]

        return PolicyEvaluationResult(
            evaluations=evaluations
        )

    @staticmethod
    def _evaluate_dscr(
        dscr: float | None,
    ) -> PolicyEvaluation:

        if dscr is None:
            return PolicyEvaluation(
                policy_id="POL_DSCR_001",
                policy_name="Debt Service Coverage",
                status=PolicyStatus.INSUFFICIENT_DATA,
                actual_value=None,
                requirement="DSCR >= 1.25",
                reason=(
                    "DSCR is unavailable and "
                    "the policy cannot be evaluated."
                ),
            )

        if dscr >= MINIMUM_DSCR:
            status = PolicyStatus.COMPLIANT
            reason = (
                f"DSCR of {dscr:.2f} meets "
                "the minimum requirement of 1.25."
            )
        else:
            status = PolicyStatus.VIOLATION
            reason = (
                f"DSCR of {dscr:.2f} is below "
                "the minimum requirement of 1.25."
            )

        return PolicyEvaluation(
            policy_id="POL_DSCR_001",
            policy_name="Debt Service Coverage",
            status=status,
            actual_value=dscr,
            requirement="DSCR >= 1.25",
            reason=reason,
        )

    @staticmethod
    def _evaluate_leverage(
        debt_to_ebitda: float | None,
    ) -> PolicyEvaluation:

        if debt_to_ebitda is None:
            return PolicyEvaluation(
                policy_id="POL_LEVERAGE_001",
                policy_name="Leverage",
                status=PolicyStatus.INSUFFICIENT_DATA,
                actual_value=None,
                requirement="Debt/EBITDA <= 4.00",
                reason=(
                    "Debt-to-EBITDA is unavailable."
                ),
            )

        if debt_to_ebitda <= MAXIMUM_DEBT_TO_EBITDA:
            status = PolicyStatus.COMPLIANT
            reason = (
                f"Debt-to-EBITDA of "
                f"{debt_to_ebitda:.2f} is within "
                "the maximum permitted level of 4.00."
            )
        else:
            status = PolicyStatus.VIOLATION
            reason = (
                f"Debt-to-EBITDA of "
                f"{debt_to_ebitda:.2f} exceeds "
                "the maximum permitted level of 4.00."
            )

        return PolicyEvaluation(
            policy_id="POL_LEVERAGE_001",
            policy_name="Leverage",
            status=status,
            actual_value=debt_to_ebitda,
            requirement="Debt/EBITDA <= 4.00",
            reason=reason,
        )

    @staticmethod
    def _evaluate_documentation(
        audited_available: bool | None,
    ) -> PolicyEvaluation:

        if audited_available is None:
            return PolicyEvaluation(
                policy_id="POL_DOC_001",
                policy_name="Financial Documentation",
                status=PolicyStatus.INSUFFICIENT_DATA,
                actual_value=None,
                requirement=(
                    "Latest audited financial "
                    "statements required"
                ),
                reason=(
                    "Availability of audited financial "
                    "statements is unknown."
                ),
            )

        if audited_available:
            status = PolicyStatus.COMPLIANT
            reason = (
                "Latest audited financial statements "
                "are available."
            )
        else:
            status = PolicyStatus.VIOLATION
            reason = (
                "Latest audited financial statements "
                "are not available."
            )

        return PolicyEvaluation(
            policy_id="POL_DOC_001",
            policy_name="Financial Documentation",
            status=status,
            actual_value=audited_available,
            requirement=(
                "Latest audited financial "
                "statements required"
            ),
            reason=reason,
        )

    @staticmethod
    def _evaluate_relationship(
        relationship_years: float | None,
    ) -> PolicyEvaluation:

        if relationship_years is None:
            return PolicyEvaluation(
                policy_id="POL_RELATIONSHIP_001",
                policy_name="Banking Relationship",
                status=PolicyStatus.INSUFFICIENT_DATA,
                actual_value=None,
                requirement=(
                    "Banking relationship >= 2 years"
                ),
                reason=(
                    "Banking relationship duration "
                    "is unavailable."
                ),
            )

        if relationship_years >= MINIMUM_RELATIONSHIP_YEARS:
            status = PolicyStatus.COMPLIANT
            reason = (
                f"Banking relationship of "
                f"{relationship_years:.1f} years meets "
                "the minimum two-year requirement."
            )
        else:
            status = PolicyStatus.VIOLATION
            reason = (
                f"Banking relationship of "
                f"{relationship_years:.1f} years is "
                "below the minimum two-year requirement."
            )

        return PolicyEvaluation(
            policy_id="POL_RELATIONSHIP_001",
            policy_name="Banking Relationship",
            status=status,
            actual_value=relationship_years,
            requirement="Banking relationship >= 2 years",
            reason=reason,
        )

    @staticmethod
    def _evaluate_related_party(
        material_transaction: bool | None,
    ) -> PolicyEvaluation:

        if material_transaction is None:
            return PolicyEvaluation(
                policy_id="POL_RELATED_PARTY_001",
                policy_name="Related-Party Transactions",
                status=PolicyStatus.INSUFFICIENT_DATA,
                actual_value=None,
                requirement=(
                    "Material related-party transactions "
                    "require enhanced review"
                ),
                reason=(
                    "Related-party transaction status "
                    "is unavailable."
                ),
            )

        if material_transaction:
            status = PolicyStatus.ENHANCED_REVIEW
            reason = (
                "A material related-party transaction "
                "was identified and requires enhanced "
                "credit review."
            )
        else:
            status = PolicyStatus.COMPLIANT
            reason = (
                "No material related-party transaction "
                "was identified."
            )

        return PolicyEvaluation(
            policy_id="POL_RELATED_PARTY_001",
            policy_name="Related-Party Transactions",
            status=status,
            actual_value=material_transaction,
            requirement=(
                "Material related-party transactions "
                "require enhanced review"
            ),
            reason=reason,
        )

    @staticmethod
    def _evaluate_unusual_transaction(
        unusual_transaction: bool | None,
    ) -> PolicyEvaluation:

        if unusual_transaction is None:
            return PolicyEvaluation(
                policy_id="POL_TRANSACTION_001",
                policy_name="Unusual Transactions",
                status=PolicyStatus.INSUFFICIENT_DATA,
                actual_value=None,
                requirement=(
                    "Large or unusual transactions "
                    "require enhanced review"
                ),
                reason=(
                    "Unusual transaction status "
                    "is unavailable."
                ),
            )

        if unusual_transaction:
            status = PolicyStatus.ENHANCED_REVIEW
            reason = (
                "A large or unusual transaction was "
                "identified and requires enhanced review."
            )
        else:
            status = PolicyStatus.COMPLIANT
            reason = (
                "No large or unusual transaction "
                "requiring enhanced review was identified."
            )

        return PolicyEvaluation(
            policy_id="POL_TRANSACTION_001",
            policy_name="Unusual Transactions",
            status=status,
            actual_value=unusual_transaction,
            requirement=(
                "Large or unusual transactions "
                "require enhanced review"
            ),
            reason=reason,
        )