import base64
from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass
class RenderedPage:
    page_number: int
    image_bytes: bytes
    mime_type: str
    base64_data: str


class PDFRenderer:

    def render_page(
        self,
        file_path: Path,
        page_number: int,
        dpi: int = 200,
    ) -> RenderedPage:

        document = pymupdf.open(file_path)

        try:
            if (
                page_number < 1
                or page_number > len(document)
            ):
                raise ValueError(
                    f"Invalid page number {page_number}. "
                    f"PDF contains {len(document)} pages."
                )

            page = document[
                page_number - 1
            ]

            pixmap = page.get_pixmap(
                dpi=dpi,
                alpha=False,
            )

            image_bytes = (
                pixmap.tobytes("png")
            )

            base64_data = (
                base64.b64encode(
                    image_bytes
                )
                .decode("utf-8")
            )

            return RenderedPage(
                page_number=page_number,
                image_bytes=image_bytes,
                mime_type="image/png",
                base64_data=base64_data,
            )

        finally:
            document.close()