from dataclasses import dataclass
from typing import Dict

from src.document_intelligence.schemas import FinancialDocumentExtraction


@dataclass
class MetricValidationResult:
    metric_name: str
    expected_value: str
    extracted_value: str | None
    matched: bool


@dataclass
class LLMExtractionQuality:
    total_metrics: int
    matched_metrics: int
    accuracy: float
    results: list[MetricValidationResult]


class LLMExtractionQualityEvaluator:

    def evaluate(
        self,
        extraction: FinancialDocumentExtraction,
        expected_metrics: Dict[str, str],
    ) -> LLMExtractionQuality:

        extracted_metrics = {
            metric.metric_name.strip().lower(): metric.value.strip()
            for metric in extraction.financial_metrics
        }

        results = []
        matched_count = 0

        for metric_name, expected_value in expected_metrics.items():

            extracted_value = extracted_metrics.get(
                metric_name.strip().lower()
            )

            matched = (
                extracted_value is not None
                and extracted_value == expected_value
            )

            if matched:
                matched_count += 1

            results.append(
                MetricValidationResult(
                    metric_name=metric_name,
                    expected_value=expected_value,
                    extracted_value=extracted_value,
                    matched=matched,
                )
            )

        total_metrics = len(expected_metrics)

        accuracy = (
            matched_count / total_metrics
            if total_metrics > 0
            else 0.0
        )

        return LLMExtractionQuality(
            total_metrics=total_metrics,
            matched_metrics=matched_count,
            accuracy=accuracy,
            results=results,
        )