from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )


class TableData(StrictBaseModel):
    title: Optional[str]
    columns: List[str]
    rows: List[List[str]]


class FinancialMetric(StrictBaseModel):
    metric_name: str
    value: str
    unit: Optional[str]
    period: Optional[str]
    page_number: int
    source_text: Optional[str]


class DocumentSection(StrictBaseModel):
    section_title: Optional[str]
    text: Optional[str]
    tables: List[TableData]


class FinancialDocumentExtraction(StrictBaseModel):
    document_type: str
    page_number: int
    sections: List[DocumentSection]
    financial_metrics: List[FinancialMetric]