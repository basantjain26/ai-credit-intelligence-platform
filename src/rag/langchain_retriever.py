from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from langchain_core.retrievers import (
    BaseRetriever,
)
from pydantic import ConfigDict

from src.rag.query_embedding import (
    QueryEmbedder,
)

from src.rag.vector_search import (
    search_similar_chunks,
)


class CreditDocumentRetriever(
    BaseRetriever
):
    """
    LangChain retriever for the
    AI Credit Intelligence Platform.

    Supports two trusted retrieval scopes:

    CASE
        Retrieves borrower/application-specific
        documents.

    ENTERPRISE
        Retrieves shared enterprise knowledge
        such as lending policies.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    customer_id: str | None = None

    application_id: str | None = None

    top_k: int = 5

    document_type: str | None = None

    scope: str = "CASE"

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Any = None,
    ) -> list[Document]:

        normalized_scope = (
            self.scope.upper()
        )

        if normalized_scope not in {
            "CASE",
            "ENTERPRISE",
        }:
            raise ValueError(
                "scope must be CASE "
                "or ENTERPRISE."
            )

        if normalized_scope == "CASE":

            if not self.customer_id:
                raise ValueError(
                    "customer_id is required "
                    "for CASE scope."
                )

            if not self.application_id:
                raise ValueError(
                    "application_id is required "
                    "for CASE scope."
                )

        query_embedder = QueryEmbedder()

        query_embedding = (
            query_embedder.embed(
                query
            )
        )

        results = search_similar_chunks(
            query_embedding=query_embedding,
            customer_id=self.customer_id,
            application_id=(
                self.application_id
            ),
            top_k=self.top_k,
            document_type=(
                self.document_type
            ),
            scope=normalized_scope,
        )

        documents: list[Document] = []

        for result in results:

            stored_metadata = (
                result.metadata or {}
            )

            metadata = {
                **stored_metadata,

                # Trusted provenance fields
                # overwrite anything that may
                # exist in stored chunk metadata.
                "chunk_id": (
                    result.chunk_id
                ),
                "document_id": (
                    result.document_id
                ),
                "document_name": (
                    result.document_name
                ),
                "document_type": (
                    result.document_type
                ),
                "chunk_type": (
                    result.chunk_type
                ),
                "page_number": (
                    result.page_number
                ),
                "cosine_distance": (
                    result.cosine_distance
                ),
                "similarity_score": (
                    result.similarity_score
                ),

                # Retrieval scope itself is
                # trusted application metadata.
                "retrieval_scope": (
                    normalized_scope
                ),
            }

            if normalized_scope == "CASE":

                metadata[
                    "customer_id"
                ] = self.customer_id

                metadata[
                    "application_id"
                ] = self.application_id

            else:

                metadata[
                    "customer_id"
                ] = None

                metadata[
                    "application_id"
                ] = None

            documents.append(
                Document(
                    page_content=(
                        result.chunk_text
                    ),
                    metadata=metadata,
                )
            )

        return documents