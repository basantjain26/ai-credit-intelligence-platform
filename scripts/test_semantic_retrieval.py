from src.rag.retriever import (
    SemanticRetriever,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"

# IMPORTANT:
# Replace this only if your database query shows a different
# embedding_model.
EMBEDDING_MODEL = (
    "text-embedding-3-small"
)


def main() -> None:

    retriever = SemanticRetriever(
        embedding_model=EMBEDDING_MODEL
    )

    queries = [
        (
            "What concerns exist around "
            "ABC Manufacturing's debt and "
            "repayment capacity?"
        ),
        (
            "What is the borrower's "
            "revenue performance?"
        ),
        (
            "What related-party risks "
            "have been identified?"
        ),
    ]

    for query in queries:

        print(
            "\n"
            + "=" * 100
        )

        print(
            "QUERY"
        )

        print(
            "=" * 100
        )

        print(
            query
        )

        results = retriever.retrieve(
            query=query,
            top_k=5,
            customer_id=customer_id,
            application_id=application_id,
        )

        print(
            "\nTOP RETRIEVED CHUNKS"
        )

        for rank, chunk in enumerate(
            results,
            start=1,
        ):

            print(
                "\n"
                + "-" * 100
            )

            print(
                f"Rank: {rank}"
            )

            print(
                "Similarity:",
                round(
                    chunk.similarity_score,
                    4,
                ),
            )

            print(
                "Cosine distance:",
                round(
                    chunk.cosine_distance,
                    4,
                ),
            )

            print(
                "Document:",
                chunk.document_name,
            )

            print(
                "Document type:",
                chunk.document_type,
            )

            print(
                "Chunk ID:",
                chunk.chunk_id,
            )

            print(
                "Chunk type:",
                chunk.chunk_type,
            )

            print(
                "Page:",
                chunk.page_number,
            )

            print(
                "\nText:"
            )

            print(
                chunk.chunk_text
            )


if __name__ == "__main__":
    main()