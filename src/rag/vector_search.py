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
    customer_id: str | None,
    application_id: str | None,
    top_k: int = 5,
    document_type: str | None = None,
    scope: str = "CASE",
) -> list[SearchResult]:

    if not query_embedding:
        raise ValueError(
            "query_embedding cannot be empty."
        )

    if top_k < 1:
        raise ValueError(
            "top_k must be at least 1."
        )

    normalized_scope = scope.upper()

    if normalized_scope not in {
        "CASE",
        "ENTERPRISE",
    }:
        raise ValueError(
            "scope must be CASE or ENTERPRISE."
        )

    if normalized_scope == "CASE":

        if not customer_id:
            raise ValueError(
                "customer_id is required "
                "for CASE scope."
            )

        if not application_id:
            raise ValueError(
                "application_id is required "
                "for CASE scope."
            )

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

        register_vector(connection)

        query_vector = Vector(
            query_embedding
        )

        if normalized_scope == "CASE":

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
                    ON d.document_id =
                       dc.document_id
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

            parameters = (
                query_vector,
                customer_id,
                application_id,
                document_type,
                document_type,
                query_vector,
                top_k,
            )

        else:

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
                    ON d.document_id =
                       dc.document_id
                WHERE
                    dc.embedding IS NOT NULL
                    AND d.customer_id IS NULL
                    AND d.application_id IS NULL
                    AND (
                        %s IS NULL
                        OR d.document_type = %s
                    )
                ORDER BY
                    dc.embedding <=> %s
                LIMIT %s;
            """

            parameters = (
                query_vector,
                document_type,
                document_type,
                query_vector,
                top_k,
            )

        with connection.cursor() as cursor:

            cursor.execute(
                sql,
                parameters,
            )

            rows = cursor.fetchall()

        results: list[SearchResult] = []

        for row in rows:

            cosine_distance = float(
                row[8]
            )

            similarity_score = (
                1.0 - cosine_distance
            )

            results.append(
                SearchResult(
                    chunk_id=row[0],
                    document_id=row[1],
                    document_name=row[2],
                    document_type=row[3],
                    chunk_type=row[4],
                    chunk_text=row[5],
                    page_number=row[6],
                    metadata=row[7] or {},
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