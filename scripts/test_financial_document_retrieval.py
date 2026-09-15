from src.financial_analysis.retrieval import (
    FinancialDocumentRetriever,
)


def run_search(
    retriever,
    query,
    customer_id,
    application_id,
):

    print(
        "\n"
        + "=" * 80
    )

    print(
        f"QUERY: {query}"
    )

    print(
        "=" * 80
    )

    results = retriever.search(
        query=query,
        customer_id=customer_id,
        application_id=application_id,
        limit=5,
    )

    if not results:

        print(
            "No financial evidence found."
        )

        return

    for index, evidence in enumerate(
        results,
        start=1,
    ):

        print(
            f"\nRESULT {index}"
        )

        print(
            "Similarity:",
            round(
                evidence.similarity,
                4,
            ),
        )

        print(
            "Document:",
            evidence.document_name,
        )

        print(
            "Document ID:",
            evidence.document_id,
        )

        print(
            "Chunk ID:",
            evidence.chunk_id,
        )

        print(
            "Chunk Type:",
            evidence.chunk_type,
        )

        print(
            "Page:",
            evidence.page_number,
        )

        print(
            "Fiscal Year:",
            evidence.fiscal_year,
        )

        print(
            "\nEvidence:"
        )

        print(
            evidence.chunk_text
        )

        print(
            "\nMetadata:"
        )

        print(
            evidence.metadata
        )


def main():

    customer_id = "CUST_000001"
    application_id = "APP_2026_00001"

    queries = [
        (
            "What was FY2026 revenue "
            "and EBITDA?"
        ),
        (
            "Reasons for revenue decline "
            "or weaker sales performance"
        ),
        (
            "Debt borrowings leverage "
            "and financing"
        ),
        (
            "Operating cash flow and "
            "liquidity"
        ),
    ]

    with FinancialDocumentRetriever() as retriever:

        for query in queries:

            run_search(
                retriever=retriever,
                query=query,
                customer_id=customer_id,
                application_id=application_id,
            )


if __name__ == "__main__":
    main()