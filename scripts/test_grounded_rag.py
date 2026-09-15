from src.rag.pipeline import CreditRAGPipeline


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def main() -> None:

    query = (
        "What concerns exist around ABC Manufacturing's "
        "debt and repayment capacity?"
    )

    rag = CreditRAGPipeline(
        customer_id=customer_id,
        application_id=application_id,
        retrieval_top_k=10,
        context_top_n=4,
    )

    result = rag.ask(
        query
    )

    print("=" * 100)
    print("QUESTION")
    print("=" * 100)

    print(query)

    print("\n")
    print("=" * 100)
    print("GROUNDED ANSWER")
    print("=" * 100)

    print(result.answer)

    print("\n")
    print("=" * 100)
    print("SUPPORTED CLAIMS")
    print("=" * 100)

    for index, claim in enumerate(
        result.claims,
        start=1,
    ):

        print(
            f"\n{index}. {claim.claim}"
        )

        for citation in claim.citations:

            print(
                "   Evidence: "
                f"{citation.document_name} "
                f"| page={citation.page_number} "
                f"| chunk={citation.chunk_id}"
            )

    print("\n")
    print("=" * 100)
    print("CITATIONS USED")
    print("=" * 100)

    for citation in result.citations:

        print(
            f"- {citation.document_name} "
            f"| page={citation.page_number} "
            f"| chunk={citation.chunk_id}"
        )

    if result.limitations:

        print("\n")
        print("=" * 100)
        print("LIMITATIONS")
        print("=" * 100)

        for limitation in result.limitations:

            print(
                f"- {limitation}"
            )


if __name__ == "__main__":
    main()