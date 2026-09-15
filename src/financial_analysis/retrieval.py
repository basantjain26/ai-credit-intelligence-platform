from dataclasses import dataclass
from typing import Any

import psycopg2
from pgvector import Vector
from pgvector.psycopg2 import register_vector
from psycopg2.extras import RealDictCursor

from src.document_intelligence.embeddings.openai_embedder import (
    OpenAIEmbedder,
)
from src.settings import DB_CONFIG


EXPECTED_EMBEDDING_DIMENSION = 1536


@dataclass
class FinancialDocumentEvidence:
    """
    One retrieved piece of evidence from a financial document.

    The evidence retains enough provenance for the Financial
    Analysis Agent to trace a finding back to the original
    document and chunk.
    """

    chunk_id: str
    document_id: str

    document_name: str
    document_type: str

    chunk_type: str
    chunk_text: str

    page_number: int | None

    similarity: float

    fiscal_year: int | None = None

    metadata: dict[str, Any] | None = None


class FinancialDocumentRetriever:
    """
    Borrower/application-scoped semantic retrieval for
    financial documents.

    Responsibilities:
    - generate an embedding for the search query
    - convert the embedding to PostgreSQL pgvector type
    - validate embedding dimensions
    - search document_chunks using cosine distance
    - restrict retrieval to the current borrower/application
    - restrict retrieval to financial-statement documents
    - optionally filter by fiscal year
    - preserve document/page/chunk provenance

    This layer does NOT:
    - interpret retrieved evidence
    - calculate financial ratios
    - calculate financial trends
    - determine financial risk
    - decide credit policy
    - use retrieved text as authoritative without provenance
    """

    def __init__(
        self,
        embedder: OpenAIEmbedder | None = None,
    ):
        self.connection = psycopg2.connect(
            **DB_CONFIG
        )

        # Register pgvector types with psycopg2.
        #
        # This allows PostgreSQL vector values to be handled
        # correctly by the Python driver.
        register_vector(
            self.connection
        )

        self.embedder = (
            embedder
            or OpenAIEmbedder()
        )

    def search(
        self,
        query: str,
        customer_id: str,
        application_id: str,
        limit: int = 5,
        fiscal_year: int | None = None,
    ) -> list[FinancialDocumentEvidence]:
        """
        Perform borrower/application-scoped semantic search
        against financial document chunks.

        Parameters
        ----------
        query:
            Natural-language search query.

        customer_id:
            Trusted borrower/customer identifier.

        application_id:
            Trusted loan application identifier.

        limit:
            Maximum number of chunks to return.

        fiscal_year:
            Optional fiscal-year metadata filter.

        Returns
        -------
        list[FinancialDocumentEvidence]
            Ranked financial document evidence.
        """

        query = query.strip()

        if not query:
            raise ValueError(
                "Financial document search query "
                "cannot be empty"
            )

        if not customer_id:
            raise ValueError(
                "customer_id is required"
            )

        if not application_id:
            raise ValueError(
                "application_id is required"
            )

        if limit < 1 or limit > 20:
            raise ValueError(
                "limit must be between 1 and 20"
            )

        query_embedding = (
            self._embed_query(
                query
            )
        )

        sql = """
            SELECT
                dc.chunk_id,
                dc.document_id,
                d.document_name,
                d.document_type,
                dc.chunk_type,
                dc.chunk_text,
                dc.page_number,
                dc.metadata,

                1 - (
                    dc.embedding <=> %s
                ) AS similarity

            FROM document_chunks dc

            JOIN documents d
                ON d.document_id = dc.document_id

            WHERE
                d.document_type = 'FINANCIAL_STATEMENT'

                AND (
                    d.customer_id = %s
                    OR d.application_id = %s
                )

                AND dc.embedding IS NOT NULL
        """

        params: list[Any] = [
            query_embedding,
            customer_id,
            application_id,
        ]

        if fiscal_year is not None:
            sql += """
                AND (
                    dc.metadata ->> 'fiscal_year'
                ) = %s
            """

            params.append(
                str(fiscal_year)
            )

        sql += """
            ORDER BY
                dc.embedding <=> %s

            LIMIT %s
        """

        params.extend(
            [
                query_embedding,
                limit,
            ]
        )

        try:
            with self.connection.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                cursor.execute(
                    sql,
                    tuple(params),
                )

                rows = cursor.fetchall()

        except Exception:
            # A failed PostgreSQL command leaves the transaction
            # in an aborted state. Roll back so the connection
            # remains usable if the caller handles the exception.
            self.connection.rollback()
            raise

        return [
            self._to_evidence(
                row
            )
            for row in rows
        ]

    def _embed_query(
        self,
        query: str,
    ) -> Vector:
        """
        Generate the query embedding and explicitly convert it
        to pgvector.Vector.

        Without this conversion, psycopg2 may serialize a Python
        list[float] as PostgreSQL numeric[].

        pgvector cosine distance requires:

            vector <=> vector

        rather than:

            vector <=> numeric[]
        """

        embedding = None

        if hasattr(
            self.embedder,
            "embed_text",
        ):
            embedding = (
                self.embedder.embed_text(
                    query
                )
            )

        elif hasattr(
            self.embedder,
            "embed",
        ):
            embedding = (
                self.embedder.embed(
                    query
                )
            )

        else:
            raise TypeError(
                "Configured embedder does not expose "
                "embed_text() or embed()"
            )

        # Some embedding APIs return:
        #
        # [
        #     [0.01, 0.02, ...]
        # ]
        #
        # instead of:
        #
        # [0.01, 0.02, ...]
        #
        # Normalize that case here.
        if (
            isinstance(embedding, list)
            and embedding
            and isinstance(
                embedding[0],
                list,
            )
        ):
            embedding = embedding[0]

        if embedding is None:
            raise ValueError(
                "Embedding provider returned None"
            )

        try:
            embedding_dimension = len(
                embedding
            )

        except TypeError as exc:
            raise TypeError(
                "Embedding provider returned an "
                "unsupported embedding type"
            ) from exc

        if (
            embedding_dimension
            != EXPECTED_EMBEDDING_DIMENSION
        ):
            raise ValueError(
                "Unexpected embedding dimension: "
                f"expected "
                f"{EXPECTED_EMBEDDING_DIMENSION}, "
                f"got {embedding_dimension}"
            )

        # Critical fix:
        #
        # Explicitly adapt the Python embedding to pgvector's
        # Vector type so psycopg2 sends a PostgreSQL vector
        # instead of numeric[].
        return Vector(
            embedding
        )

    @staticmethod
    def _to_evidence(
        row: dict[str, Any],
    ) -> FinancialDocumentEvidence:
        """
        Convert a database row into the retrieval domain model.
        """

        metadata = (
            row.get("metadata")
            or {}
        )

        fiscal_year = None

        raw_fiscal_year = metadata.get(
            "fiscal_year"
        )

        if raw_fiscal_year is not None:
            try:
                fiscal_year = int(
                    raw_fiscal_year
                )

            except (
                TypeError,
                ValueError,
            ):
                fiscal_year = None

        similarity = row.get(
            "similarity"
        )

        if similarity is None:
            similarity_value = 0.0

        else:
            similarity_value = float(
                similarity
            )

        return FinancialDocumentEvidence(
            chunk_id=str(
                row["chunk_id"]
            ),
            document_id=str(
                row["document_id"]
            ),
            document_name=(
                row["document_name"]
            ),
            document_type=(
                row["document_type"]
            ),
            chunk_type=(
                row["chunk_type"]
            ),
            chunk_text=(
                row["chunk_text"]
            ),
            page_number=(
                row.get(
                    "page_number"
                )
            ),
            similarity=(
                similarity_value
            ),
            fiscal_year=fiscal_year,
            metadata=metadata,
        )

    def close(
        self,
    ) -> None:
        """
        Close the PostgreSQL connection.
        """

        if (
            self.connection
            and not self.connection.closed
        ):
            self.connection.close()

    def __enter__(
        self,
    ):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()