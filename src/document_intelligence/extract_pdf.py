from pathlib import Path
import json

from src.document_intelligence.extractors.pdf import PDFExtractor


def main():

    file_path = Path(
        "data/source/documents/"
        "financial_statements/"
        "ABC_FY2026_Audited_Financials.pdf"
    )

    extractor = PDFExtractor()

    result = extractor.extract(
        file_path=file_path,
        document_id="TEST_DOC_001",
    )

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()