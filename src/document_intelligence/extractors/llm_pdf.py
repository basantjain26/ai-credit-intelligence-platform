import time
from pathlib import Path

import pymupdf
from openai import OpenAI

from src.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

from src.document_intelligence.aggregation.document_aggregator import (
    DocumentExtractionResult,
    FinancialDocumentAggregator,
)

from src.document_intelligence.rendering.pdf_renderer import (
    PDFRenderer,
)

from src.document_intelligence.schemas import (
    FinancialDocumentExtraction,
)

from src.llm.metrics import (
    FinancialExtractionResult,
    LLMCallMetrics,
)

from src.llm.pricing import (
    estimate_cost,
)


class LLMPDFExtractor:

    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        self.renderer = PDFRenderer()

    def extract_page(
        self,
        file_path: Path,
        page_number: int,
    ) -> FinancialExtractionResult:

        # ---------------------------------------------------------
        # 1. Render the requested PDF page into an image
        # ---------------------------------------------------------

        rendered_page = self.renderer.render_page(
            file_path=file_path,
            page_number=page_number,
        )

        # ---------------------------------------------------------
        # 2. Convert the rendered image into an inline data URL
        # ---------------------------------------------------------

        image_url = (
            f"data:{rendered_page.mime_type};base64,"
            f"{rendered_page.base64_data}"
        )

        # ---------------------------------------------------------
        # 3. Measure LLM request latency
        # ---------------------------------------------------------

        start_time = time.perf_counter()

        # ---------------------------------------------------------
        # 4. Send multimodal request to OpenAI
        # ---------------------------------------------------------

        response = self.client.responses.create(
            model=OPENAI_MODEL,

            instructions=(
                "You are a financial document extraction system. "
                "Extract only information that is visibly present "
                "in the supplied document image. "
                "Do not infer, estimate, calculate, or invent "
                "missing values. "
                "Preserve financial values exactly as displayed "
                "in the document. "
                "If a nullable field is not present, return null. "
                "Do not normalize, convert, or reinterpret units. "
                "Preserve reporting periods exactly as shown. "
                "For financial metrics, include the source text "
                "that supports the extracted value whenever possible."
            ),

            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Extract all relevant financial information "
                                f"from page {page_number}. "
                                "Capture visible section headings, text, "
                                "tables, reporting periods, financial metrics, "
                                "values, and units."
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": image_url,
                            "detail": "high",
                        },
                    ],
                }
            ],

            text={
                "format": {
                    "type": "json_schema",
                    "name": "financial_document_extraction",
                    "strict": True,
                    "schema": (
                        FinancialDocumentExtraction
                        .model_json_schema()
                    ),
                }
            },
        )

        latency_seconds = (
            time.perf_counter() - start_time
        )

        # ---------------------------------------------------------
        # 5. Validate that the model actually returned content
        # ---------------------------------------------------------

        if not response.output_text:
            raise RuntimeError(
                f"LLM returned an empty response "
                f"for page {page_number}."
            )

        # ---------------------------------------------------------
        # 6. Validate the returned JSON using Pydantic
        # ---------------------------------------------------------

        extraction = (
            FinancialDocumentExtraction
            .model_validate_json(
                response.output_text
            )
        )

        # ---------------------------------------------------------
        # 7. Read token usage
        # ---------------------------------------------------------

        input_tokens = 0
        output_tokens = 0
        total_tokens = 0

        if response.usage is not None:

            input_tokens = (
                response.usage.input_tokens
                or 0
            )

            output_tokens = (
                response.usage.output_tokens
                or 0
            )

            total_tokens = (
                response.usage.total_tokens
                or 0
            )

        # ---------------------------------------------------------
        # 8. Estimate call cost
        # ---------------------------------------------------------

        estimated_cost = estimate_cost(
            model=OPENAI_MODEL,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        # ---------------------------------------------------------
        # 9. Build operational metrics
        # ---------------------------------------------------------

        metrics = LLMCallMetrics(
            model=OPENAI_MODEL,
            latency_seconds=latency_seconds,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost,
        )

        # ---------------------------------------------------------
        # 10. Return business output + operational metrics
        # ---------------------------------------------------------

        return FinancialExtractionResult(
            extraction=extraction,
            metrics=metrics,
        )

    def extract_document(
        self,
        file_path: Path,
    ) -> DocumentExtractionResult:

        # ---------------------------------------------------------
        # 1. Determine PDF page count
        # ---------------------------------------------------------

        pdf = pymupdf.open(
            file_path
        )

        try:
            page_count = len(pdf)

        finally:
            pdf.close()

        if page_count == 0:
            raise ValueError(
                f"PDF contains no pages: {file_path}"
            )

        # ---------------------------------------------------------
        # 2. Extract every page independently
        # ---------------------------------------------------------

        page_results = []

        for page_number in range(
            1,
            page_count + 1,
        ):

            print(
                f"Extracting page "
                f"{page_number}/{page_count}"
            )

            try:
                page_result = (
                    self.extract_page(
                        file_path=file_path,
                        page_number=page_number,
                    )
                )

            except Exception as exc:
                raise RuntimeError(
                    f"LLM extraction failed "
                    f"for page {page_number} "
                    f"of {file_path.name}"
                ) from exc

            page_results.append(
                page_result
            )

        # ---------------------------------------------------------
        # 3. Aggregate page-level results deterministically
        # ---------------------------------------------------------

        aggregator = (
            FinancialDocumentAggregator()
        )

        document_result = (
            aggregator.aggregate(
                page_results
            )
        )

        return document_result