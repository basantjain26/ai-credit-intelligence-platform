from src.rag.langchain_retriever import (
    CreditDocumentRetriever,
)


def print_results(
    title: str,
    documents: list,
) -> None:

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    for index, document in enumerate(
        documents,
        start=1,
    ):

        metadata = document.metadata

        print()
        print(f"RESULT {index}")
        print(
            f"Document: "
            f"{metadata.get('document_name')}"
        )
        print(
            f"Type: "
            f"{metadata.get('document_type')}"
        )
        print(
            f"Chunk ID: "
            f"{metadata.get('chunk_id')}"
        )
        print()

        print(
            document.page_content[:1000]
        )


def main() -> None:

    retriever = CreditDocumentRetriever(
        customer_id=None,
        application_id=None,
        document_type="LENDING_POLICY",
        scope="ENTERPRISE",
        top_k=5,
    )

    query_1 = (
        "What is the minimum DSCR "
        "requirement for a working "
        "capital borrower?"
    )

    results_1 = retriever.invoke(
        query_1
    )

    print_results(
        title=query_1,
        documents=results_1,
    )

    query_2 = (
        "What policy applies to "
        "material related-party "
        "transactions?"
    )

    results_2 = retriever.invoke(
        query_2
    )

    print_results(
        title=query_2,
        documents=results_2,
    )


if __name__ == "__main__":
    main()