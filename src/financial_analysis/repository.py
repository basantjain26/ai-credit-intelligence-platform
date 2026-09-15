from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from src.financial_analysis.models import FinancialAnalysisContext
from src.settings import DB_CONFIG


class FinancialRepository:
    """
    Data-access layer for borrower financial analysis.

    This repository is responsible only for retrieving financial
    source data from PostgreSQL.

    Financial calculations, reconciliations, trend analysis,
    risk signals, and LLM interpretation belong to later layers.
    """

    def __init__(self):
        self.connection = psycopg2.connect(
            **DB_CONFIG
        )

    def get_customer(
        self,
        customer_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve the borrower/customer record.
        """

        query = """
            SELECT *
            FROM customers
            WHERE customer_id = %s
        """

        return self._fetch_one(
            query,
            (customer_id,),
        )

    def get_application(
        self,
        customer_id: str,
        application_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve the current loan application.

        Both application_id and customer_id are used so that an
        application belonging to another borrower cannot accidentally
        be loaded into the current financial-analysis context.
        """

        query = """
            SELECT *
            FROM loan_applications
            WHERE application_id = %s
              AND customer_id = %s
        """

        return self._fetch_one(
            query,
            (
                application_id,
                customer_id,
            ),
        )

    def get_financial_statements(
        self,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        """
        Retrieve historical structured financial statements
        for the borrower.

        Statements are returned latest fiscal year first.
        """

        query = """
            SELECT *
            FROM financial_statements
            WHERE customer_id = %s
            ORDER BY fiscal_year DESC
        """

        return self._fetch_all(
            query,
            (customer_id,),
        )

    def get_existing_loans(
        self,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        """
        Retrieve all existing loan facilities for the borrower.
        """

        query = """
            SELECT *
            FROM loans
            WHERE customer_id = %s
            ORDER BY loan_id
        """

        return self._fetch_all(
            query,
            (customer_id,),
        )

    def get_loan_payments(
        self,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        """
        Retrieve payment history across all loans belonging
        to the borrower.
        """

        query = """
            SELECT
                lp.*
            FROM loan_payments lp
            JOIN loans l
                ON lp.loan_id = l.loan_id
            WHERE l.customer_id = %s
            ORDER BY lp.payment_date DESC
        """

        return self._fetch_all(
            query,
            (customer_id,),
        )

    def get_financial_documents(
        self,
        customer_id: str,
        application_id: str,
    ) -> list[dict[str, Any]]:
        """
        Retrieve financial-statement documents associated with
        the borrower or current application.

        At this layer we return document metadata only.
        Document content/evidence retrieval will be handled by
        the financial document retrieval layer later in Step 4.
        """

        query = """
            SELECT *
            FROM documents
            WHERE (
                customer_id = %s
                OR application_id = %s
            )
              AND document_type = 'FINANCIAL_STATEMENT'
            ORDER BY created_at DESC
        """

        return self._fetch_all(
            query,
            (
                customer_id,
                application_id,
            ),
        )

    def get_analysis_context(
        self,
        customer_id: str,
        application_id: str,
    ) -> FinancialAnalysisContext:
        """
        Build the complete raw financial-analysis context
        for one borrower/application.

        This method performs data retrieval only.

        It intentionally does not:
        - calculate financial ratios
        - normalize financial metrics
        - reconcile conflicting values
        - calculate trends
        - assign financial risk
        - invoke an LLM
        """

        customer = self.get_customer(
            customer_id
        )

        if customer is None:
            raise ValueError(
                f"Customer not found: {customer_id}"
            )

        application = self.get_application(
            customer_id=customer_id,
            application_id=application_id,
        )

        if application is None:
            raise ValueError(
                "Loan application not found "
                f"for customer={customer_id}, "
                f"application={application_id}"
            )

        financial_statements = (
            self.get_financial_statements(
                customer_id
            )
        )

        existing_loans = (
            self.get_existing_loans(
                customer_id
            )
        )

        loan_payments = (
            self.get_loan_payments(
                customer_id
            )
        )

        financial_documents = (
            self.get_financial_documents(
                customer_id=customer_id,
                application_id=application_id,
            )
        )

        return FinancialAnalysisContext(
            customer_id=customer_id,
            application_id=application_id,
            customer=customer,
            application=application,
            financial_statements=financial_statements,
            existing_loans=existing_loans,
            loan_payments=loan_payments,
            financial_documents=financial_documents,
        )

    def _fetch_one(
        self,
        query: str,
        params: tuple[Any, ...],
    ) -> dict[str, Any] | None:
        """
        Execute a query expected to return zero or one row.
        """

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
        params: tuple[Any, ...],
    ) -> list[dict[str, Any]]:
        """
        Execute a query expected to return multiple rows.
        """

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

    def close(self) -> None:
        """
        Close the PostgreSQL connection.
        """

        if (
            self.connection
            and not self.connection.closed
        ):
            self.connection.close()

    def __enter__(self):
        """
        Allow repository usage as a context manager.
        """

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()