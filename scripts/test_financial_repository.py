from pprint import pprint

from src.financial_analysis.repository import (
    FinancialRepository,
)


def main():

    repository = FinancialRepository()

    customer_id = "CUST_000001"
    application_id = "APP_2026_00001"

    try:

        print(
            "\n========== CUSTOMER ==========\n"
        )

        pprint(
            repository.get_customer(
                customer_id
            )
        )

        print(
            "\n========== APPLICATION ==========\n"
        )

        pprint(
            repository.get_application(
                customer_id=customer_id,
                application_id=application_id,
            )
        )

        print(
            "\n========== FINANCIAL STATEMENTS ==========\n"
        )

        statements = (
            repository
            .get_financial_statements(
                customer_id
            )
        )

        for statement in statements:
            pprint(statement)
            print("-" * 60)

        print(
            "\n========== EXISTING LOANS ==========\n"
        )

        loans = (
            repository.get_existing_loans(
                customer_id
            )
        )

        for loan in loans:
            pprint(loan)
            print("-" * 60)

        print(
            "\n========== LOAN PAYMENTS ==========\n"
        )

        payments = (
            repository.get_loan_payments(
                customer_id
            )
        )

        for payment in payments:
            pprint(payment)
            print("-" * 60)

        print(
            "\n========== FINANCIAL DOCUMENTS ==========\n"
        )

        documents = (
            repository
            .get_financial_documents(
                customer_id=customer_id,
                application_id=application_id,
            )
        )

        for document in documents:
            pprint(document)
            print("-" * 60)

        print(
            "\n========== COUNTS ==========\n"
        )

        print(
            "Financial statements:",
            len(statements),
        )

        print(
            "Existing loans:",
            len(loans),
        )

        print(
            "Loan payments:",
            len(payments),
        )

        print(
            "Financial documents:",
            len(documents),
        )

    finally:
        repository.close()


if __name__ == "__main__":
    main()