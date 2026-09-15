from src.rag.langchain_retriever import (
    CreditDocumentRetriever,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def print_results(
    title: str,
    documents: list,
) -> None:

    print("\n")
    print("=" * 100)
    print(title)
    print("=" * 100)

    for rank, document in enumerate(
        documents,
        start=1,
    ):
        metadata = document.metadata

        print(
            f"\n{rank}. "
            f"{metadata['document_name']}"
        )

        print(
            f"   Type: "
            f"{metadata['document_type']}"
        )

        print(
            f"   Similarity: "
            f"{metadata['similarity_score']:.4f}"
        )

        print(
            f"   Chunk: "
            f"{metadata['chunk_id']}"
        )

        print(
            f"   Page: "
            f"{metadata['page_number']}"
        )


def main() -> None:

    query = (
        "What concerns exist around the borrower's "
        "debt and repayment capacity?"
    )

    # --------------------------------------------------
    # Search all RAG documents
    # --------------------------------------------------

    general_retriever = CreditDocumentRetriever(
        customer_id=customer_id,
        application_id=application_id,
        top_k=5,
    )

    general_results = general_retriever.invoke(
        query
    )

    print_results(
        "UNFILTERED RETRIEVAL",
        general_results,
    )

    # --------------------------------------------------
    # Search only audited financial statements
    # --------------------------------------------------

    financial_retriever = CreditDocumentRetriever(
        customer_id=customer_id,
        application_id=application_id,
        document_type="FINANCIAL_STATEMENT",
        top_k=5,
    )

    financial_results = financial_retriever.invoke(
        query
    )

    print_results(
        "FINANCIAL_STATEMENT ONLY",
        financial_results,
    )


if __name__ == "__main__":
    main()