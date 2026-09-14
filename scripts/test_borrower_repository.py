from pprint import pprint

from src.borrower_intelligence.repository import (
    BorrowerRepository,
)


def main():

    repository = BorrowerRepository()

    try:

        customer_id = "CUST_000001"
        application_id = "APP_2026_00001"

        context = repository.get_case_context(
            customer_id=customer_id,
            application_id=application_id,
        )

        print(
            "\n========== BORROWER ==========\n"
        )

        pprint(
            context.customer
        )

        print(
            "\n========== APPLICATION ==========\n"
        )

        pprint(
            context.application
        )

        print(
            "\n========== DIRECTORS ==========\n"
        )

        pprint(
            context.directors
        )

        print(
            "\n========== RELATED PARTIES ==========\n"
        )

        pprint(
            context.related_parties
        )

        print(
            "\n========== LOANS ==========\n"
        )

        pprint(
            context.loans
        )

        print(
            "\n========== FINANCIALS ==========\n"
        )

        pprint(
            context.financial_statements
        )

        print(
            "\n========== DOCUMENTS ==========\n"
        )

        pprint(
            context.documents
        )

        print(
            "\n========== SUMMARY ==========\n"
        )

        print(
            "Directors:",
            len(context.directors),
        )

        print(
            "Related parties:",
            len(context.related_parties),
        )

        print(
            "Loans:",
            len(context.loans),
        )

        print(
            "Loan payments:",
            len(context.loan_payments),
        )

        print(
            "Bank accounts:",
            len(context.bank_accounts),
        )

        print(
            "Financial statements:",
            len(
                context.financial_statements
            ),
        )

        print(
            "Documents:",
            len(context.documents),
        )

    finally:

        repository.close()


if __name__ == "__main__":
    main()