from dataclasses import dataclass
from typing import Any

import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extras import RealDictCursor

from src.document_intelligence.embeddings.openai_embedder import (
    OpenAIEmbedder,
)
from src.settings import DB_CONFIG


@dataclass
class BorrowerDocumentEvidence:
    chunk_id: str
    document_id: str

    document_name: str
    document_type: str | None

    chunk_type: str
    chunk_text: str

    page_number: int | None

    metadata: dict[str, Any]

    similarity: float


class BorrowerDocumentRetriever:

    def __init__(
        self,
        embedder: OpenAIEmbedder | None = None,
    ):
        self.connection = psycopg2.connect(
            **DB_CONFIG
        )

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
        application_id: str | None = None,
        limit: int = 5,
    ) -> list[BorrowerDocumentEvidence]:

        query_embedding = (
            self.embedder.embed_text(
                query
            )
        )

        rows = self._search_chunks(
            query_embedding=query_embedding,
            customer_id=customer_id,
            application_id=application_id,
            limit=limit,
        )

        return [
            BorrowerDocumentEvidence(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                document_name=row["document_name"],
                document_type=row["document_type"],
                chunk_type=row["chunk_type"],
                chunk_text=row["chunk_text"],
                page_number=row["page_number"],
                metadata=row["metadata"] or {},
                similarity=float(
                    row["similarity"]
                ),
            )
            for row in rows
        ]

    def _search_chunks(
        self,
        query_embedding: list[float],
        customer_id: str,
        application_id: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:

        if application_id:

            query = """
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
                    dc.embedding
                    <=> %s::vector
                ) AS similarity

            FROM document_chunks dc

            JOIN documents d
              ON dc.document_id = d.document_id

            WHERE
                dc.embedding IS NOT NULL

                AND (
                    d.customer_id = %s
                    OR d.application_id = %s
                )

            ORDER BY
                dc.embedding
                <=> %s::vector

            LIMIT %s;
            """

            params = (
                query_embedding,
                customer_id,
                application_id,
                query_embedding,
                limit,
            )

        else:

            query = """
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
                    dc.embedding
                    <=> %s::vector
                ) AS similarity

            FROM document_chunks dc

            JOIN documents d
              ON dc.document_id = d.document_id

            WHERE
                dc.embedding IS NOT NULL
                AND d.customer_id = %s

            ORDER BY
                dc.embedding
                <=> %s::vector

            LIMIT %s;
            """

            params = (
                query_embedding,
                customer_id,
                query_embedding,
                limit,
            )

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
        