from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContentBlock:
    block_id: str
    block_type: str
    text: str | None = None
    rows: list[list[Any]] | None = None

    page_number: int | None = None
    paragraph_index: int | None = None
    table_index: int | None = None
    sheet_name: str | None = None
    row_number: int | None = None


@dataclass
class ExtractedDocument:
    document_id: str
    file_name: str
    file_type: str
    parser_name: str
    parser_version: str

    content_blocks: list[ContentBlock] = field(default_factory=list)