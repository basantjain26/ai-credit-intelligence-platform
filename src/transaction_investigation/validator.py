from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.transaction_investigation.schemas import (
    TransactionEvidence,
    TransactionInvestigationResult,
)
from src.transaction_investigation.tools import (
    TransactionInvestigationContext,
)


@dataclass
class ValidationIssue:
    """
    One provenance validation failure.
    """

    code: str
    message: str
    finding_id: str | None = None
    transaction_id: str | None = None


@dataclass
class TransactionValidationResult:
    """
    Result of deterministic provenance validation.
    """

    is_valid: bool

    validated_transaction_ids: list[str] = field(
        default_factory=list
    )

    issues: list[ValidationIssue] = field(
        default_factory=list
    )


class TransactionProvenanceValidator:
    """
    Deterministically validate material claims produced by the
    transaction investigation agent.

    Important:

    This validator does NOT ask an LLM whether another LLM's
    answer looks reasonable.

    It checks the answer against trusted application state.
    """

    ANOMALY_SCORE_TOLERANCE = 1e-6

    def __init__(
        self,
        context: TransactionInvestigationContext,
    ) -> None:

        self.context = context

        # -----------------------------------------------------
        # All transaction IDs belonging to this trusted case.
        # -----------------------------------------------------

        all_transactions = (
            context.training_transactions
            + context.inference_transactions
        )

        self.valid_transaction_ids = {
            row["transaction_id"]
            for row in all_transactions
        }

        # -----------------------------------------------------
        # Current investigation-window transactions.
        #
        # Findings should normally reference these transactions.
        # -----------------------------------------------------

        self.inference_transaction_ids = {
            row["transaction_id"]
            for row in context.inference_transactions
        }

    # =========================================================
    # PUBLIC API
    # =========================================================

    def validate(
        self,
        result: TransactionInvestigationResult,
    ) -> TransactionValidationResult:
        """
        Validate the final structured transaction investigation.
        """

        issues: list[ValidationIssue] = []

        validated_transaction_ids: set[str] = set()

        # =====================================================
        # CASE SCOPE
        # =====================================================

        self._validate_case_scope(
            result=result,
            issues=issues,
        )

        # =====================================================
        # FINDINGS
        # =====================================================

        for finding in result.findings:

            # -------------------------------------------------
            # Validate transaction IDs directly referenced by
            # the finding.
            # -------------------------------------------------

            for transaction_id in (
                finding.transaction_ids
            ):

                if self._validate_transaction_id(
                    transaction_id=transaction_id,
                    finding_id=finding.finding_id,
                    issues=issues,
                ):
                    validated_transaction_ids.add(
                        transaction_id
                    )

            # -------------------------------------------------
            # Validate each evidence object.
            # -------------------------------------------------

            for evidence in finding.evidence:

                self._validate_evidence(
                    evidence=evidence,
                    finding_id=finding.finding_id,
                    finding_transaction_ids=(
                        finding.transaction_ids
                    ),
                    validated_transaction_ids=(
                        validated_transaction_ids
                    ),
                    issues=issues,
                )

        # =====================================================
        # REVIEW QUEUE
        # =====================================================

        for transaction_id in (
            result.transactions_requiring_review
        ):

            if self._validate_transaction_id(
                transaction_id=transaction_id,
                finding_id=None,
                issues=issues,
            ):
                validated_transaction_ids.add(
                    transaction_id
                )

        return TransactionValidationResult(
            is_valid=not issues,
            validated_transaction_ids=sorted(
                validated_transaction_ids
            ),
            issues=issues,
        )

    # =========================================================
    # CASE SCOPE
    # =========================================================

    def _validate_case_scope(
        self,
        result: TransactionInvestigationResult,
        issues: list[ValidationIssue],
    ) -> None:

        if (
            result.customer_id
            != self.context.customer_id
        ):

            issues.append(
                ValidationIssue(
                    code="CUSTOMER_SCOPE_MISMATCH",
                    message=(
                        "Result customer_id does not match "
                        "the trusted investigation context."
                    ),
                )
            )

        if (
            result.application_id
            != self.context.application_id
        ):

            issues.append(
                ValidationIssue(
                    code="APPLICATION_SCOPE_MISMATCH",
                    message=(
                        "Result application_id does not match "
                        "the trusted investigation context."
                    ),
                )
            )

    # =========================================================
    # TRANSACTION ID
    # =========================================================

    def _validate_transaction_id(
        self,
        transaction_id: str,
        finding_id: str | None,
        issues: list[ValidationIssue],
    ) -> bool:

        if (
            transaction_id
            not in self.valid_transaction_ids
        ):

            issues.append(
                ValidationIssue(
                    code="UNKNOWN_TRANSACTION_ID",
                    message=(
                        "Transaction ID is not present in the "
                        "trusted customer transaction data."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

            return False

        if (
            transaction_id
            not in self.inference_transaction_ids
        ):

            issues.append(
                ValidationIssue(
                    code="OUTSIDE_INVESTIGATION_WINDOW",
                    message=(
                        "Transaction exists but is outside the "
                        "current inference/investigation window."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

            return False

        return True

    # =========================================================
    # EVIDENCE
    # =========================================================

    def _validate_evidence(
        self,
        evidence: TransactionEvidence,
        finding_id: str,
        finding_transaction_ids: list[str],
        validated_transaction_ids: set[str],
        issues: list[ValidationIssue],
    ) -> None:

        transaction_id = (
            evidence.transaction_id
        )

        # -----------------------------------------------------
        # Evidence types referring to a specific transaction
        # should contain a transaction ID.
        # -----------------------------------------------------

        transaction_evidence_types = {
            "TRANSACTION",
            "ML_ANOMALY",
            "RELATED_PARTY",
            "BUSINESS_RULE",
        }

        if (
            evidence.evidence_type
            in transaction_evidence_types
            and not transaction_id
        ):

            issues.append(
                ValidationIssue(
                    code="MISSING_EVIDENCE_TRANSACTION_ID",
                    message=(
                        f"{evidence.evidence_type} evidence "
                        "does not contain a transaction_id."
                    ),
                    finding_id=finding_id,
                )
            )

            return

        if not transaction_id:
            return

        # -----------------------------------------------------
        # Transaction existence + investigation window.
        # -----------------------------------------------------

        transaction_valid = (
            self._validate_transaction_id(
                transaction_id=transaction_id,
                finding_id=finding_id,
                issues=issues,
            )
        )

        if not transaction_valid:
            return

        validated_transaction_ids.add(
            transaction_id
        )

        # -----------------------------------------------------
        # Evidence should correspond to a transaction explicitly
        # referenced by its parent finding.
        # -----------------------------------------------------

        if (
            transaction_id
            not in finding_transaction_ids
        ):

            issues.append(
                ValidationIssue(
                    code="EVIDENCE_FINDING_MISMATCH",
                    message=(
                        "Evidence references a transaction that "
                        "is not listed in the parent finding's "
                        "transaction_ids."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

        # =====================================================
        # ML ANOMALY PROVENANCE
        # =====================================================

        if (
            evidence.evidence_type
            == "ML_ANOMALY"
        ):

            self._validate_ml_evidence(
                evidence=evidence,
                finding_id=finding_id,
                issues=issues,
            )

        # =====================================================
        # RELATED-PARTY PROVENANCE
        # =====================================================

        elif (
            evidence.evidence_type
            == "RELATED_PARTY"
        ):

            self._validate_related_party_evidence(
                transaction_id=transaction_id,
                finding_id=finding_id,
                issues=issues,
            )

        # =====================================================
        # BUSINESS RULE PROVENANCE
        # =====================================================

        elif (
            evidence.evidence_type
            == "BUSINESS_RULE"
        ):

            self._validate_business_rule_evidence(
                transaction_id=transaction_id,
                finding_id=finding_id,
                issues=issues,
            )

    # =========================================================
    # ML EVIDENCE
    # =========================================================

    def _validate_ml_evidence(
        self,
        evidence: TransactionEvidence,
        finding_id: str,
        issues: list[ValidationIssue],
    ) -> None:

        transaction_id = (
            evidence.transaction_id
        )

        if not transaction_id:
            return

        actual_result = (
            self.context.get_anomaly_result(
                transaction_id
            )
        )

        if actual_result is None:

            issues.append(
                ValidationIssue(
                    code="MISSING_MODEL_RESULT",
                    message=(
                        "ML anomaly evidence was supplied but "
                        "no trusted model result exists for "
                        "the transaction."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

            return

        # -----------------------------------------------------
        # Important semantic check:
        #
        # ML_ANOMALY evidence should only be used when the
        # Isolation Forest actually classified the transaction
        # as an anomaly.
        # -----------------------------------------------------

        if not actual_result.is_anomaly:

            issues.append(
                ValidationIssue(
                    code="NOT_MODEL_ANOMALY",
                    message=(
                        "Evidence labels the transaction as an "
                        "ML anomaly, but the trusted Isolation "
                        "Forest result does not classify it as "
                        "an anomalous transaction."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

        # -----------------------------------------------------
        # Anomaly score
        # -----------------------------------------------------

        if (
            evidence.anomaly_score
            is None
        ):

            issues.append(
                ValidationIssue(
                    code="MISSING_ANOMALY_SCORE",
                    message=(
                        "ML anomaly evidence does not include "
                        "the trusted anomaly score."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

        elif not self._float_matches(
            evidence.anomaly_score,
            actual_result.anomaly_score,
        ):

            issues.append(
                ValidationIssue(
                    code="ANOMALY_SCORE_MISMATCH",
                    message=(
                        "Evidence anomaly score does not match "
                        "the trusted Isolation Forest result. "
                        f"Expected "
                        f"{actual_result.anomaly_score}, "
                        f"received "
                        f"{evidence.anomaly_score}."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

        # -----------------------------------------------------
        # Model version
        # -----------------------------------------------------

        if (
            evidence.model_version
            != actual_result.model_version
        ):

            issues.append(
                ValidationIssue(
                    code="MODEL_VERSION_MISMATCH",
                    message=(
                        "Evidence model_version does not match "
                        "the trusted anomaly result. "
                        f"Expected "
                        f"{actual_result.model_version}, "
                        f"received "
                        f"{evidence.model_version}."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

        # -----------------------------------------------------
        # Feature version
        # -----------------------------------------------------

        if (
            evidence.feature_version
            != actual_result.feature_version
        ):

            issues.append(
                ValidationIssue(
                    code="FEATURE_VERSION_MISMATCH",
                    message=(
                        "Evidence feature_version does not match "
                        "the trusted anomaly result. "
                        f"Expected "
                        f"{actual_result.feature_version}, "
                        f"received "
                        f"{evidence.feature_version}."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

    # =========================================================
    # RELATED-PARTY EVIDENCE
    # =========================================================

    def _validate_related_party_evidence(
        self,
        transaction_id: str,
        finding_id: str,
        issues: list[ValidationIssue],
    ) -> None:

        feature_row = (
            self.context.get_feature_row(
                transaction_id
            )
        )

        if feature_row is None:

            issues.append(
                ValidationIssue(
                    code="MISSING_FEATURE_ROW",
                    message=(
                        "No trusted inference feature row exists "
                        "for related-party evidence."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

            return

        if not bool(
            feature_row.get(
                "is_related_party"
            )
        ):

            issues.append(
                ValidationIssue(
                    code="NOT_RELATED_PARTY",
                    message=(
                        "Evidence labels the transaction as "
                        "related-party activity, but the trusted "
                        "feature context does not."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

    # =========================================================
    # BUSINESS RULE EVIDENCE
    # =========================================================

    def _validate_business_rule_evidence(
        self,
        transaction_id: str,
        finding_id: str,
        issues: list[ValidationIssue],
    ) -> None:
        """
        For Step 5 we currently have three deterministic
        transaction flags:

            is_round_amount
            is_related_party
            is_international

        BUSINESS_RULE evidence is valid if at least one trusted
        deterministic rule fired.

        In a larger production system the evidence schema would
        include rule_id, and we would validate the exact rule.
        """

        feature_row = (
            self.context.get_feature_row(
                transaction_id
            )
        )

        if feature_row is None:

            issues.append(
                ValidationIssue(
                    code="MISSING_FEATURE_ROW",
                    message=(
                        "No trusted feature row exists for "
                        "business-rule evidence."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

            return

        rule_fired = any(
            [
                bool(
                    feature_row.get(
                        "is_round_amount"
                    )
                ),
                bool(
                    feature_row.get(
                        "is_related_party"
                    )
                ),
                bool(
                    feature_row.get(
                        "is_international"
                    )
                ),
            ]
        )

        if not rule_fired:

            issues.append(
                ValidationIssue(
                    code="NO_BUSINESS_RULE_SUPPORT",
                    message=(
                        "Evidence is labeled BUSINESS_RULE, "
                        "but none of the trusted deterministic "
                        "transaction rules fired."
                    ),
                    finding_id=finding_id,
                    transaction_id=transaction_id,
                )
            )

    # =========================================================
    # HELPERS
    # =========================================================

    @classmethod
    def _float_matches(
        cls,
        left: float,
        right: float,
    ) -> bool:

        return (
            abs(
                float(left)
                - float(right)
            )
            <= cls.ANOMALY_SCORE_TOLERANCE
        )