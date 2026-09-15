from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


@dataclass
class CanonicalFinancialMetric:
    canonical_name: str
    value: Decimal | None
    raw_name: str
    raw_value: Any
    source_type: str
    fiscal_year: int | None = None
    unit: str | None = None
    currency: str | None = None


class CanonicalMetricMapper:
    """
    Maps source-specific financial field names into a stable
    canonical vocabulary used across financial analysis.

    This layer performs terminology normalization only.

    It does not:
    - reconcile conflicting values
    - calculate financial ratios
    - calculate trends
    - decide which source is authoritative
    - perform LLM reasoning
    """

    METRIC_ALIASES = {
        "revenue": {
            "revenue",
            "sales",
            "net_sales",
            "net_revenue",
            "total_revenue",
            "turnover",
            "operating_revenue",
            "revenue_from_operations",
        },
        "ebitda": {
            "ebitda",
            "earnings_before_interest_tax_depreciation_amortization",
            "earnings_before_interest_taxes_depreciation_and_amortization",
        },
        "ebit": {
            "ebit",
            "operating_profit",
            "operating_income",
            "profit_before_interest_and_tax",
        },
        "net_income": {
            "net_income",
            "net_profit",
            "profit_after_tax",
            "pat",
            "profit_for_the_year",
            "profit_for_year",
        },
        "total_debt": {
            "total_debt",
            "debt",
            "borrowings",
            "total_borrowings",
            "interest_bearing_debt",
            "interest_bearing_borrowings",
        },
        "short_term_debt": {
            "short_term_debt",
            "short_term_borrowings",
            "current_borrowings",
            "current_debt",
        },
        "long_term_debt": {
            "long_term_debt",
            "long_term_borrowings",
            "non_current_borrowings",
            "noncurrent_borrowings",
        },
        "total_assets": {
            "total_assets",
            "assets",
        },
        "current_assets": {
            "current_assets",
            "total_current_assets",
        },
        "current_liabilities": {
            "current_liabilities",
            "total_current_liabilities",
        },
        "total_liabilities": {
            "total_liabilities",
            "liabilities",
        },
        "equity": {
            "equity",
            "shareholders_equity",
            "shareholder_equity",
            "net_worth",
            "total_equity",
        },
        "cash_and_cash_equivalents": {
            "cash_and_cash_equivalents",
            "cash",
            "cash_equivalents",
            "cash_balance",
        },
        "interest_expense": {
            "interest_expense",
            "finance_cost",
            "finance_costs",
            "interest_cost",
            "interest_paid",
        },
        "depreciation_amortization": {
            "depreciation_amortization",
            "depreciation_and_amortization",
            "depreciation",
            "d_and_a",
        },
        "operating_cash_flow": {
            "operating_cash_flow",
            "cash_flow_from_operations",
            "cash_from_operations",
            "net_cash_from_operating_activities",
            "cash_generated_from_operations",
        },
        "capital_expenditure": {
            "capital_expenditure",
            "capex",
            "capital_expenditures",
            "purchase_of_property_plant_equipment",
        },
        "inventory": {
            "inventory",
            "inventories",
            "stock",
        },
        "accounts_receivable": {
            "accounts_receivable",
            "trade_receivables",
            "receivables",
            "trade_debtors",
        },
        "accounts_payable": {
            "accounts_payable",
            "trade_payables",
            "payables",
            "trade_creditors",
        },
        "tax_expense": {
            "tax_expense",
            "income_tax_expense",
            "taxation",
        },
        "debt_service": {
            "debt_service",
            "total_debt_service",
            "principal_and_interest",
            "principal_interest_payments",
        },
    }

    def __init__(self):
        self.alias_to_canonical = self._build_alias_index()

    def canonicalize_name(
        self,
        raw_name: str,
    ) -> str | None:
        """
        Convert a source-specific field name into a canonical
        metric name.

        Unknown metrics return None rather than being guessed.
        """

        normalized_name = self._normalize_name(
            raw_name
        )

        return self.alias_to_canonical.get(
            normalized_name
        )

    def map_metric(
        self,
        raw_name: str,
        raw_value: Any,
        source_type: str,
        fiscal_year: int | None = None,
        unit: str | None = None,
        currency: str | None = None,
    ) -> CanonicalFinancialMetric | None:
        """
        Map one raw financial observation into the canonical model.
        """

        canonical_name = self.canonicalize_name(
            raw_name
        )

        if canonical_name is None:
            return None

        value = self._to_decimal(
            raw_value
        )

        return CanonicalFinancialMetric(
            canonical_name=canonical_name,
            value=value,
            raw_name=raw_name,
            raw_value=raw_value,
            source_type=source_type,
            fiscal_year=fiscal_year,
            unit=unit,
            currency=currency,
        )

    def map_record(
        self,
        record: dict[str, Any],
        source_type: str,
        fiscal_year: int | None = None,
        excluded_fields: set[str] | None = None,
    ) -> list[CanonicalFinancialMetric]:
        """
        Map all recognized financial fields in one dictionary.

        Non-financial metadata fields are ignored.
        """

        excluded_fields = excluded_fields or set()

        mapped_metrics = []

        for raw_name, raw_value in record.items():

            if raw_name in excluded_fields:
                continue

            metric = self.map_metric(
                raw_name=raw_name,
                raw_value=raw_value,
                source_type=source_type,
                fiscal_year=fiscal_year,
            )

            if metric is not None:
                mapped_metrics.append(
                    metric
                )

        return mapped_metrics

    def get_supported_metrics(
        self,
    ) -> list[str]:
        """
        Return all canonical financial metrics supported
        by this mapper.
        """

        return sorted(
            self.METRIC_ALIASES.keys()
        )

    def _build_alias_index(
        self,
    ) -> dict[str, str]:

        alias_index = {}

        for canonical_name, aliases in (
            self.METRIC_ALIASES.items()
        ):

            alias_index[
                self._normalize_name(
                    canonical_name
                )
            ] = canonical_name

            for alias in aliases:
                normalized_alias = (
                    self._normalize_name(
                        alias
                    )
                )

                existing = alias_index.get(
                    normalized_alias
                )

                if (
                    existing is not None
                    and existing != canonical_name
                ):
                    raise ValueError(
                        "Financial metric alias collision: "
                        f"{alias} maps to both "
                        f"{existing} and "
                        f"{canonical_name}"
                    )

                alias_index[
                    normalized_alias
                ] = canonical_name

        return alias_index

    @staticmethod
    def _normalize_name(
        name: str,
    ) -> str:

        normalized = (
            name.strip()
            .lower()
            .replace("&", "and")
            .replace("/", "_")
            .replace("-", "_")
            .replace(" ", "_")
        )

        while "__" in normalized:
            normalized = normalized.replace(
                "__",
                "_",
            )

        return normalized.strip("_")

    @staticmethod
    def _to_decimal(
        value: Any,
    ) -> Decimal | None:

        if value is None:
            return None

        if isinstance(value, Decimal):
            return value

        if isinstance(value, bool):
            return None

        if isinstance(
            value,
            (int, float),
        ):
            return Decimal(
                str(value)
            )

        if isinstance(value, str):

            cleaned = (
                value.strip()
                .replace(",", "")
            )

            if not cleaned:
                return None

            try:
                return Decimal(
                    cleaned
                )
            except InvalidOperation:
                return None

        return None