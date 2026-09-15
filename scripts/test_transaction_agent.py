import json

from pydantic import ValidationError

from src.transaction_investigation.agent import (
    TransactionInvestigationAgent,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def main() -> None:

    print(
        "\n"
        + "=" * 100
    )

    print(
        "STEP 5.3 — TRANSACTION "
        "INVESTIGATION AGENT"
    )

    print(
        "=" * 100
    )

    # =========================================================
    # BUILD AGENT
    # =========================================================

    print(
        "\nBuilding trusted transaction "
        "investigation context..."
    )

    agent = (
        TransactionInvestigationAgent(
            customer_id=customer_id,
            application_id=application_id,

            contamination=0.05,

            max_tool_rounds=10,

            # Keep True while learning so that we can observe
            # the model's tool-selection behavior.
            log_tool_calls=True,
        )
    )

    print(
        "Transaction Investigation "
        "Agent ready."
    )

    # =========================================================
    # SHOW PREPARED ML CONTEXT
    # =========================================================

    print(
        "\n"
        + "-" * 100
    )

    print(
        "PREPARED INVESTIGATION CONTEXT"
    )

    print(
        "-" * 100
    )

    print(
        "Customer ID:",
        agent.customer_id,
    )

    print(
        "Application ID:",
        agent.application_id,
    )

    print(
        "Historical training transactions:",
        len(
            agent.context
            .training_transactions
        ),
    )

    print(
        "Inference transactions:",
        len(
            agent.context
            .inference_transactions
        ),
    )

    print(
        "Feature version:",
        agent.context
        .feature_baseline
        .feature_version,
    )

    print(
        "Model version:",
        agent.context.model_version,
    )

    # =========================================================
    # INVESTIGATION QUESTION
    # =========================================================

    question = """
Investigate this borrower's recent bank transaction activity for
credit-risk concerns.

Focus on:

- statistically unusual transaction behavior,
- unusually large transactions,
- new or rare counterparties,
- related-party activity,
- international transactions,
- transaction velocity,
- unusual counterparty concentration,
- combinations of multiple risk indicators,
- anything requiring follow-up by the credit analyst.

Use the transaction evidence and ML anomaly evidence available through
the tools.

Do not assume that an anomaly is fraud.

Distinguish statistical anomaly evidence from deterministic
business-rule evidence and contextual interpretation.
""".strip()

    print(
        "\n"
        + "=" * 100
    )

    print(
        "STARTING AGENT INVESTIGATION"
    )

    print(
        "=" * 100
    )

    print(
        "\nQuestion:\n"
    )

    print(
        question
    )

    # =========================================================
    # RUN AGENT
    # =========================================================

    try:

        result = (
            agent.investigate(
                question
            )
        )

    except ValidationError as exc:

        print(
            "\nStructured output "
            "validation failed."
        )

        print(
            exc
        )

        raise

    except Exception as exc:

        print(
            "\nTransaction investigation "
            "failed."
        )

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        raise

    # =========================================================
    # STRUCTURED RESULT
    # =========================================================

    print(
        "\n"
        + "=" * 100
    )

    print(
        "STRUCTURED TRANSACTION "
        "INVESTIGATION RESULT"
    )

    print(
        "=" * 100
    )

    print(
        json.dumps(
            result.model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )

    # =========================================================
    # HUMAN-READABLE SUMMARY
    # =========================================================

    print(
        "\n"
        + "=" * 100
    )

    print(
        "INVESTIGATION SUMMARY"
    )

    print(
        "=" * 100
    )

    print(
        "\nOverall transaction risk:"
    )

    print(
        result.overall_transaction_risk
    )

    print(
        "\nSummary:"
    )

    print(
        result.summary
    )

    # =========================================================
    # FINDINGS
    # =========================================================

    print(
        "\n"
        + "=" * 100
    )

    print(
        "MATERIAL FINDINGS"
    )

    print(
        "=" * 100
    )

    if not result.findings:

        print(
            "\nNo material findings "
            "were returned."
        )

    for index, finding in enumerate(
        result.findings,
        start=1,
    ):

        print(
            f"\nFinding {index}"
        )

        print(
            "-" * 60
        )

        print(
            "Finding ID:",
            finding.finding_id,
        )

        print(
            "Title:",
            finding.title,
        )

        print(
            "Severity:",
            finding.severity,
        )

        print(
            "Transaction IDs:",
            (
                ", ".join(
                    finding.transaction_ids
                )
                if finding.transaction_ids
                else "None"
            ),
        )

        print(
            "\nExplanation:"
        )

        print(
            finding.explanation
        )

        print(
            "\nCredit-risk relevance:"
        )

        print(
            finding.credit_risk_relevance
        )

        # -----------------------------------------------------
        # EVIDENCE
        # -----------------------------------------------------

        if finding.evidence:

            print(
                "\nEvidence:"
            )

            for evidence_index, evidence in enumerate(
                finding.evidence,
                start=1,
            ):

                print(
                    f"\n  Evidence "
                    f"{evidence_index}"
                )

                print(
                    "  Type:",
                    evidence.evidence_type,
                )

                print(
                    "  Transaction ID:",
                    evidence.transaction_id,
                )

                print(
                    "  Description:",
                    evidence.description,
                )

                if (
                    evidence.anomaly_score
                    is not None
                ):

                    print(
                        "  Anomaly score:",
                        evidence.anomaly_score,
                    )

                if (
                    evidence.model_version
                    is not None
                ):

                    print(
                        "  Model version:",
                        evidence.model_version,
                    )

                if (
                    evidence.feature_version
                    is not None
                ):

                    print(
                        "  Feature version:",
                        evidence.feature_version,
                    )

        # -----------------------------------------------------
        # FOLLOW-UP
        # -----------------------------------------------------

        if (
            finding.analyst_follow_up
        ):

            print(
                "\nAnalyst follow-up:"
            )

            print(
                finding.analyst_follow_up
            )

    # =========================================================
    # REVIEW QUEUE
    # =========================================================

    print(
        "\n"
        + "=" * 100
    )

    print(
        "TRANSACTIONS REQUIRING REVIEW"
    )

    print(
        "=" * 100
    )

    if (
        result.transactions_requiring_review
    ):

        for transaction_id in (
            result.transactions_requiring_review
        ):

            print(
                "-",
                transaction_id,
            )

    else:

        print(
            "None"
        )

    # =========================================================
    # ADDITIONAL INFORMATION
    # =========================================================

    print(
        "\n"
        + "=" * 100
    )

    print(
        "ADDITIONAL INFORMATION REQUIRED"
    )

    print(
        "=" * 100
    )

    if (
        result.additional_information_required
    ):

        for item in (
            result.additional_information_required
        ):

            print(
                "-",
                item,
            )

    else:

        print(
            "None"
        )

    # =========================================================
    # LIMITATIONS
    # =========================================================

    print(
        "\n"
        + "=" * 100
    )

    print(
        "LIMITATIONS"
    )

    print(
        "=" * 100
    )

    if result.limitations:

        for limitation in (
            result.limitations
        ):

            print(
                "-",
                limitation,
            )

    else:

        print(
            "None"
        )

    print(
        "\n"
        + "=" * 100
    )

    print(
        "STEP 5.3 TEST COMPLETED"
    )

    print(
        "=" * 100
    )


if __name__ == "__main__":
    main()