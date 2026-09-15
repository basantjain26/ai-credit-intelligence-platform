from src.rag.query_embedding import QueryEmbedder
from src.rag.vector_search import search_similar_chunks


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def main() -> None:

    query = (
        "What concerns exist around ABC Manufacturing's "
        "debt and repayment capacity?"
    )

    # -----------------------------------------
    # Step 1: Embed the query
    # -----------------------------------------

    embedder = QueryEmbedder()

    query_embedding = embedder.embed(
        query
    )

    print("=" * 100)
    print("QUERY")
    print("=" * 100)

    print(query)

    print(
        f"\nEmbedding dimension: "
        f"{len(query_embedding)}"
    )

    # -----------------------------------------
    # Step 2: Vector search
    # -----------------------------------------

    results = search_similar_chunks(
        query_embedding=query_embedding,
        customer_id=customer_id,
        application_id=application_id,
        top_k=5,
    )

    print("\n")
    print("=" * 100)
    print("TOP 5 SEMANTIC RESULTS")
    print("=" * 100)

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print("\n" + "-" * 100)

        print(
            f"Rank: {rank}"
        )

        print(
            f"Similarity: "
            f"{result.similarity_score:.4f}"
        )

        print(
            f"Cosine distance: "
            f"{result.cosine_distance:.4f}"
        )

        print(
            f"Document: "
            f"{result.document_name}"
        )

        print(
            f"Document type: "
            f"{result.document_type}"
        )

        print(
            f"Chunk ID: "
            f"{result.chunk_id}"
        )

        print(
            f"Chunk type: "
            f"{result.chunk_type}"
        )

        print(
            f"Page: "
            f"{result.page_number}"
        )

        print("\nText:")

        print(
            result.chunk_text
        )


if __name__ == "__main__":
    main()