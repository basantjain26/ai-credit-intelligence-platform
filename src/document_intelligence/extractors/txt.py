from pathlib import Path
import uuid

from .base import DocumentExtractor
from src.document_intelligence.models import (
    ContentBlock,
    ExtractedDocument,
)


class TXTExtractor(DocumentExtractor):

    def extract(
        self,
        file_path: Path,
        document_id: str,
    ) -> ExtractedDocument:

        text = file_path.read_text(
            encoding="utf-8"
        )

        content_blocks = []

        paragraphs = text.split("\n\n")

        for paragraph_index, paragraph in enumerate(
            paragraphs
        ):
            cleaned_text = paragraph.strip()

            if not cleaned_text:
                continue

            content_blocks.append(
                ContentBlock(
                    block_id=self._new_block_id(document_id),
                    block_type="TEXT",
                    text=cleaned_text,
                    paragraph_index=paragraph_index,
                )
            )

        return ExtractedDocument(
            document_id=document_id,
            file_name=file_path.name,
            file_type="TXT",
            parser_name="python-text",
            parser_version="1.0",
            content_blocks=content_blocks,
        )

    @staticmethod
    def _new_block_id(document_id: str) -> str:
        suffix = uuid.uuid4().hex[:10].upper()
        return f"{document_id}_BLK_{suffix}"