from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_PATH = Path(
    "data/ml/raw/historical_credit_applications.csv"
)

TARGET_COLUMN = "default_within_12m"

FEATURE_COLUMNS = [
    "company_age_years",
    "banking_relationship_years",
    "revenue",
    "ebitda_margin",
    "debt_to_ebitda",
    "dscr",
    "current_ratio",
    "credit_score",
    "existing_exposure",
    "past_due_count_12m",
    "bureau_inquiries_6m",
    "transaction_anomaly_rate",
    "related_party_transaction_ratio",
    "requested_amount",
]


def main() -> None:

    dataframe = pd.read_csv(DATA_PATH)

    print()
    print("=" * 80)
    print("CREDIT RISK DATASET ANALYSIS")
    print("=" * 80)

    #
    # 1. Dataset shape
    #
    print()
    print("1. DATASET SHAPE")
    print("-" * 80)

    print(f"Rows    : {len(dataframe):,}")
    print(f"Columns : {len(dataframe.columns)}")

    #
    # 2. Target distribution
    #
    print()
    print("2. TARGET DISTRIBUTION")
    print("-" * 80)

    target_counts = (
        dataframe[TARGET_COLUMN]
        .value_counts()
        .sort_index()
    )

    target_percentages = (
        dataframe[TARGET_COLUMN]
        .value_counts(normalize=True)
        .sort_index()
        * 100
    )

    for target_value in target_counts.index:

        label = (
            "DEFAULT"
            if target_value == 1
            else "NON-DEFAULT"
        )

        print(
            f"{label:<12}: "
            f"{target_counts[target_value]:>6,} "
            f"({target_percentages[target_value]:.2f}%)"
        )

    #
    # 3. Missing values
    #
    print()
    print("3. MISSING VALUES")
    print("-" * 80)

    missing_values = (
        dataframe[FEATURE_COLUMNS]
        .isna()
        .sum()
    )

    print(missing_values)

    #
    # 4. Feature statistics
    #
    print()
    print("4. FEATURE STATISTICS")
    print("-" * 80)

    print(
        dataframe[FEATURE_COLUMNS]
        .describe()
        .T[
            [
                "mean",
                "std",
                "min",
                "50%",
                "max",
            ]
        ]
        .round(3)
    )

    #
    # 5. Default vs non-default comparison
    #
    print()
    print("5. DEFAULT VS NON-DEFAULT")
    print("-" * 80)

    comparison = (
        dataframe.groupby(TARGET_COLUMN)[
            FEATURE_COLUMNS
        ]
        .mean()
        .T
    )

    comparison.columns = [
        "non_default_mean",
        "default_mean",
    ]

    comparison["difference"] = (
        comparison["default_mean"]
        - comparison["non_default_mean"]
    )

    print(
        comparison.round(3)
    )

    #
    # 6. Correlation with target
    #
    print()
    print("6. CORRELATION WITH DEFAULT")
    print("-" * 80)

    correlations = (
        dataframe[
            FEATURE_COLUMNS + [TARGET_COLUMN]
        ]
        .corr()[TARGET_COLUMN]
        .drop(TARGET_COLUMN)
        .sort_values(
            key=abs,
            ascending=False,
        )
    )

    print(
        correlations.round(4)
    )

    #
    # 7. Majority-class baseline accuracy
    #
    print()
    print("7. NAIVE MAJORITY-CLASS BASELINE")
    print("-" * 80)

    majority_percentage = (
        target_percentages.max()
    )

    print(
        "A model predicting only the majority "
        "class would achieve:"
    )

    print(
        f"Accuracy = {majority_percentage:.2f}%"
    )

    print()
    print(
        "This is why accuracy alone is not "
        "sufficient for credit-risk evaluation."
    )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()