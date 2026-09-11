from pathlib import Path

from src.document_intelligence.rendering.pdf_renderer import PDFRenderer


PDF_PATH = Path(
    "data/source/documents/financial_statements/"
    "ABC_FY2026_Audited_Financials_SCANNED.pdf"
)


def main():
    renderer = PDFRenderer()

    page = renderer.render_page(
        file_path=PDF_PATH,
        page_number=1,
    )

    print("Page:", page.page_number)
    print("MIME type:", page.mime_type)
    print("Image bytes:", len(page.image_bytes))
    print("Base64 characters:", len(page.base64_data))
    print("Base64 preview:", page.base64_data[:100])


if __name__ == "__main__":
    main()