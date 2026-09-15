from __future__ import annotations

import os

from langchain_core.documents import Document
from openai import OpenAI
from pydantic import BaseModel, Field


DEFAULT_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6",
)


class ChunkRelevanceScore(BaseModel):
    """
    Relevance judgment for one retrieved chunk.
    """

    chunk_id: str

    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    reason: str


class RerankingResult(BaseModel):
    """
    Structured result returned by the reranking model.
    """

    rankings: list[ChunkRelevanceScore]


class LLMReranker:
    """
    Reranks vector-search candidates according to how useful
    each chunk is for answering the user's specific question.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
    ) -> None:

        self.model = model
        self.client = OpenAI()

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_n: int = 4,
    ) -> list[Document]:

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        if not documents:
            return []

        if top_n < 1:
            raise ValueError(
                "top_n must be at least 1."
            )

        candidate_text = self._build_candidate_text(
            documents
        )

        response = self.client.responses.parse(
            model=self.model,
            instructions=(
                "You are a retrieval reranking component for "
                "a commercial-bank credit analysis system. "
                "Evaluate how relevant each candidate document "
                "chunk is to answering the user's question. "
                "Use only the supplied candidate text. "
                "Do not answer the user's question. "
                "Do not introduce external knowledge. "
                "Assign each candidate a relevance score from "
                "0.0 to 1.0, where 1.0 means directly useful "
                "evidence and 0.0 means irrelevant. "
                "Return one ranking entry for every supplied "
                "chunk_id."
            ),
            input=(
                f"QUESTION:\n"
                f"{query}\n\n"
                f"CANDIDATE CHUNKS:\n"
                f"{candidate_text}"
            ),
            text_format=RerankingResult,
        )

        parsed = response.output_parsed

        if parsed is None:
            raise RuntimeError(
                "Reranking model returned no structured result."
            )

        return self._apply_ranking(
            documents=documents,
            ranking_result=parsed,
            top_n=top_n,
        )

    @staticmethod
    def _build_candidate_text(
        documents: list[Document],
    ) -> str:

        sections = []

        for document in documents:

            chunk_id = document.metadata.get(
                "chunk_id"
            )

            document_name = document.metadata.get(
                "document_name"
            )

            page_number = document.metadata.get(
                "page_number"
            )

            sections.append(
                "\n".join(
                    [
                        f"CHUNK_ID: {chunk_id}",
                        f"DOCUMENT: {document_name}",
                        f"PAGE: {page_number}",
                        "TEXT:",
                        document.page_content,
                    ]
                )
            )

        return "\n\n---\n\n".join(
            sections
        )

    @staticmethod
    def _apply_ranking(
        documents: list[Document],
        ranking_result: RerankingResult,
        top_n: int,
    ) -> list[Document]:

        score_lookup = {
            ranking.chunk_id: ranking
            for ranking in ranking_result.rankings
        }

        reranked_documents = []

        for document in documents:

            chunk_id = document.metadata.get(
                "chunk_id"
            )

            ranking = score_lookup.get(
                chunk_id
            )

            if ranking is None:
                continue

            # Preserve vector retrieval score and add
            # reranker information separately.

            document.metadata[
                "reranker_score"
            ] = ranking.relevance_score

            document.metadata[
                "reranker_reason"
            ] = ranking.reason

            reranked_documents.append(
                document
            )

        reranked_documents.sort(
            key=lambda document: document.metadata.get(
                "reranker_score",
                0.0,
            ),
            reverse=True,
        )

        return reranked_documents[:top_n]