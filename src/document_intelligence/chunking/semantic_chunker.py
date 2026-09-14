from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from src.document_intelligence.schemas import (
    FinancialDocumentExtraction,
)


@dataclass
class SemanticChunk:
    chunk_id: str
    document_id: str
    chunk_type: str
    text: str
    page_number: int | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class FinancialDocumentChunker:

    def chunk(
        self,
        document_id: str,
        extraction: FinancialDocumentExtraction,
    ) -> list[SemanticChunk]:

        chunks: list[SemanticChunk] = []

        chunks.extend(
            self._chunk_sections(
                document_id=document_id,
                extraction=extraction,
            )
        )

        chunks.extend(
            self._chunk_financial_metrics(
                document_id=document_id,
                extraction=extraction,
            )
        )

        return chunks

    def _chunk_sections(
        self,
        document_id: str,
        extraction: FinancialDocumentExtraction,
    ) -> list[SemanticChunk]:

        chunks = []

        for section_index, section in enumerate(
            extraction.sections
        ):

            content = []

            if section.section_title:
                content.append(
                    f"Section: {section.section_title}"
                )

            if section.text:
                content.append(
                    section.text.strip()
                )

            for table in section.tables:

                table_text = (
                    self._table_to_text(
                        title=table.title,
                        columns=table.columns,
                        rows=table.rows,
                    )
                )

                if table_text:
                    content.append(
                        table_text
                    )

            text = "\n\n".join(
                item
                for item in content
                if item
            )

            if not text.strip():
                continue

            chunks.append(
                SemanticChunk(
                    chunk_id=str(uuid4()),
                    document_id=document_id,
                    chunk_type="SECTION",
                    text=text,
                    page_number=None,
                    metadata={
                        "section_index": section_index,
                        "section_title": (
                            section.section_title
                        ),
                    },
                )
            )

        return chunks

    def _chunk_financial_metrics(
        self,
        document_id: str,
        extraction: FinancialDocumentExtraction,
    ) -> list[SemanticChunk]:

        metrics_by_page = {}

        for metric in extraction.financial_metrics:

            metrics_by_page.setdefault(
                metric.page_number,
                [],
            ).append(metric)

        chunks = []

        for page_number, metrics in (
            metrics_by_page.items()
        ):

            lines = [
                "Financial Metrics"
            ]

            metric_names = []

            for metric in metrics:

                metric_names.append(
                    metric.metric_name
                )

                line = (
                    f"{metric.metric_name}: "
                    f"{metric.value}"
                )

                if metric.unit:
                    line += f" {metric.unit}"

                if metric.period:
                    line += (
                        f" | Period: {metric.period}"
                    )

                if metric.source_text:
                    line += (
                        f" | Source: "
                        f"{metric.source_text}"
                    )

                lines.append(line)

            chunks.append(
                SemanticChunk(
                    chunk_id=str(uuid4()),
                    document_id=document_id,
                    chunk_type=(
                        "FINANCIAL_METRICS"
                    ),
                    text="\n".join(lines),
                    page_number=page_number,
                    metadata={
                        "metric_names": (
                            metric_names
                        )
                    },
                )
            )

        return chunks

    @staticmethod
    def _table_to_text(
        title: str | None,
        columns: list[str],
        rows: list[list[str]],
    ) -> str:

        lines = []

        if title:
            lines.append(
                f"Table: {title}"
            )

        if columns:
            lines.append(
                " | ".join(
                    str(column)
                    for column in columns
                )
            )

        for row in rows:

            lines.append(
                " | ".join(
                    str(value)
                    for value in row
                )
            )

        return "\n".join(lines)