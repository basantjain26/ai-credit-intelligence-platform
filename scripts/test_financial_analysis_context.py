from pprint import pprint

from src.financial_analysis.repository import (
    FinancialRepository,
)


def main():

    repository = FinancialRepository()

    customer_id = "CUST_000001"
    application_id = "APP_2026_00001"

    try:

        context = (
            repository.get_analysis_context(
                customer_id=customer_id,
                application_id=application_id,
            )
        )

        print(
            "\n========== FINANCIAL ANALYSIS CONTEXT ==========\n"
        )

        print(
            "Customer ID:",
            context.customer_id,
        )

        print(
            "Application ID:",
            context.application_id,
        )

        print(
            "\n========== CUSTOMER ==========\n"
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
            "\n========== FINANCIAL STATEMENTS ==========\n"
        )

        for statement in (
            context.financial_statements
        ):
            pprint(statement)
            print("-" * 60)

        print(
            "\n========== EXISTING LOANS ==========\n"
        )

        for loan in (
            context.existing_loans
        ):
            pprint(loan)
            print("-" * 60)

        print(
            "\n========== LOAN PAYMENTS ==========\n"
        )

        for payment in (
            context.loan_payments
        ):
            pprint(payment)
            print("-" * 60)

        print(
            "\n========== FINANCIAL DOCUMENTS ==========\n"
        )

        for document in (
            context.financial_documents
        ):
            pprint(document)
            print("-" * 60)

        print(
            "\n========== CONTEXT SUMMARY ==========\n"
        )

        print(
            "Financial statements:",
            len(
                context.financial_statements
            ),
        )

        print(
            "Existing loans:",
            len(
                context.existing_loans
            ),
        )

        print(
            "Loan payments:",
            len(
                context.loan_payments
            ),
        )

        print(
            "Financial documents:",
            len(
                context.financial_documents
            ),
        )

    finally:
        repository.close()


if __name__ == "__main__":
    main()