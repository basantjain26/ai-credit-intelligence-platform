from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from src.borrower_intelligence.models import (
    BorrowerCaseContext,
)


@dataclass
class BorrowerSignals:
    existing_exposure: Decimal
    requested_amount: Decimal
    potential_post_loan_exposure: Decimal

    loan_count: int
    director_count: int
    related_party_count: int
    high_risk_related_party_count: int

    relationship_years: float | None

    latest_financial_year: str | None
    audited_revenue: Decimal | None
    declared_revenue: Decimal | None

    revenue_difference: Decimal | None
    revenue_difference_pct: Decimal | None

    revenue_mismatch: bool

    missing_information: list[str]


class BorrowerSignalEngine:

    def calculate(
        self,
        context: BorrowerCaseContext,
    ) -> BorrowerSignals:

        existing_exposure = (
            self._calculate_existing_exposure(
                context.loans
            )
        )

        requested_amount = (
            self._get_requested_amount(
                context.application
            )
        )

        potential_post_loan_exposure = (
            existing_exposure
            + requested_amount
        )

        high_risk_related_party_count = (
            self._count_high_risk_related_parties(
                context.related_parties
            )
        )

        relationship_years = (
            self._calculate_relationship_years(
                context.customer
            )
        )

        latest_financial = (
            self._get_latest_financial_statement(
                context.financial_statements
            )
        )

        audited_revenue = None
        latest_financial_year = None

        if latest_financial:

            audited_revenue = (
                self._extract_decimal(
                    latest_financial,
                    [
                        "revenue",
                        "total_revenue",
                        "audited_revenue",
                    ],
                )
            )

            latest_financial_year = (
                self._extract_string(
                    latest_financial,
                    [
                        "fiscal_year",
                        "financial_year",
                        "period",
                    ],
                )
            )

        declared_revenue = (
            self._extract_decimal(
                context.application,
                [
                    "declared_revenue",
                    "annual_revenue",
                    "revenue",
                    "reported_revenue",
                ],
            )
        )

        revenue_difference = None
        revenue_difference_pct = None
        revenue_mismatch = False

        if (
            declared_revenue is not None
            and audited_revenue is not None
        ):

            revenue_difference = (
                declared_revenue
                - audited_revenue
            )

            if audited_revenue != 0:

                revenue_difference_pct = (
                    revenue_difference
                    / audited_revenue
                    * Decimal("100")
                )

            revenue_mismatch = (
                revenue_difference != 0
            )

        missing_information = (
            self._detect_missing_information(
                context=context,
                audited_revenue=audited_revenue,
                declared_revenue=declared_revenue,
            )
        )

        return BorrowerSignals(
            existing_exposure=existing_exposure,
            requested_amount=requested_amount,
            potential_post_loan_exposure=(
                potential_post_loan_exposure
            ),

            loan_count=len(context.loans),
            director_count=len(context.directors),
            related_party_count=(
                len(context.related_parties)
            ),

            high_risk_related_party_count=(
                high_risk_related_party_count
            ),

            relationship_years=relationship_years,

            latest_financial_year=(
                latest_financial_year
            ),

            audited_revenue=audited_revenue,
            declared_revenue=declared_revenue,

            revenue_difference=(
                revenue_difference
            ),

            revenue_difference_pct=(
                revenue_difference_pct
            ),

            revenue_mismatch=(
                revenue_mismatch
            ),

            missing_information=(
                missing_information
            ),
        )

    def _calculate_existing_exposure(
        self,
        loans: list[dict[str, Any]],
    ) -> Decimal:

        total = Decimal("0")

        for loan in loans:

            amount = self._extract_decimal(
                loan,
                [
                    "outstanding_amount",
                    "outstanding_balance",
                    "current_balance",
                    "principal_outstanding",
                ],
            )

            if amount is not None:
                total += amount

        return total

    def _get_requested_amount(
        self,
        application: dict[str, Any],
    ) -> Decimal:

        value = self._extract_decimal(
            application,
            [
                "requested_amount",
                "loan_amount",
                "facility_amount",
                "requested_loan_amount",
            ],
        )

        if value is None:
            return Decimal("0")

        return value

    def _count_high_risk_related_parties(
        self,
        related_parties: list[
            dict[str, Any]
        ],
    ) -> int:

        count = 0

        for party in related_parties:

            risk_value = (
                self._extract_string(
                    party,
                    [
                        "risk_level",
                        "risk_rating",
                        "risk_category",
                    ],
                )
            )

            if (
                risk_value
                and risk_value.upper()
                in {
                    "HIGH",
                    "HIGH_RISK",
                    "CRITICAL",
                }
            ):
                count += 1

        return count

    def _calculate_relationship_years(
        self,
        customer: dict[str, Any],
    ) -> float | None:

        relationship_start = None

        for key in [
            "relationship_start_date",
            "customer_since",
            "relationship_since",
            "created_at",
        ]:

            value = customer.get(key)

            if value is not None:
                relationship_start = value
                break

        if relationship_start is None:
            return None

        start_date = (
            self._to_date(
                relationship_start
            )
        )

        if start_date is None:
            return None

        today = date.today()

        days = (
            today - start_date
        ).days

        if days < 0:
            return None

        return round(
            days / 365.25,
            1,
        )

    def _get_latest_financial_statement(
        self,
        financials: list[
            dict[str, Any]
        ],
    ) -> dict[str, Any] | None:

        if not financials:
            return None

        # Repository already orders
        # financial statements DESC.
        return financials[0]

    def _detect_missing_information(
        self,
        context: BorrowerCaseContext,
        audited_revenue: Decimal | None,
        declared_revenue: Decimal | None,
    ) -> list[str]:

        missing = []

        if not context.directors:
            missing.append(
                "No director information available"
            )

        if not context.financial_statements:
            missing.append(
                "No financial statements available"
            )

        if audited_revenue is None:
            missing.append(
                "Audited revenue not available"
            )

        if declared_revenue is None:
            missing.append(
                "Application-declared revenue "
                "not available"
            )

        if not context.documents:
            missing.append(
                "No borrower documents registered"
            )

        return missing

    @staticmethod
    def _extract_decimal(
        record: dict[str, Any],
        possible_keys: list[str],
    ) -> Decimal | None:

        for key in possible_keys:

            value = record.get(key)

            if value is None:
                continue

            try:

                cleaned = (
                    str(value)
                    .replace(",", "")
                    .strip()
                )

                return Decimal(cleaned)

            except (
                InvalidOperation,
                ValueError,
            ):
                continue

        return None

    @staticmethod
    def _extract_string(
        record: dict[str, Any],
        possible_keys: list[str],
    ) -> str | None:

        for key in possible_keys:

            value = record.get(key)

            if value is not None:
                return str(value)

        return None

    @staticmethod
    def _to_date(
        value: Any,
    ) -> date | None:

        if isinstance(
            value,
            datetime,
        ):
            return value.date()

        if isinstance(
            value,
            date,
        ):
            return value

        if isinstance(
            value,
            str,
        ):

            for format_string in [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d-%m-%Y",
            ]:

                try:

                    return datetime.strptime(
                        value,
                        format_string,
                    ).date()

                except ValueError:
                    continue

        return None