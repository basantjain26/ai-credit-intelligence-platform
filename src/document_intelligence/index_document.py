from pathlib import Path

from src.settings import (
    OPENAI_EMBEDDING_MODEL,
)

from src.document_intelligence.extractors.llm_pdf import (
    LLMPDFExtractor,
)

from src.document_intelligence.chunking.semantic_chunker import (
    FinancialDocumentChunker,
)

from src.document_intelligence.embeddings.openai_embedder import (
    OpenAIEmbedder,
)

from src.document_intelligence.embeddings.vector_repository import (
    VectorRepository,
)


class DocumentIndexer:

    def __init__(
        self,
    ):

        self.extractor = (
            LLMPDFExtractor()
        )

        self.chunker = (
            FinancialDocumentChunker()
        )

        self.embedder = (
            OpenAIEmbedder()
        )

    def index_pdf(
        self,
        document_id: str,
        file_path: Path,
    ) -> None:

        print(
            "\n1. Extracting document..."
        )

        document_result = (
            self.extractor.extract_document(
                file_path=file_path
            )
        )

        print(
            "\n2. Creating semantic chunks..."
        )

        chunks = (
            self.chunker.chunk(
                document_id=document_id,
                extraction=(
                    document_result.extraction
                ),
            )
        )

        print(
            f"Created {len(chunks)} chunks."
        )

        if not chunks:

            raise RuntimeError(
                "No semantic chunks generated."
            )

        print(
            "\n3. Generating embeddings..."
        )

        embeddings = (
            self.embedder.embed_texts(
                [
                    chunk.text
                    for chunk in chunks
                ]
            )
        )

        print(
            f"Generated "
            f"{len(embeddings)} embeddings."
        )

        print(
            "\n4. Storing vectors..."
        )

        repository = (
            VectorRepository()
        )

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
            "\nDocument indexing complete."
        )