from src.policy_intelligence.models import (
    PolicyFacts,
)

from src.policy_intelligence.policy_agent import (
    PolicyAgent,
)


def main() -> None:

    facts = PolicyFacts(
        dscr=1.12,
        debt_to_ebitda=125 / 95,
        audited_financials_available=True,
        banking_relationship_years=7.0,
        material_related_party_transaction=True,
        unusual_transaction_detected=True,
    )

    agent = PolicyAgent()

    result = agent.evaluate(
        facts
    )

    print()
    print("=" * 80)
    print("POLICY AGENT ASSESSMENT")
    print("=" * 80)

    print()
    print("SUMMARY")
    print(result.summary)

    print()
    print("FINDINGS")

    for finding in result.findings:

        print()
        print(
            f"{finding.policy_id}: "
            f"{finding.status}"
        )

        print(
            finding.finding
        )

        print(
            "Evidence: "
            + ", ".join(
                finding.evidence_chunk_ids
            )
        )

    print()
    print(
        "Requires Credit Officer Review: "
        f"{result.requires_credit_officer_review}"
    )

    print()

    print("Review Reasons:")

    for reason in result.review_reasons:
        print(
            f"- {reason}"
        )


if __name__ == "__main__":
    main()