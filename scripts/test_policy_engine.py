from src.policy_intelligence.models import (
    PolicyFacts,
)

from src.policy_intelligence.policy_engine import (
    LendingPolicyEngine,
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

    engine = LendingPolicyEngine()

    result = engine.evaluate(
        facts
    )

    print()
    print("=" * 80)
    print("LENDING POLICY EVALUATION")
    print("=" * 80)

    for evaluation in result.evaluations:

        print()
        print(
            f"{evaluation.policy_id} "
            f"- {evaluation.policy_name}"
        )

        print(
            f"Status      : "
            f"{evaluation.status.value}"
        )

        print(
            f"Actual      : "
            f"{evaluation.actual_value}"
        )

        print(
            f"Requirement : "
            f"{evaluation.requirement}"
        )

        print(
            f"Reason      : "
            f"{evaluation.reason}"
        )

    print()
    print("=" * 80)

    print(
        f"Violations      : "
        f"{len(result.violations)}"
    )

    print(
        f"Enhanced Reviews: "
        f"{len(result.enhanced_reviews)}"
    )


if __name__ == "__main__":
    main()