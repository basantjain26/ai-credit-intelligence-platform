from pathlib import Path

from src.document_intelligence.extractors.llm_pdf import (
    LLMPDFExtractor,
)


PDF_PATH = Path(
    "data/source/documents/financial_statements/"
    "ABC_FY2026_Audited_Financials_SCANNED.pdf"
)


def main():

    extractor = LLMPDFExtractor()

    result = extractor.extract_document(
        file_path=PDF_PATH
    )

    print(
        "\n========== DOCUMENT EXTRACTION ==========\n"
    )

    print(
        result.extraction.model_dump_json(
            indent=2
        )
    )

    print(
        "\n========== DOCUMENT METRICS ==========\n"
    )

    print(
        "Pages processed:",
        result.pages_processed,
    )

    print(
        "Model:",
        result.metrics.model,
    )

    print(
        "Total latency:",
        round(
            result.metrics.latency_seconds,
            2,
        ),
        "seconds",
    )

    print(
        "Input tokens:",
        result.metrics.input_tokens,
    )

    print(
        "Output tokens:",
        result.metrics.output_tokens,
    )

    print(
        "Total tokens:",
        result.metrics.total_tokens,
    )

    print(
        "Estimated cost: $",
        round(
            result.metrics.estimated_cost_usd,
            6,
        ),
    )

    print(
        "\n========== FINANCIAL METRICS ==========\n"
    )

    for metric in (
        result.extraction.financial_metrics
    ):

        print(
            f"Page {metric.page_number} | "
            f"{metric.metric_name} = "
            f"{metric.value} "
            f"{metric.unit or ''} "
            f"({metric.period or 'N/A'})"
        )


if __name__ == "__main__":
    main()