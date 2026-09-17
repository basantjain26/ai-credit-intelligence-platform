from src.external_research.research_agent import (
    ExternalResearchAgent,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def main() -> None:

    agent = ExternalResearchAgent()

    print()
    print("=" * 80)
    print("EXTERNAL CREDIT RESEARCH")
    print("=" * 80)

    print()
    print(f"Customer ID    : {customer_id}")
    print(f"Application ID : {application_id}")

    result = agent.research(
        borrower_name=(
            "ABC Manufacturing Pvt Ltd"
        ),
        industry=(
            "Auto components and "
            "industrial manufacturing"
        ),
        location=None,
        directors=[
            "Rajesh Sharma",
        ],
    )

    print()
    print("=" * 80)
    print("RESEARCH SUMMARY")
    print("=" * 80)

    print()
    print(result.research_summary)

    print()
    print("=" * 80)
    print("FINDINGS")
    print("=" * 80)

    if not result.findings:
        print()
        print(
            "No sufficiently supported "
            "external findings returned."
        )

    for index, finding in enumerate(
        result.findings,
        start=1,
    ):

        print()
        print(f"Finding {index}")
        print("-" * 80)

        print(
            f"Finding        : "
            f"{finding.finding}"
        )

        print(
            f"Entity match   : "
            f"{finding.entity_match}"
        )

        print(
            f"Risk relevance : "
            f"{finding.risk_relevance}"
        )

        print(
            f"Evidence       : "
            f"{finding.evidence}"
        )

        print(
            f"Source         : "
            f"{finding.source_title}"
        )

        print(
            f"URL            : "
            f"{finding.source_url}"
        )

    print()
    print("=" * 80)
    print("UNRESOLVED ENTITY MATCHES")
    print("=" * 80)

    if result.unresolved_entity_matches:

        for item in (
            result.unresolved_entity_matches
        ):
            print(f"- {item}")

    else:
        print(
            "No unresolved entity matches."
        )

    print()
    print("=" * 80)
    print("RESEARCH LIMITATIONS")
    print("=" * 80)

    if result.research_limitations:

        for limitation in (
            result.research_limitations
        ):
            print(f"- {limitation}")

    else:
        print(
            "No research limitations reported."
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()