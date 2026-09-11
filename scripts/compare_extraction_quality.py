from pathlib import Path

from src.document_intelligence.extractors.pdf import PDFExtractor
from src.document_intelligence.quality.evaluator import (
    evaluate_financial_document,
)


FILES = [
    Path(
        "data/source/documents/financial_statements/"
        "ABC_FY2026_Audited_Financials.pdf"
    ),
    Path(
        "data/source/documents/financial_statements/"
        "ABC_FY2026_Audited_Financials_SCANNED.pdf"
    ),
]


def main():
    extractor = PDFExtractor()

    for index, file_path in enumerate(FILES, start=1):

        extracted = extractor.extract(
            file_path=file_path,
            document_id=f"QUALITY_TEST_{index}",
        )

        quality = evaluate_financial_document(extracted)

        print()
        print("=" * 60)
        print(file_path.name)
        print("=" * 60)
        print(f"Characters       : {quality.character_count}")
        print(f"Text blocks      : {quality.text_block_count}")
        print(f"Tables           : {quality.table_count}")
        print(f"Keyword coverage : {quality.keyword_coverage}")
        print(f"Quality score    : {quality.quality_score}")
        print(f"Fallback needed  : {quality.requires_fallback}")


if __name__ == "__main__":
    main()