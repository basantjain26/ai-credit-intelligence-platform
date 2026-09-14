import json

import psycopg2

from pgvector.psycopg2 import (
    register_vector,
)

from src.settings import (
    DB_CONFIG,
)

from src.document_intelligence.chunking.semantic_chunker import (
    SemanticChunk,
)


class VectorRepository:

    def __init__(self):

        self.connection = (
            psycopg2.connect(
                **DB_CONFIG
            )
        )

        register_vector(
            self.connection
        )

    def save_chunks(
        self,
        chunks: list[SemanticChunk],
        embeddings: list[list[float]],
        embedding_model: str,
    ) -> None:

        if len(chunks) != len(embeddings):

            raise ValueError(
                "Chunks and embeddings "
                "must have equal counts."
            )

        with self.connection:

            with self.connection.cursor() as cursor:

                for chunk, embedding in zip(
                    chunks,
                    embeddings,
                ):

                    cursor.execute(
                        """
                        INSERT INTO document_chunks (
                            chunk_id,
                            document_id,
                            chunk_type,
                            chunk_text,
                            page_number,
                            metadata,
                            embedding,
                            embedding_model
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        ON CONFLICT (chunk_id)
                        DO UPDATE SET

                            chunk_text =
                                EXCLUDED.chunk_text,

                            metadata =
                                EXCLUDED.metadata,

                            embedding =
                                EXCLUDED.embedding,

                            embedding_model =
                                EXCLUDED.embedding_model;
                        """,
                        (
                            chunk.chunk_id,
                            chunk.document_id,
                            chunk.chunk_type,
                            chunk.text,
                            chunk.page_number,
                            json.dumps(
                                chunk.metadata
                            ),
                            embedding,
                            embedding_model,
                        ),
                    )

    def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[dict]:

        with self.connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    chunk_type,
                    chunk_text,
                    page_number,
                    metadata,

                    1 - (
                        embedding
                        <=> %s::vector
                    ) AS similarity

                FROM document_chunks

                WHERE embedding IS NOT NULL

                ORDER BY
                    embedding
                    <=> %s::vector

                LIMIT %s;
                """,
                (
                    query_embedding,
                    query_embedding,
                    limit,
                ),
            )

            rows = cursor.fetchall()

        return [
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "chunk_type": row[2],
                "text": row[3],
                "page_number": row[4],
                "metadata": row[5],
                "similarity": float(
                    row[6]
                ),
            }
            for row in rows
        ]

    def close(
        self,
    ) -> None:

        self.connection.close()