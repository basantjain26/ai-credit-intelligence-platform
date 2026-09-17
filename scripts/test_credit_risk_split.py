from pathlib import Path

import pandas as pd

from src.credit_risk.data_split import (
    create_train_validation_test_split,
)

from src.credit_risk.features import (
    split_features_and_target,
)


DATA_PATH = Path(
    "data/ml/raw/historical_credit_applications.csv"
)


def print_split_statistics(
    name: str,
    X: pd.DataFrame,
    y: pd.Series,
) -> None:

    default_count = int(
        y.sum()
    )

    default_rate = (
        y.mean()
    )

    print(
        f"{name:<12}"
        f"Rows={len(X):>5,}   "
        f"Defaults={default_count:>4,}   "
        f"Default Rate={default_rate:.2%}"
    )


def main() -> None:

    dataframe = pd.read_csv(
        DATA_PATH
    )

    X, y = split_features_and_target(
        dataframe
    )

    split = (
        create_train_validation_test_split(
            X,
            y,
        )
    )

    print()
    print("=" * 80)
    print(
        "TRAIN / VALIDATION / TEST SPLIT"
    )
    print("=" * 80)

    print_split_statistics(
        "FULL",
        X,
        y,
    )

    print_split_statistics(
        "TRAIN",
        split.X_train,
        split.y_train,
    )

    print_split_statistics(
        "VALIDATION",
        split.X_validation,
        split.y_validation,
    )

    print_split_statistics(
        "TEST",
        split.X_test,
        split.y_test,
    )

    print()
    print("=" * 80)

    #
    # Safety checks
    #
    assert len(split.X_train) == 7000
    assert len(split.X_validation) == 1500
    assert len(split.X_test) == 1500

    assert set(
        split.X_train.index
    ).isdisjoint(
        split.X_validation.index
    )

    assert set(
        split.X_train.index
    ).isdisjoint(
        split.X_test.index
    )

    assert set(
        split.X_validation.index
    ).isdisjoint(
        split.X_test.index
    )

    print(
        "No row overlap between splits."
    )

    print(
        "Split validation successful."
    )


if __name__ == "__main__":
    main()