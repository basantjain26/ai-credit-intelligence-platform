from dataclasses import asdict
from decimal import Decimal
from typing import Any

from src.borrower_intelligence.repository import (
    BorrowerRepository,
)
from src.borrower_intelligence.retrieval import (
    BorrowerDocumentRetriever,
)
from src.borrower_intelligence.signals import (
    BorrowerSignalEngine,
)


class BorrowerTools:

    def __init__(
        self,
        customer_id: str,
        application_id: str,
    ):
        self.customer_id = customer_id
        self.application_id = application_id

        self.repository = BorrowerRepository()

        self.signal_engine = (
            BorrowerSignalEngine()
        )

        self.document_retriever = (
            BorrowerDocumentRetriever()
        )

    def get_borrower_profile(
        self,
    ) -> dict[str, Any]:

        customer = (
            self.repository.get_customer(
                self.customer_id
            )
        )

        return self._serialize(
            customer
        )

    def get_application_details(
        self,
    ) -> dict[str, Any]:

        application = (
            self.repository.get_application(
                application_id=(
                    self.application_id
                ),
                customer_id=(
                    self.customer_id
                ),
            )
        )

        return self._serialize(
            application
        )

    def get_existing_exposure(
        self,
    ) -> dict[str, Any]:

        loans = (
            self.repository.get_loans(
                self.customer_id
            )
        )

        context = (
            self.repository.get_case_context(
                customer_id=self.customer_id,
                application_id=(
                    self.application_id
                ),
            )
        )

        signals = (
            self.signal_engine.calculate(
                context
            )
        )

        return self._serialize(
            {
                "existing_exposure": (
                    signals.existing_exposure
                ),
                "requested_amount": (
                    signals.requested_amount
                ),
                "potential_post_loan_exposure": (
                    signals.potential_post_loan_exposure
                ),
                "loan_count": (
                    signals.loan_count
                ),
                "loans": loans,
            }
        )

    def get_directors(
        self,
    ) -> list[dict[str, Any]]:

        directors = (
            self.repository.get_directors(
                self.customer_id
            )
        )

        return self._serialize(
            directors
        )

    def get_related_parties(
        self,
    ) -> list[dict[str, Any]]:

        related_parties = (
            self.repository.get_related_parties(
                self.customer_id
            )
        )

        return self._serialize(
            related_parties
        )

    def get_borrower_signals(
        self,
    ) -> dict[str, Any]:

        context = (
            self.repository.get_case_context(
                customer_id=self.customer_id,
                application_id=(
                    self.application_id
                ),
            )
        )

        signals = (
            self.signal_engine.calculate(
                context
            )
        )

        return self._serialize(
            asdict(signals)
        )

    def search_borrower_documents(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:

        results = (
            self.document_retriever.search(
                query=query,
                customer_id=self.customer_id,
                application_id=(
                    self.application_id
                ),
                limit=limit,
            )
        )

        return [
            self._serialize(
                asdict(result)
            )
            for result in results
        ]

    def close(
        self,
    ) -> None:

        self.repository.close()

        self.document_retriever.close()
        
    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:

        arguments = arguments or {}

        if tool_name == "get_borrower_profile":
            return self.get_borrower_profile()

        if tool_name == "get_application_details":
            return self.get_application_details()

        if tool_name == "get_existing_exposure":
            return self.get_existing_exposure()

        if tool_name == "get_directors":
            return self.get_directors()

        if tool_name == "get_related_parties":
            return self.get_related_parties()

        if tool_name == "get_borrower_signals":
            return self.get_borrower_signals()

        if tool_name == "search_borrower_documents":

            return self.search_borrower_documents(
                query=arguments["query"],
                limit=arguments.get(
                    "limit",
                    5,
                ),
            )

        raise ValueError(
            f"Unknown borrower tool: {tool_name}"
        )

    @classmethod
    def _serialize(
        cls,
        value: Any,
    ) -> Any:

        if isinstance(
            value,
            Decimal,
        ):
            return str(value)

        if isinstance(
            value,
            dict,
        ):
            return {
                key: cls._serialize(item)
                for key, item
                in value.items()
            }

        if isinstance(
            value,
            list,
        ):
            return [
                cls._serialize(item)
                for item in value
            ]

        if isinstance(
            value,
            tuple,
        ):
            return [
                cls._serialize(item)
                for item in value
            ]

        if hasattr(
            value,
            "isoformat",
        ):
            return value.isoformat()

        return value