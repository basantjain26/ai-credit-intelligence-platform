from src.rag.langchain_retriever import (
    CreditDocumentRetriever,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def main() -> None:

    query = (
        "What concerns exist around ABC Manufacturing's "
        "debt and repayment capacity?"
    )

    retriever = CreditDocumentRetriever(
        customer_id=customer_id,
        application_id=application_id,
        top_k=5,
    )

    documents = retriever.invoke(
        query
    )

    print("=" * 100)
    print("QUERY")
    print("=" * 100)

    print(query)

    print("\n")
    print("=" * 100)
    print("LANGCHAIN RETRIEVAL RESULTS")
    print("=" * 100)

    for rank, document in enumerate(
        documents,
        start=1,
    ):

        metadata = document.metadata

        print("\n" + "-" * 100)

        print(
            f"Rank: {rank}"
        )

        print(
            "Similarity:",
            round(
                metadata["similarity_score"],
                4,
            ),
        )

        print(
            "Document:",
            metadata["document_name"],
        )

        print(
            "Document type:",
            metadata["document_type"],
        )

        print(
            "Chunk ID:",
            metadata["chunk_id"],
        )

        print(
            "Page:",
            metadata["page_number"],
        )

        print("\nText:")

        print(
            document.page_content
        )


if __name__ == "__main__":
    main()