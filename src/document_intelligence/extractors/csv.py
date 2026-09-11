from pathlib import Path
import csv
import uuid

from .base import DocumentExtractor
from src.document_intelligence.models import ContentBlock, ExtractedDocument


class CSVExtractor(DocumentExtractor):

    def extract(
        self,
        file_path: Path,
        document_id: str,
    ) -> ExtractedDocument:

        rows = []

        with open(
            file_path,
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.reader(file)

            for row in reader:
                rows.append(row)

        block = ContentBlock(
            block_id=self._new_block_id(document_id),
            block_type="TABLE",
            rows=rows,
            table_index=1,
        )

        return ExtractedDocument(
            document_id=document_id,
            file_name=file_path.name,
            file_type="CSV",
            parser_name="python-csv",
            parser_version="stdlib",
            content_blocks=[block],
        )

    @staticmethod
    def _new_block_id(document_id: str) -> str:
        suffix = uuid.uuid4().hex[:10].upper()
        return f"{document_id}_BLK_{suffix}"