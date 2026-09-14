from openai import OpenAI

from src.settings import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
)


class OpenAIEmbedder:

    def __init__(self):

        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        self.model = (
            OPENAI_EMBEDDING_MODEL
        )

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        text = text.strip()

        if not text:
            raise ValueError(
                "Cannot embed empty text."
            )

        response = (
            self.client.embeddings.create(
                model=self.model,
                input=text,
            )
        )

        return (
            response.data[0]
            .embedding
        )

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        cleaned_texts = [
            text.strip()
            for text in texts
            if text.strip()
        ]

        if not cleaned_texts:
            return []

        response = (
            self.client.embeddings.create(
                model=self.model,
                input=cleaned_texts,
            )
        )

        ordered_results = sorted(
            response.data,
            key=lambda item: item.index,
        )

        return [
            result.embedding
            for result in ordered_results
        ]