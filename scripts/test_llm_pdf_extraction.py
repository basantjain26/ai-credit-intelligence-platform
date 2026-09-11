from pathlib import Path

from src.document_intelligence.extractors.llm_pdf import (
    LLMPDFExtractor,
)
from src.document_intelligence.quality.llm_evaluator import (
    LLMExtractionQualityEvaluator,
)


PDF_PATH = Path(
    "data/source/documents/financial_statements/"
    "ABC_FY2026_Audited_Financials_SCANNED.pdf"
)


# IMPORTANT:
# Keep only the metrics that are actually visible on each page.
# Adjust these page numbers after checking the PDF.
PAGE_EXPECTATIONS = {
    2: {
        "Revenue": "790",
        "EBITDA": "95",
        "Net Income": "39",
    },
    3: {
        "Total Debt": "125",
        "Operating Cash Flow": "57",
    },
}


def print_llm_metrics(result) -> None:
    print("\n========== LLM METRICS ==========\n")

    print(
        "Model:",
        result.metrics.model,
    )

    print(
        "Latency:",
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


def print_quality_results(quality) -> None:
    print(
        "\n========== EXTRACTION QUALITY ==========\n"
    )

    for item in quality.results:

        status = (
            "PASS"
            if item.matched
            else "FAIL"
        )

        print(
            f"[{status}] "
            f"{item.metric_name}: "
            f"expected={item.expected_value}, "
            f"extracted={item.extracted_value}"
        )

    print(
        "\nMatched metrics:",
        f"{quality.matched_metrics}/"
        f"{quality.total_metrics}",
    )

    print(
        "Accuracy:",
        f"{quality.accuracy * 100:.2f}%",
    )


def main():
    extractor = LLMPDFExtractor()

    evaluator = (
        LLMExtractionQualityEvaluator()
    )

    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    total_cost = 0.0
    total_latency = 0.0

    total_expected_metrics = 0
    total_matched_metrics = 0

    for (
        page_number,
        expected_metrics,
    ) in PAGE_EXPECTATIONS.items():

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"PROCESSING PAGE {page_number}"
        )

        print(
            "=" * 70
        )

        result = extractor.extract_page(
            file_path=PDF_PATH,
            page_number=page_number,
        )

        print(
            "\n========== EXTRACTION ==========\n"
        )

        print(
            result.extraction.model_dump_json(
                indent=2
            )
        )

        print_llm_metrics(
            result
        )

        quality = evaluator.evaluate(
            extraction=result.extraction,
            expected_metrics=expected_metrics,
        )

        print_quality_results(
            quality
        )

        # Aggregate operational metrics
        total_input_tokens += (
            result.metrics.input_tokens
        )

        total_output_tokens += (
            result.metrics.output_tokens
        )

        total_tokens += (
            result.metrics.total_tokens
        )

        total_cost += (
            result.metrics.estimated_cost_usd
        )

        total_latency += (
            result.metrics.latency_seconds
        )

        # Aggregate extraction quality
        total_expected_metrics += (
            quality.total_metrics
        )

        total_matched_metrics += (
            quality.matched_metrics
        )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "DOCUMENT-LEVEL SUMMARY"
    )

    print(
        "=" * 70
    )

    print(
        "\nPages evaluated:",
        len(PAGE_EXPECTATIONS),
    )

    print(
        "Total input tokens:",
        total_input_tokens,
    )

    print(
        "Total output tokens:",
        total_output_tokens,
    )

    print(
        "Total tokens:",
        total_tokens,
    )

    print(
        "Total latency:",
        round(
            total_latency,
            2,
        ),
        "seconds",
    )

    print(
        "Total estimated cost: $",
        round(
            total_cost,
            6,
        ),
    )

    document_accuracy = (
        total_matched_metrics
        / total_expected_metrics
        if total_expected_metrics > 0
        else 0.0
    )

    print(
        "\nTotal expected metrics:",
        total_expected_metrics,
    )

    print(
        "Total matched metrics:",
        total_matched_metrics,
    )

    print(
        "Document extraction accuracy:",
        f"{document_accuracy * 100:.2f}%",
    )


if __name__ == "__main__":
    main()