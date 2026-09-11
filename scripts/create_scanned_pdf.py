from pathlib import Path
import fitz


SOURCE = Path(
    "data/source/documents/financial_statements/"
    "ABC_FY2026_Audited_Financials.pdf"
)

OUTPUT = Path(
    "data/source/documents/financial_statements/"
    "ABC_FY2026_Audited_Financials_SCANNED.pdf"
)


def main():
    source_pdf = fitz.open(SOURCE)
    output_pdf = fitz.open()

    try:
        for page in source_pdf:
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False,
            )

            image_bytes = pixmap.tobytes("png")

            new_page = output_pdf.new_page(
                width=page.rect.width,
                height=page.rect.height,
            )

            new_page.insert_image(
                new_page.rect,
                stream=image_bytes,
            )

        output_pdf.save(OUTPUT)

    finally:
        source_pdf.close()
        output_pdf.close()

    print(f"Created scanned PDF: {OUTPUT}")


if __name__ == "__main__":
    main()