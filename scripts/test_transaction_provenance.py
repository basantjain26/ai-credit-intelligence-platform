from src.transaction_investigation.schemas import (
    TransactionEvidence,
    TransactionFinding,
    TransactionInvestigationResult,
)
from src.transaction_investigation.tools import (
    TransactionInvestigationContext,
)
from src.transaction_investigation.validator import (
    TransactionProvenanceValidator,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def print_validation(
    name: str,
    validation,
) -> None:

    print(
        "\n"
        + "=" * 100
    )

    print(
        name
    )

    print(
        "=" * 100
    )

    print(
        "Valid:",
        validation.is_valid,
    )

    print(
        "Validated transaction IDs:",
        validation.validated_transaction_ids,
    )

    if validation.issues:

        print(
            "\nIssues:"
        )

        for issue in validation.issues:

            print(
                f"- [{issue.code}] "
                f"{issue.message}"
            )

            if issue.finding_id:

                print(
                    "  Finding:",
                    issue.finding_id,
                )

            if issue.transaction_id:

                print(
                    "  Transaction:",
                    issue.transaction_id,
                )

    else:

        print(
            "\nNo validation issues."
        )


def main() -> None:

    print(
        "\nBuilding trusted investigation context..."
    )

    context = (
        TransactionInvestigationContext.build(
            customer_id=customer_id,
            application_id=application_id,
            contamination=0.05,
        )
    )

    validator = (
        TransactionProvenanceValidator(
            context=context
        )
    )

    # =========================================================
    # GET REAL MODEL RESULT FOR XYZ
    # =========================================================

    actual_xyz_result = (
        context.get_anomaly_result(
            "TXN_000008"
        )
    )

    if actual_xyz_result is None:

        raise RuntimeError(
            "TXN_000008 does not have "
            "an inference anomaly result."
        )

    print(
        "\nTrusted XYZ model result:"
    )

    print(
        "is_anomaly:",
        actual_xyz_result.is_anomaly,
    )

    print(
        "anomaly_score:",
        actual_xyz_result.anomaly_score,
    )

    print(
        "model_version:",
        actual_xyz_result.model_version,
    )

    print(
        "feature_version:",
        actual_xyz_result.feature_version,
    )

    # =========================================================
    # TEST 1
    # VALID EVIDENCE
    # =========================================================

    valid_result = (
        TransactionInvestigationResult(
            customer_id=customer_id,

            application_id=application_id,

            overall_transaction_risk=(
                "ELEVATED"
            ),

            summary=(
                "Transaction activity contains "
                "material items requiring analyst review."
            ),

            findings=[
                TransactionFinding(
                    finding_id="FINDING_001",

                    title=(
                        "Large related-party transfer"
                    ),

                    severity="HIGH",

                    explanation=(
                        "A large debit was made to "
                        "a known related party."
                    ),

                    credit_risk_relevance=(
                        "The transaction may require "
                        "verification of business purpose "
                        "and related-party exposure."
                    ),

                    transaction_ids=[
                        "TXN_000008"
                    ],

                    evidence=[
                        TransactionEvidence(
                            evidence_type=(
                                "TRANSACTION"
                            ),

                            transaction_id=(
                                "TXN_000008"
                            ),

                            description=(
                                "Source bank transaction."
                            ),
                        ),

                        TransactionEvidence(
                            evidence_type=(
                                "RELATED_PARTY"
                            ),

                            transaction_id=(
                                "TXN_000008"
                            ),

                            description=(
                                "Counterparty is identified "
                                "as a related party."
                            ),
                        ),
                    ],

                    analyst_follow_up=(
                        "Obtain supporting documentation "
                        "for the transfer."
                    ),
                )
            ],

            transactions_requiring_review=[
                "TXN_000008"
            ],

            additional_information_required=[
                (
                    "Supporting documentation for "
                    "the XYZ Holdings transfer."
                )
            ],

            limitations=[],
        )
    )

    # ---------------------------------------------------------
    # Add ML evidence only if the actual model classified XYZ
    # as anomalous.
    #
    # We never hardcode expected model behavior into the test.
    # ---------------------------------------------------------

    if actual_xyz_result.is_anomaly:

        valid_result.findings[
            0
        ].evidence.append(
            TransactionEvidence(
                evidence_type=(
                    "ML_ANOMALY"
                ),

                transaction_id=(
                    "TXN_000008"
                ),

                description=(
                    "Isolation Forest classified "
                    "the transaction as anomalous."
                ),

                anomaly_score=(
                    actual_xyz_result
                    .anomaly_score
                ),

                model_version=(
                    actual_xyz_result
                    .model_version
                ),

                feature_version=(
                    actual_xyz_result
                    .feature_version
                ),
            )
        )

    validation = validator.validate(
        valid_result
    )

    print_validation(
        "TEST 1 — VALID PROVENANCE",
        validation,
    )

    if not validation.is_valid:

        raise AssertionError(
            "Valid provenance test failed."
        )

    # =========================================================
    # TEST 2
    # FAKE TRANSACTION ID
    # =========================================================

    fake_transaction_result = (
        valid_result.model_copy(
            deep=True
        )
    )

    fake_transaction_result.findings[
        0
    ].transaction_ids = [
        "TXN_FAKE_999"
    ]

    fake_transaction_result.findings[
        0
    ].evidence[
        0
    ].transaction_id = (
        "TXN_FAKE_999"
    )

    validation = validator.validate(
        fake_transaction_result
    )

    print_validation(
        "TEST 2 — FAKE TRANSACTION",
        validation,
    )

    if validation.is_valid:

        raise AssertionError(
            "Fake transaction should "
            "have failed validation."
        )

    # =========================================================
    # TEST 3
    # FAKE ANOMALY SCORE
    #
    # Only meaningful when XYZ is actually an ML anomaly.
    # =========================================================

    if actual_xyz_result.is_anomaly:

        fake_score_result = (
            valid_result.model_copy(
                deep=True
            )
        )

        ml_evidence = next(
            evidence
            for evidence
            in fake_score_result
            .findings[0]
            .evidence
            if (
                evidence.evidence_type
                == "ML_ANOMALY"
            )
        )

        ml_evidence.anomaly_score = (
            actual_xyz_result.anomaly_score
            + 0.50
        )

        validation = (
            validator.validate(
                fake_score_result
            )
        )

        print_validation(
            "TEST 3 — FAKE ANOMALY SCORE",
            validation,
        )

        if validation.is_valid:

            raise AssertionError(
                "Fake anomaly score should "
                "have failed validation."
            )

    # =========================================================
    # TEST 4
    # FALSE RELATED-PARTY CLAIM
    #
    # Find a current transaction that is NOT related party.
    # =========================================================

    non_related_transaction_id = None

    for row in (
        context.inference_features
    ):

        if not bool(
            row.get(
                "is_related_party"
            )
        ):

            non_related_transaction_id = (
                row["transaction_id"]
            )

            break

    if non_related_transaction_id:

        false_related_result = (
            TransactionInvestigationResult(
                customer_id=customer_id,

                application_id=application_id,

                overall_transaction_risk=(
                    "MODERATE"
                ),

                summary=(
                    "Test result."
                ),

                findings=[
                    TransactionFinding(
                        finding_id=(
                            "FINDING_FALSE_RP"
                        ),

                        title=(
                            "False related-party claim"
                        ),

                        severity="MEDIUM",

                        explanation=(
                            "Test evidence."
                        ),

                        credit_risk_relevance=(
                            "Test evidence."
                        ),

                        transaction_ids=[
                            non_related_transaction_id
                        ],

                        evidence=[
                            TransactionEvidence(
                                evidence_type=(
                                    "RELATED_PARTY"
                                ),

                                transaction_id=(
                                    non_related_transaction_id
                                ),

                                description=(
                                    "Incorrectly claims "
                                    "related-party status."
                                ),
                            )
                        ],
                    )
                ],

                transactions_requiring_review=[],

                additional_information_required=[],

                limitations=[],
            )
        )

        validation = (
            validator.validate(
                false_related_result
            )
        )

        print_validation(
            "TEST 4 — FALSE RELATED-PARTY CLAIM",
            validation,
        )

        if validation.is_valid:

            raise AssertionError(
                "False related-party evidence "
                "should have failed validation."
            )

    print(
        "\n"
        + "=" * 100
    )

    print(
        "STEP 5.4 PROVENANCE TESTS PASSED"
    )

    print(
        "=" * 100
    )


if __name__ == "__main__":
    main()