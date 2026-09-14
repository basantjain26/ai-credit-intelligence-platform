from src.document_intelligence.normalization.financial_value import (
    FinancialValueNormalizer,
)


TEST_VALUES = [
    ("790", None),
    ("790.0", None),
    ("1,250.50", None),
    ("(125)", None),
    ("95%", None),
    ("₹790 Mn", None),
    ("790 million", None),
    ("1.2 Cr", None),
    ("5 lakh", None),
    ("790", "INR million"),
]


def main():

    normalizer = (
        FinancialValueNormalizer()
    )

    for raw_value, unit in TEST_VALUES:

        result = normalizer.normalize(
            raw_value=raw_value,
            unit=unit,
        )

        print(
            f"{raw_value!r:20} "
            f"unit={unit!r:15} "
            f"-> "
            f"value={result.numeric_value}, "
            f"normalized_unit="
            f"{result.normalized_unit}, "
            f"success="
            f"{result.successfully_normalized}"
        )


if __name__ == "__main__":
    main()