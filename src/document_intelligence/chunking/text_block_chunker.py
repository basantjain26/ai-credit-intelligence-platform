from uuid import uuid4

from src.document_intelligence.chunking.semantic_chunker import (
    SemanticChunk,
)


class TextBlockChunker:

    def chunk(
        self,
        document_id: str,
        blocks: list[dict],
    ) -> list[SemanticChunk]:

        chunks: list[SemanticChunk] = []

        for block in blocks:

            text = (
                block.get("text_content") or ""
            ).strip()

            if not text:
                continue

            chunks.append(
                SemanticChunk(
                    chunk_id=str(uuid4()),
                    document_id=document_id,
                    chunk_type="TEXT",
                    text=text,
                    page_number=block.get(
                        "page_number"
                    ),
                    metadata={
                        "block_id": block.get(
                            "block_id"
                        ),
                        "paragraph_index": block.get(
                            "paragraph_index"
                        ),
                    },
                )
            )

        return chunks