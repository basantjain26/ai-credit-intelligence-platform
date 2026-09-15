from src.rag.query_embedding import QueryEmbedder


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def main() -> None:

    query = (
        "What concerns exist around ABC Manufacturing's "
        "debt and repayment capacity?"
    )

    embedder = QueryEmbedder()

    embedding = embedder.embed(
        query
    )

    print("Query:")
    print(query)

    print("\nEmbedding model:")
    print(embedder.model)

    print("\nEmbedding dimension:")
    print(len(embedding))

    print("\nFirst 10 values:")
    print(embedding[:10])


if __name__ == "__main__":
    main()