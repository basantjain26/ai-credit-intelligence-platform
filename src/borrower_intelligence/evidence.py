from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvidenceRecord:
    evidence_id: str

    source_type: str
    source_name: str

    tool_name: str

    document_id: str | None = None
    document_name: str | None = None
    page_number: int | None = None

    content: Any = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )