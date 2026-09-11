from pathlib import Path
import uuid
import fitz

from .base import DocumentExtractor
from src.document_intelligence.models import ContentBlock, ExtractedDocument


class PDFExtractor(DocumentExtractor):

    def extract(
        self,
        file_path: Path,
        document_id: str,
    ) -> ExtractedDocument:

        pdf = fitz.open(file_path)
        content_blocks = []

        try:
            for page_index, page in enumerate(pdf):
                page_number = page_index + 1

                text = page.get_text("text").strip()

                if text:
                    content_blocks.append(
                        ContentBlock(
                            block_id=self._new_block_id(document_id),
                            block_type="TEXT",
                            text=text,
                            page_number=page_number,
                        )
                    )

                tables = self._extract_tables(
                    page=page,
                    document_id=document_id,
                    page_number=page_number,
                )

                content_blocks.extend(tables)

        finally:
            pdf.close()

        return ExtractedDocument(
            document_id=document_id,
            file_name=file_path.name,
            file_type="PDF",
            parser_name="PyMuPDF",
            parser_version=fitz.VersionBind,
            content_blocks=content_blocks,
        )

    def _extract_tables(
        self,
        page,
        document_id: str,
        page_number: int,
    ) -> list[ContentBlock]:

        blocks = []

        try:
            table_finder = page.find_tables()

            for table_index, table in enumerate(
                table_finder.tables,
                start=1,
            ):
                rows = table.extract()

                blocks.append(
                    ContentBlock(
                        block_id=self._new_block_id(document_id),
                        block_type="TABLE",
                        rows=rows,
                        page_number=page_number,
                        table_index=table_index,
                    )
                )

        except Exception as exc:
            print(
                f"Table extraction failed "
                f"on page {page_number}: {exc}"
            )

        return blocks

    @staticmethod
    def _new_block_id(document_id: str) -> str:
        suffix = uuid.uuid4().hex[:10].upper()
        return f"{document_id}_BLK_{suffix}"