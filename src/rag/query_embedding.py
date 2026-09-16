from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


DEFAULT_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)


class QueryEmbedder:
    """
    Converts a natural-language RAG query
    into an embedding vector.
    """

    def __init__(
        self,
        model: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:

        self.model = model
        self.client = OpenAI()

    def embed(
        self,
        query: str,
    ) -> list[float]:

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        response = (
            self.client.embeddings.create(
                model=self.model,
                input=query,
            )
        )

        embedding = (
            response.data[0].embedding
        )

        if not embedding:
            raise RuntimeError(
                "Embedding API returned "
                "an empty embedding."
            )

        return embedding