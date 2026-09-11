from pathlib import Path

from src.document_intelligence.extractors.pdf import PDFExtractor


def main():
    file_path = Path(
        "data/source/documents/financial_statements/"
        "ABC_FY2026_Audited_Financials_SCANNED.pdf"
    )

    extractor = PDFExtractor()

    result = extractor.extract(
        file_path=file_path,
        document_id="TEST_SCANNED_001",
    )

    print(f"File: {result.file_name}")
    print(f"Blocks: {len(result.content_blocks)}")

    for block in result.content_blocks:
        print()
        print("Type:", block.block_type)
        print("Page:", block.page_number)

        if block.text:
            print("Characters:", len(block.text))
            print("Preview:", block.text[:200])

        if block.rows:
            print("Rows:", len(block.rows))


if __name__ == "__main__":
    main()