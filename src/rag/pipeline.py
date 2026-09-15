from __future__ import annotations

from src.rag.grounded_answer import (
    GroundedAnswerGenerator,
    GroundedAnswerResult,
)
from src.rag.langchain_retriever import (
    CreditDocumentRetriever,
)
from src.rag.reranker import (
    LLMReranker,
)


class CreditRAGPipeline:
    """
    Enterprise RAG pipeline for one trusted credit case.

    Flow:

        Query
          ↓
        Vector retrieval
          ↓
        Reranking
          ↓
        Context selection
          ↓
        Grounded generation
          ↓
        Deterministic citation validation
    """

    def __init__(
        self,
        customer_id: str,
        application_id: str,
        retrieval_top_k: int = 10,
        context_top_n: int = 4,
        document_type: str | None = None,
    ) -> None:

        self.customer_id = customer_id
        self.application_id = application_id

        self.context_top_n = context_top_n

        self.retriever = CreditDocumentRetriever(
            customer_id=customer_id,
            application_id=application_id,
            top_k=retrieval_top_k,
            document_type=document_type,
        )

        self.reranker = LLMReranker()

        self.answer_generator = (
            GroundedAnswerGenerator()
        )

    def ask(
        self,
        query: str,
    ) -> GroundedAnswerResult:

        # ----------------------------------------------------
        # Stage 1 — Semantic retrieval
        # ----------------------------------------------------

        candidates = self.retriever.invoke(
            query
        )

        if not candidates:
            raise RuntimeError(
                "No relevant document chunks were retrieved."
            )

        # ----------------------------------------------------
        # Stage 2 — Reranking / context selection
        # ----------------------------------------------------

        context_documents = self.reranker.rerank(
            query=query,
            documents=candidates,
            top_n=self.context_top_n,
        )

        if not context_documents:
            raise RuntimeError(
                "No document chunks remained after reranking."
            )

        # ----------------------------------------------------
        # Stage 3 — Grounded generation
        # ----------------------------------------------------

        return self.answer_generator.generate(
            query=query,
            documents=context_documents,
        )