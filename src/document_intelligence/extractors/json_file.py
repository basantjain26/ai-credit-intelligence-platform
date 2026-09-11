from pathlib import Path
import json
import uuid

from .base import DocumentExtractor
from src.document_intelligence.models import ContentBlock, ExtractedDocument


class JSONExtractor(DocumentExtractor):

    def extract(
        self,
        file_path: Path,
        document_id: str,
    ) -> ExtractedDocument:

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        text = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )

        block = ContentBlock(
            block_id=self._new_block_id(document_id),
            block_type="TEXT",
            text=text,
        )

        return ExtractedDocument(
            document_id=document_id,
            file_name=file_path.name,
            file_type="JSON",
            parser_name="python-json",
            parser_version="stdlib",
            content_blocks=[block],
        )

    @staticmethod
    def _new_block_id(document_id: str) -> str:
        suffix = uuid.uuid4().hex[:10].upper()
        return f"{document_id}_BLK_{suffix}"