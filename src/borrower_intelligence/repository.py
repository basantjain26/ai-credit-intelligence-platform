import psycopg2
from psycopg2.extras import RealDictCursor

from src.settings import DB_CONFIG

from src.borrower_intelligence.models import (
    BorrowerCaseContext,
)


class BorrowerRepository:

    def __init__(self):
        self.connection = psycopg2.connect(
            **DB_CONFIG
        )

    def get_customer(
        self,
        customer_id: str,
    ) -> dict:

        query = """
        SELECT *
        FROM customers
        WHERE customer_id = %s;
        """

        row = self._fetch_one(
            query,
            (customer_id,),
        )

        if row is None:
            raise ValueError(
                f"Customer not found: {customer_id}"
            )

        return row

    def get_application(
        self,
        application_id: str,
        customer_id: str,
    ) -> dict:

        query = """
        SELECT *
        FROM loan_applications
        WHERE application_id = %s
          AND customer_id = %s;
        """

        row = self._fetch_one(
            query,
            (
                application_id,
                customer_id,
            ),
        )

        if row is None:
            raise ValueError(
                "Loan application not found: "
                f"{application_id}"
            )

        return row

    def get_directors(
        self,
        customer_id: str,
    ) -> list[dict]:

        query = """
        SELECT *
        FROM company_directors
        WHERE customer_id = %s
        ORDER BY director_id;
        """

        return self._fetch_all(
            query,
            (customer_id,),
        )

    def get_related_parties(
        self,
        customer_id: str,
    ) -> list[dict]:

        query = """
        SELECT *
        FROM related_parties
        WHERE customer_id = %s
        ORDER BY related_party_id;
        """

        return self._fetch_all(
            query,
            (customer_id,),
        )

    def get_loans(
        self,
        customer_id: str,
    ) -> list[dict]:

        query = """
        SELECT *
        FROM loans
        WHERE customer_id = %s
        ORDER BY loan_id;
        """

        return self._fetch_all(
            query,
            (customer_id,),
        )

    def get_loan_payments(
        self,
        customer_id: str,
    ) -> list[dict]:

        query = """
        SELECT lp.*
        FROM loan_payments lp
        JOIN loans l
          ON lp.loan_id = l.loan_id
        WHERE l.customer_id = %s
        ORDER BY lp.loan_id;
        """

        return self._fetch_all(
            query,
            (customer_id,),
        )

    def get_bank_accounts(
        self,
        customer_id: str,
    ) -> list[dict]:

        query = """
        SELECT *
        FROM bank_accounts
        WHERE customer_id = %s
        ORDER BY account_id;
        """

        return self._fetch_all(
            query,
            (customer_id,),
        )

    def get_financial_statements(
        self,
        customer_id: str,
    ) -> list[dict]:

        query = """
        SELECT *
        FROM financial_statements
        WHERE customer_id = %s
        ORDER BY fiscal_year DESC;
        """

        return self._fetch_all(
            query,
            (customer_id,),
        )

    def get_documents(
        self,
        customer_id: str,
        application_id: str,
    ) -> list[dict]:

        query = """
        SELECT *
        FROM documents
        WHERE customer_id = %s
           OR application_id = %s
        ORDER BY created_at;
        """

        return self._fetch_all(
            query,
            (
                customer_id,
                application_id,
            ),
        )

    def get_case_context(
        self,
        customer_id: str,
        application_id: str,
    ) -> BorrowerCaseContext:

        customer = self.get_customer(
            customer_id
        )

        application = self.get_application(
            application_id=application_id,
            customer_id=customer_id,
        )

        directors = self.get_directors(
            customer_id
        )

        related_parties = (
            self.get_related_parties(
                customer_id
            )
        )

        loans = self.get_loans(
            customer_id
        )

        loan_payments = (
            self.get_loan_payments(
                customer_id
            )
        )

        bank_accounts = (
            self.get_bank_accounts(
                customer_id
            )
        )

        financial_statements = (
            self.get_financial_statements(
                customer_id
            )
        )

        documents = self.get_documents(
            customer_id=customer_id,
            application_id=application_id,
        )

        return BorrowerCaseContext(
            customer_id=customer_id,
            application_id=application_id,
            customer=customer,
            application=application,
            directors=directors,
            related_parties=related_parties,
            loans=loans,
            loan_payments=loan_payments,
            bank_accounts=bank_accounts,
            financial_statements=(
                financial_statements
            ),
            documents=documents,
        )

    def _fetch_one(
        self,
        query: str,
        params: tuple,
    ) -> dict | None:

        with self.connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                query,
                params,
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def _fetch_all(
        self,
        query: str,
        params: tuple,
    ) -> list[dict]:

        with self.connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                query,
                params,
            )

            rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def close(
        self,
    ) -> None:

        self.connection.close()