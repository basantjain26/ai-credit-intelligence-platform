from pprint import pprint

from src.borrower_intelligence.repository import (
    BorrowerRepository,
)

from src.borrower_intelligence.signals import (
    BorrowerSignalEngine,
)


def main():

    repository = (
        BorrowerRepository()
    )

    try:

        customer_id = "CUST_000001"
        application_id = "APP_2026_00001"

        context = (
            repository.get_case_context(
                customer_id=customer_id,
                application_id=application_id,
            )
        )

        engine = (
            BorrowerSignalEngine()
        )

        signals = engine.calculate(
            context
        )

        print(
            "\n"
            "========== BORROWER SIGNALS =========="
            "\n"
        )

        pprint(signals)

        print(
            "\n========== EXPOSURE =========="
        )

        print(
            "Existing exposure:",
            signals.existing_exposure,
        )

        print(
            "Requested amount:",
            signals.requested_amount,
        )

        print(
            "Potential post-loan exposure:",
            signals.potential_post_loan_exposure,
        )

        print(
            "\n========== RELATIONSHIP =========="
        )

        print(
            "Relationship years:",
            signals.relationship_years,
        )

        print(
            "Directors:",
            signals.director_count,
        )

        print(
            "Related parties:",
            signals.related_party_count,
        )

        print(
            "High-risk related parties:",
            signals.high_risk_related_party_count,
        )

        print(
            "\n========== REVENUE CHECK =========="
        )

        print(
            "Financial year:",
            signals.latest_financial_year,
        )

        print(
            "Declared revenue:",
            signals.declared_revenue,
        )

        print(
            "Audited revenue:",
            signals.audited_revenue,
        )

        print(
            "Difference:",
            signals.revenue_difference,
        )

        print(
            "Difference %:",
            signals.revenue_difference_pct,
        )

        print(
            "Mismatch:",
            signals.revenue_mismatch,
        )

        print(
            "\n========== MISSING INFO =========="
        )

        for item in (
            signals.missing_information
        ):
            print(
                "-",
                item,
            )

    finally:

        repository.close()


if __name__ == "__main__":
    main()