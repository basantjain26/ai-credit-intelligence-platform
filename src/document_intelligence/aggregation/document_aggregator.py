from dataclasses import dataclass
from typing import List

from src.document_intelligence.schemas import (
    FinancialDocumentExtraction,
    FinancialMetric,
    DocumentSection,
)
from src.llm.metrics import LLMCallMetrics


@dataclass
class DocumentExtractionResult:
    extraction: FinancialDocumentExtraction
    metrics: LLMCallMetrics
    pages_processed: int


class FinancialDocumentAggregator:

    def aggregate(
        self,
        page_results: List,
    ) -> DocumentExtractionResult:

        if not page_results:
            raise ValueError(
                "Cannot aggregate an empty list of page results."
            )

        all_sections: List[DocumentSection] = []
        all_metrics: List[FinancialMetric] = []

        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0
        total_latency = 0.0
        total_cost = 0.0

        document_types = []

        for result in page_results:

            extraction = result.extraction
            metrics = result.metrics

            document_types.append(
                extraction.document_type
            )

            all_sections.extend(
                extraction.sections
            )

            all_metrics.extend(
                extraction.financial_metrics
            )

            total_input_tokens += (
                metrics.input_tokens
            )

            total_output_tokens += (
                metrics.output_tokens
            )

            total_tokens += (
                metrics.total_tokens
            )

            total_latency += (
                metrics.latency_seconds
            )

            total_cost += (
                metrics.estimated_cost_usd
            )

        document_type = self._resolve_document_type(
            document_types
        )

        aggregated_extraction = (
            FinancialDocumentExtraction(
                document_type=document_type,

                # This is now document-level, not a single page.
                # We use 0 to represent aggregated document scope.
                page_number=0,

                sections=all_sections,
                financial_metrics=all_metrics,
            )
        )

        aggregated_metrics = LLMCallMetrics(
            model=page_results[0].metrics.model,
            latency_seconds=total_latency,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=total_cost,
        )

        return DocumentExtractionResult(
            extraction=aggregated_extraction,
            metrics=aggregated_metrics,
            pages_processed=len(page_results),
        )

    @staticmethod
    def _resolve_document_type(
        document_types: List[str],
    ) -> str:

        if not document_types:
            return "UNKNOWN"

        normalized = [
            document_type
            for document_type in document_types
            if document_type
        ]

        if not normalized:
            return "UNKNOWN"

        return max(
            set(normalized),
            key=normalized.count,
        )