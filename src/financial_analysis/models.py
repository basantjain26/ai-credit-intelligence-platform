from dataclasses import dataclass, field
from typing import Any


@dataclass
class FinancialAnalysisContext:
    customer_id: str
    application_id: str

    customer: dict[str, Any]
    application: dict[str, Any]

    financial_statements: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    existing_loans: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    loan_payments: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    financial_documents: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )