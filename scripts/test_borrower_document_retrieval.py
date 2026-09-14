from src.borrower_intelligence.retrieval import (
    BorrowerDocumentRetriever,
)


def run_query(
    retriever: BorrowerDocumentRetriever,
    query: str,
    customer_id: str,
    application_id: str,
):

    print(
        "\n"
        "===================================="
    )

    print(
        f"QUERY: {query}"
    )

    print(
        "===================================="
    )

    results = retriever.search(
        query=query,
        customer_id=customer_id,
        application_id=application_id,
        limit=3,
    )

    if not results:

        print(
            "No evidence found."
        )

        return

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"\nResult {index}"
        )

        print(
            "Similarity:",
            round(
                result.similarity,
                4,
            ),
        )

        print(
            "Document:",
            result.document_name,
        )

        print(
            "Document type:",
            result.document_type,
        )

        print(
            "Chunk type:",
            result.chunk_type,
        )

        print(
            "Page:",
            result.page_number,
        )

        print(
            "\nEvidence:"
        )

        print(
            result.chunk_text
        )


def main():

    customer_id = "CUST_000001"
    application_id = "APP_2026_00001"

    retriever = (
        BorrowerDocumentRetriever()
    )

    try:

        queries = [
            (
                "What business does "
                "ABC Manufacturing operate?"
            ),
            (
                "What was the borrower's "
                "FY2026 revenue?"
            ),
            (
                "What does the document "
                "say about EBITDA?"
            ),
            (
                "What existing credit "
                "facilities does the "
                "borrower have?"
            ),
            (
                "Are any related parties "
                "mentioned?"
            ),
        ]

        for query in queries:

            run_query(
                retriever=retriever,
                query=query,
                customer_id=customer_id,
                application_id=application_id,
            )

    finally:

        retriever.close()


if __name__ == "__main__":
    main()