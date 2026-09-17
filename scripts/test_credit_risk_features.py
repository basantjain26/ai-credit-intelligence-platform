from pathlib import Path

import pandas as pd

from src.credit_risk.features import (
    NUMERIC_FEATURES,
    build_numeric_preprocessor,
    split_features_and_target,
)


DATA_PATH = Path(
    "data/ml/raw/historical_credit_applications.csv"
)


def main() -> None:

    dataframe = pd.read_csv(
        DATA_PATH
    )

    X, y = split_features_and_target(
        dataframe
    )

    print("=" * 70)
    print("CREDIT RISK FEATURE PREPARATION")
    print("=" * 70)

    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")

    print()
    print("Features:")
    for feature in NUMERIC_FEATURES:
        print(f"- {feature}")

    print()
    print(
        "application_id in X:",
        "application_id" in X.columns,
    )

    print(
        "target in X:",
        "default_within_12m" in X.columns,
    )

    #
    # Demonstrate missing-value handling
    # without modifying source data.
    #
    sample = X.head(100).copy()

    sample.loc[
        sample.index[:5],
        "dscr",
    ] = None

    print()
    print(
        "Missing DSCR before preprocessing:",
        sample["dscr"].isna().sum(),
    )

    preprocessor = (
        build_numeric_preprocessor()
    )

    transformed = (
        preprocessor.fit_transform(
            sample
        )
    )

    print(
        "Missing values after preprocessing:",
        pd.isna(transformed).sum(),
    )

    print()
    print(
        "Transformed shape:",
        transformed.shape,
    )

    print()
    print(
        "Approximate transformed means "
        "(first five features):"
    )

    print(
        transformed.mean(axis=0)[:5]
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()