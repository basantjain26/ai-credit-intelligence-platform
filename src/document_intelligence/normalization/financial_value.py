import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional


@dataclass
class NormalizedFinancialValue:
    raw_value: str

    numeric_value: Optional[Decimal]

    normalized_unit: Optional[str]

    multiplier: Decimal

    is_percentage: bool

    successfully_normalized: bool


class FinancialValueNormalizer:

    MULTIPLIERS = {
        "k": Decimal("1000"),
        "thousand": Decimal("1000"),

        "lakh": Decimal("100000"),
        "lac": Decimal("100000"),

        "m": Decimal("1000000"),
        "mn": Decimal("1000000"),
        "million": Decimal("1000000"),

        "cr": Decimal("10000000"),
        "crore": Decimal("10000000"),

        "b": Decimal("1000000000"),
        "bn": Decimal("1000000000"),
        "billion": Decimal("1000000000"),
    }

    NULL_VALUES = {
        "",
        "-",
        "na",
        "n/a",
        "none",
        "null",
    }

    def normalize(
        self,
        raw_value: str,
        unit: Optional[str] = None,
    ) -> NormalizedFinancialValue:

        if raw_value is None:
            return self._failed("")

        original_value = str(raw_value).strip()

        if original_value.lower() in self.NULL_VALUES:
            return self._failed(
                original_value
            )

        working_value = (
            original_value
            .strip()
            .lower()
        )

        is_percentage = "%" in working_value

        # Remove currency symbols
        working_value = (
            working_value
            .replace("₹", "")
            .replace("$", "")
            .replace("€", "")
            .replace("£", "")
        )

        negative = False

        # Accounting-style negatives:
        # (125) -> -125
        if (
            working_value.startswith("(")
            and working_value.endswith(")")
        ):
            negative = True

            working_value = (
                working_value[1:-1]
                .strip()
            )

        # Remove commas
        working_value = (
            working_value
            .replace(",", "")
        )

        multiplier = Decimal("1")

        detected_unit = None

        # Check explicit unit parameter first
        unit_text = (
            unit.lower().strip()
            if unit
            else ""
        )

        multiplier_from_unit = (
            self._find_multiplier(
                unit_text
            )
        )

        if multiplier_from_unit:
            multiplier = (
                multiplier_from_unit[1]
            )

            detected_unit = (
                multiplier_from_unit[0]
            )

        else:
            multiplier_from_value = (
                self._find_multiplier(
                    working_value
                )
            )

            if multiplier_from_value:
                detected_unit = (
                    multiplier_from_value[0]
                )

                multiplier = (
                    multiplier_from_value[1]
                )

        # Remove textual unit words
        working_value = (
            self._remove_multiplier_words(
                working_value
            )
        )

        # Remove percentage symbol
        working_value = (
            working_value
            .replace("%", "")
            .strip()
        )

        # Extract numeric content
        match = re.search(
            r"-?\d+(?:\.\d+)?",
            working_value,
        )

        if not match:
            return self._failed(
                original_value
            )

        try:
            numeric_value = Decimal(
                match.group()
            )

        except InvalidOperation:
            return self._failed(
                original_value
            )

        if negative:
            numeric_value = (
                -abs(numeric_value)
            )

        numeric_value *= multiplier

        if is_percentage:
            numeric_value /= Decimal("100")

            detected_unit = "PERCENT"

        return NormalizedFinancialValue(
            raw_value=original_value,
            numeric_value=numeric_value,
            normalized_unit=detected_unit,
            multiplier=multiplier,
            is_percentage=is_percentage,
            successfully_normalized=True,
        )

    def _find_multiplier(
        self,
        text: str,
    ):
        if not text:
            return None

        normalized = (
            text.lower()
            .replace(".", "")
        )

        for (
            keyword,
            multiplier,
        ) in self.MULTIPLIERS.items():

            pattern = (
                rf"\b{re.escape(keyword)}\b"
            )

            if re.search(
                pattern,
                normalized,
            ):
                return (
                    keyword,
                    multiplier,
                )

        return None

    def _remove_multiplier_words(
        self,
        value: str,
    ) -> str:

        cleaned = value

        for keyword in self.MULTIPLIERS:

            cleaned = re.sub(
                rf"\b{re.escape(keyword)}\b",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )

        return cleaned.strip()

    @staticmethod
    def _failed(
        raw_value: str,
    ) -> NormalizedFinancialValue:

        return NormalizedFinancialValue(
            raw_value=raw_value,
            numeric_value=None,
            normalized_unit=None,
            multiplier=Decimal("1"),
            is_percentage=False,
            successfully_normalized=False,
        )