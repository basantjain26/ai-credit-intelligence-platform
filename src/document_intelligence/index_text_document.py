from __future__ import annotations

import psycopg2

from src.settings import (
    DB_CONFIG,
    OPENAI_EMBEDDING_MODEL,
)

from src.document_intelligence.chunking.text_block_chunker import (
    TextBlockChunker,
)

from src.document_intelligence.embeddings.openai_embedder import (
    OpenAIEmbedder,
)

from src.document_intelligence.embeddings.vector_repository import (
    VectorRepository,
)


class TextDocumentIndexer:

    def __init__(self) -> None:

        self.chunker = TextBlockChunker()

        self.embedder = OpenAIEmbedder()

    def _load_blocks(
        self,
        document_id: str,
    ) -> list[dict]:

        connection = psycopg2.connect(
            **DB_CONFIG
        )

        try:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        block_id,
                        text_content,
                        page_number,
                        paragraph_index
                    FROM document_content_blocks
                    WHERE document_id = %s
                      AND text_content IS NOT NULL
                    ORDER BY
                        paragraph_index NULLS LAST,
                        block_id
                    """,
                    (document_id,),
                )

                rows = cursor.fetchall()

        finally:
            connection.close()

        return [
            {
                "block_id": row[0],
                "text_content": row[1],
                "page_number": row[2],
                "paragraph_index": row[3],
            }
            for row in rows
        ]

    def index(
        self,
        document_id: str,
    ) -> None:

        print(
            "\n1. Loading extracted text blocks..."
        )

        blocks = self._load_blocks(
            document_id=document_id
        )

        print(
            f"Loaded {len(blocks)} blocks."
        )

        if not blocks:
            raise RuntimeError(
                "No extracted text blocks found."
            )

        print(
            "\n2. Creating text chunks..."
        )

        chunks = self.chunker.chunk(
            document_id=document_id,
            blocks=blocks,
        )

        print(
            f"Created {len(chunks)} chunks."
        )

        if not chunks:
            raise RuntimeError(
                "No text chunks generated."
            )

        print(
            "\n3. Generating embeddings..."
        )

        embeddings = self.embedder.embed_texts(
            [
                chunk.text
                for chunk in chunks
            ]
        )

        print(
            f"Generated "
            f"{len(embeddings)} embeddings."
        )

        print(
            "\n4. Storing vectors..."
        )

        repository = VectorRepository()

        try:
            repository.save_chunks(
                chunks=chunks,
                embeddings=embeddings,
                embedding_model=(
                    OPENAI_EMBEDDING_MODEL
                ),
            )

        finally:
            repository.close()

        print(
            "\nText document indexing complete."
        )