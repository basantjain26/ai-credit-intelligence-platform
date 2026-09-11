from dataclasses import dataclass

from src.document_intelligence.models import ExtractedDocument


@dataclass
class ExtractionQuality:
    character_count: int
    text_block_count: int
    table_count: int
    keyword_coverage: float
    quality_score: float
    requires_fallback: bool


FINANCIAL_KEYWORDS = {
    "revenue",
    "ebitda",
    "net income",
    "assets",
    "liabilities",
    "debt",
    "cash flow",
}


def evaluate_financial_document(
    document: ExtractedDocument,
) -> ExtractionQuality:

    text_blocks = [
        block
        for block in document.content_blocks
        if block.block_type == "TEXT"
    ]

    table_blocks = [
        block
        for block in document.content_blocks
        if block.block_type == "TABLE"
    ]

    full_text = " ".join(
        block.text or ""
        for block in text_blocks
    ).lower()

    character_count = len(full_text)

    matched_keywords = sum(
        keyword in full_text
        for keyword in FINANCIAL_KEYWORDS
    )

    keyword_coverage = (
        matched_keywords / len(FINANCIAL_KEYWORDS)
    )

    text_score = min(character_count / 3000, 1.0)
    table_score = min(len(table_blocks) / 2, 1.0)

    quality_score = (
        0.50 * text_score
        + 0.30 * keyword_coverage
        + 0.20 * table_score
    )

    requires_fallback = quality_score < 0.60

    return ExtractionQuality(
        character_count=character_count,
        text_block_count=len(text_blocks),
        table_count=len(table_blocks),
        keyword_coverage=round(keyword_coverage, 3),
        quality_score=round(quality_score, 3),
        requires_fallback=requires_fallback,
    )