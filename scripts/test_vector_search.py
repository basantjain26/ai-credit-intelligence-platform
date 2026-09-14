from src.document_intelligence.embeddings.openai_embedder import (
    OpenAIEmbedder,
)

from src.document_intelligence.embeddings.vector_repository import (
    VectorRepository,
)


QUERIES = [
    "What was ABC Manufacturing revenue?",
    "How much debt does the borrower have?",
    "What is the company's EBITDA?",
    "What was operating cash flow?",
]


def main():

    embedder = (
        OpenAIEmbedder()
    )

    repository = (
        VectorRepository()
    )

    try:

        for query in QUERIES:

            print(
                "\n"
                + "=" * 80
            )

            print(
                f"QUERY: {query}"
            )

            query_embedding = (
                embedder.embed_text(
                    query
                )
            )

            results = (
                repository.search(
                    query_embedding=(
                        query_embedding
                    ),
                    limit=3,
                )
            )

            for rank, result in enumerate(
                results,
                start=1,
            ):

                print(
                    f"\nRESULT #{rank}"
                )

                print(
                    "Similarity:",
                    round(
                        result["similarity"],
                        4,
                    ),
                )

                print(
                    "Document:",
                    result["document_id"],
                )

                print(
                    "Page:",
                    result["page_number"],
                )

                print(
                    "Chunk type:",
                    result["chunk_type"],
                )

                print(
                    "\nText:"
                )

                print(
                    result["text"][:1000]
                )

    finally:

        repository.close()


if __name__ == "__main__":
    main()