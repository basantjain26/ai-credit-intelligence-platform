from dataclasses import dataclass, field
from typing import Any


@dataclass
class BorrowerCaseContext:
    customer_id: str
    application_id: str

    customer: dict[str, Any]

    application: dict[str, Any]

    directors: list[dict[str, Any]] = field(
        default_factory=list
    )

    related_parties: list[dict[str, Any]] = field(
        default_factory=list
    )

    loans: list[dict[str, Any]] = field(
        default_factory=list
    )

    loan_payments: list[dict[str, Any]] = field(
        default_factory=list
    )

    bank_accounts: list[dict[str, Any]] = field(
        default_factory=list
    )

    financial_statements: list[dict[str, Any]] = field(
        default_factory=list
    )

    documents: list[dict[str, Any]] = field(
        default_factory=list
    )