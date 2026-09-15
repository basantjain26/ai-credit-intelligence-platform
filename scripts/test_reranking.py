from src.rag.langchain_retriever import (
    CreditDocumentRetriever,
)
from src.rag.reranker import (
    LLMReranker,
)


customer_id = "CUST_000001"
application_id = "APP_2026_00001"


def main() -> None:

    query = (
        "What concerns exist around ABC Manufacturing's "
        "debt and repayment capacity?"
    )

    # =====================================================
    # STAGE 1 — VECTOR RETRIEVAL
    # =====================================================

    retriever = CreditDocumentRetriever(
        customer_id=customer_id,
        application_id=application_id,
        top_k=10,
    )

    candidates = retriever.invoke(
        query
    )

    print("=" * 100)
    print("STAGE 1 — VECTOR RETRIEVAL")
    print("=" * 100)

    for rank, document in enumerate(
        candidates,
        start=1,
    ):

        print(
            f"\n{rank}. "
            f"{document.metadata['chunk_id']}"
        )

        print(
            f"   Document: "
            f"{document.metadata['document_name']}"
        )

        print(
            f"   Vector similarity: "
            f"{document.metadata['similarity_score']:.4f}"
        )

    # =====================================================
    # STAGE 2 — LLM RERANKING
    # =====================================================

    reranker = LLMReranker()

    reranked = reranker.rerank(
        query=query,
        documents=candidates,
        top_n=4,
    )

    print("\n")
    print("=" * 100)
    print("STAGE 2 — RERANKED CONTEXT")
    print("=" * 100)

    for rank, document in enumerate(
        reranked,
        start=1,
    ):

        metadata = document.metadata

        print(
            f"\n{rank}. "
            f"{metadata['chunk_id']}"
        )

        print(
            f"   Document: "
            f"{metadata['document_name']}"
        )

        print(
            f"   Page: "
            f"{metadata['page_number']}"
        )

        print(
            f"   Vector similarity: "
            f"{metadata['similarity_score']:.4f}"
        )

        print(
            f"   Reranker score: "
            f"{metadata['reranker_score']:.4f}"
        )

        print(
            f"   Reason: "
            f"{metadata['reranker_reason']}"
        )

        print("\n   Text:")

        print(
            f"   {document.page_content}"
        )


if __name__ == "__main__":
    main()