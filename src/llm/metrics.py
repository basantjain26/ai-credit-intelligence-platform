from dataclasses import dataclass
from src.document_intelligence.schemas import FinancialDocumentExtraction


@dataclass
class LLMCallMetrics:
    model: str
    latency_seconds: float

    input_tokens: int
    output_tokens: int
    total_tokens: int

    estimated_cost_usd: float

@dataclass
class FinancialExtractionResult:
    extraction: FinancialDocumentExtraction
    metrics: LLMCallMetrics
