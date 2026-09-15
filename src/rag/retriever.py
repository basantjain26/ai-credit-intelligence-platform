from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import psycopg2
from dotenv import load_dotenv
from openai import OpenAI
from pgvector import Vector
from pgvector.psycopg2 import register_vector


load_dotenv()


@dataclass
class RetrievedChunk:
    """
    One chunk returned by semantic vector search.
    """

    chunk_id: str
    document_id: str
    document_name: str
    document_type: str | None
    chunk_type: str
    chunk_text: str
    page_number: int | None
    metadata: dict[str, Any]
    embedding_model: str
    cosine_distance: float
    similarity_score: float


class SemanticRetriever:
    """
    Minimal semantic retriever using:

        OpenAI embeddings
              +
        PostgreSQL / pgvector

    No LangChain is used in this baseline.
    """

    def __init__(
        self,
        embedding_model: str,
    ) -> None:

        if not embedding_model:
            raise ValueError(
                "embedding_model is required"
            )

        self.embedding_model = (
            embedding_model
        )

        self.client = OpenAI()

    # =========================================================
    # PUBLIC API
    # =========================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        customer_id: str | None = None,
        application_id: str | None = None,
    ) -> list[RetrievedChunk]:
        """
        Embed a query and retrieve the most semantically similar
        document chunks.
        """

        if not query or not query.strip():
            raise ValueError(
                "query cannot be empty"
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be at least 1"
            )

        query_embedding = (
            self._embed_query(
                query
            )
        )

        return self._vector_search(
            query_embedding=query_embedding,
            top_k=top_k,
            customer_id=customer_id,
            application_id=application_id,
        )

    # =========================================================
    # QUERY EMBEDDING
    # =========================================================

    def _embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Convert the natural-language query into a vector using
        the same embedding model used for stored chunks.
        """

        response = (
            self.client.embeddings.create(
                model=self.embedding_model,
                input=query,
            )
        )

        embedding = (
            response.data[0].embedding
        )

        if not embedding:
            raise RuntimeError(
                "Embedding API returned "
                "an empty query embedding."
            )

        return embedding

    # =========================================================
    # VECTOR SEARCH
    # =========================================================

    def _vector_search(
        self,
        query_embedding: list[float],
        top_k: int,
        customer_id: str | None,
        application_id: str | None,
    ) -> list[RetrievedChunk]:

        connection = (
            self._get_connection()
        )

        try:

            register_vector(
                connection
            )

            with connection.cursor() as cursor:

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
                        dc.embedding_model,

                        dc.embedding <=> %s
                            AS cosine_distance

                    FROM document_chunks dc

                    JOIN documents d
                        ON d.document_id
                        = dc.document_id

                    WHERE
                        dc.embedding IS NOT NULL

                        AND dc.embedding_model = %s

                        AND (
                            %s IS NULL
                            OR d.customer_id = %s
                        )

                        AND (
                            %s IS NULL
                            OR d.application_id = %s
                        )

                    ORDER BY
                        dc.embedding <=> %s

                    LIMIT %s
                """
                query_vector = Vector(query_embedding)
                cursor.execute(
                    sql,
                    (
                        query_vector,
                        self.embedding_model,

                        customer_id,
                        customer_id,

                        application_id,
                        application_id,

                        query_vector,
                        top_k,
                    ),
                )

                rows = (
                    cursor.fetchall()
                )

                results = []

                for row in rows:

                    cosine_distance = float(
                        row[9]
                    )

                    # -----------------------------------------
                    # pgvector cosine distance:
                    #
                    #     distance = 1 - cosine_similarity
                    #
                    # Therefore:
                    #
                    #     similarity = 1 - distance
                    # -----------------------------------------

                    similarity_score = (
                        1.0
                        - cosine_distance
                    )

                    results.append(
                        RetrievedChunk(
                            chunk_id=row[0],
                            document_id=row[1],
                            document_name=row[2],
                            document_type=row[3],
                            chunk_type=row[4],
                            chunk_text=row[5],
                            page_number=row[6],
                            metadata=row[7] or {},
                            embedding_model=row[8],
                            cosine_distance=(
                                cosine_distance
                            ),
                            similarity_score=(
                                similarity_score
                            ),
                        )
                    )

                return results

        finally:

            connection.close()

    # =========================================================
    # DATABASE
    # =========================================================

    @staticmethod
    def _get_connection():

        return psycopg2.connect(
            host=os.getenv(
                "POSTGRES_HOST",
                "localhost",
            ),
            port=int(
                os.getenv(
                    "POSTGRES_PORT",
                    "5434",
                )
            ),
            dbname=os.getenv(
                "POSTGRES_DB",
                "credit_intelligence",
            ),
            user=os.getenv(
                "POSTGRES_USER",
                "credit_user",
            ),
            password=os.getenv(
                "POSTGRES_PASSWORD",
                "credit_password",
            ),
        )