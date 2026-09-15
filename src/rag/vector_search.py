from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import psycopg2
from dotenv import load_dotenv
from pgvector import Vector
from pgvector.psycopg2 import register_vector


load_dotenv()


@dataclass
class SearchResult:
    """
    One document chunk returned by semantic vector search.
    """

    chunk_id: str
    document_id: str
    document_name: str
    document_type: str | None
    chunk_type: str
    chunk_text: str
    page_number: int | None
    metadata: dict[str, Any]
    cosine_distance: float
    similarity_score: float


def search_similar_chunks(
    query_embedding: list[float],
    customer_id: str,
    application_id: str,
    top_k: int = 5,
    document_type: str | None = None,
) -> list[SearchResult]:
    """
    Retrieve the most semantically similar document chunks
    for a specific customer/application.

    Retrieval combines:

        1. Customer/application scope
        2. Optional document-type filtering
        3. Cosine vector similarity

    Parameters
    ----------
    query_embedding:
        Embedding generated from the user's query.

    customer_id:
        Trusted customer scope.

    application_id:
        Trusted loan-application scope.

    top_k:
        Maximum number of chunks to return.

    document_type:
        Optional business metadata filter, for example:

            FINANCIAL_STATEMENT
            BORROWER_PROFILE
            EXPOSURE_SCHEDULE

        If None, all document types within the case are eligible.
    """

    # =========================================================
    # INPUT VALIDATION
    # =========================================================

    if not query_embedding:
        raise ValueError(
            "query_embedding cannot be empty."
        )

    if not customer_id:
        raise ValueError(
            "customer_id cannot be empty."
        )

    if not application_id:
        raise ValueError(
            "application_id cannot be empty."
        )

    if top_k < 1:
        raise ValueError(
            "top_k must be at least 1."
        )

    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    connection = psycopg2.connect(
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

    try:

        # -----------------------------------------------------
        # Register PostgreSQL pgvector type with psycopg2.
        # -----------------------------------------------------

        register_vector(
            connection
        )

        # -----------------------------------------------------
        # IMPORTANT:
        #
        # OpenAI returns list[float].
        #
        # Without explicit Vector conversion, psycopg2 may send
        # the Python list as PostgreSQL numeric[].
        #
        # pgvector cosine comparison requires:
        #
        #     vector <=> vector
        #
        # not:
        #
        #     vector <=> numeric[]
        # -----------------------------------------------------

        query_vector = Vector(
            query_embedding
        )

        # =====================================================
        # VECTOR SEARCH
        # =====================================================

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

                dc.embedding <=> %s
                    AS cosine_distance

            FROM document_chunks dc

            JOIN documents d
                ON d.document_id = dc.document_id

            WHERE
                dc.embedding IS NOT NULL

                AND d.customer_id = %s

                AND d.application_id = %s

                AND (
                    %s IS NULL
                    OR d.document_type = %s
                )

            ORDER BY
                dc.embedding <=> %s

            LIMIT %s;
        """

        with connection.cursor() as cursor:

            cursor.execute(
                sql,
                (
                    # SELECT cosine distance
                    query_vector,

                    # Trusted case scope
                    customer_id,
                    application_id,

                    # Optional metadata filter
                    document_type,
                    document_type,

                    # ORDER BY cosine distance
                    query_vector,

                    # Top-K
                    top_k,
                ),
            )

            rows = cursor.fetchall()

        # =====================================================
        # MAP DATABASE RESULTS
        # =====================================================

        results: list[SearchResult] = []

        for row in rows:

            cosine_distance = float(
                row[8]
            )

            # -------------------------------------------------
            # pgvector <=> returns cosine DISTANCE.
            #
            # Smaller distance = closer vectors.
            #
            # For easier interpretation:
            #
            # similarity = 1 - cosine_distance
            #
            # NOTE:
            # This is NOT a probability.
            # -------------------------------------------------

            similarity_score = (
                1.0 - cosine_distance
            )

            result = SearchResult(
                chunk_id=row[0],
                document_id=row[1],
                document_name=row[2],
                document_type=row[3],
                chunk_type=row[4],
                chunk_text=row[5],
                page_number=row[6],
                metadata=row[7] or {},
                cosine_distance=cosine_distance,
                similarity_score=similarity_score,
            )

            results.append(
                result
            )

        return results

    finally:

        connection.close()