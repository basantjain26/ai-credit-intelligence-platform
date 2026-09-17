from pathlib import Path

import pandas as pd

from sklearn.linear_model import (
    LogisticRegression,
)

from sklearn.metrics import (
    roc_auc_score,
)

from sklearn.pipeline import Pipeline

from src.credit_risk.data_split import (
    create_train_validation_test_split,
)

from src.credit_risk.features import (
    build_numeric_preprocessor,
    split_features_and_target,
)


DATA_PATH = Path(
    "data/ml/raw/historical_credit_applications.csv"
)


C_VALUES = [
    0.001,
    0.01,
    0.1,
    1.0,
    10.0,
    100.0,
]


def build_model(
    c_value: float,
) -> Pipeline:

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_numeric_preprocessor(),
            ),
            (
                "classifier",
                LogisticRegression(
                    C=c_value,
                    penalty="l2",
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
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
    print("=" * 78)
    print(
        "LOGISTIC REGRESSION "
        "REGULARIZATION EXPERIMENT"
    )
    print("=" * 78)

    print()
    print(
        f"{'C':>10}"
        f"{'Train AUC':>15}"
        f"{'Validation AUC':>20}"
        f"{'Gap':>12}"
    )

    print("-" * 78)

    for c_value in C_VALUES:

        model = build_model(
            c_value
        )

        model.fit(
            split.X_train,
            split.y_train,
        )

        train_probability = (
            model.predict_proba(
                split.X_train
            )[:, 1]
        )

        validation_probability = (
            model.predict_proba(
                split.X_validation
            )[:, 1]
        )

        train_auc = roc_auc_score(
            split.y_train,
            train_probability,
        )

        validation_auc = roc_auc_score(
            split.y_validation,
            validation_probability,
        )

        gap = (
            train_auc
            - validation_auc
        )

        print(
            f"{c_value:>10.3f}"
            f"{train_auc:>15.4f}"
            f"{validation_auc:>20.4f}"
            f"{gap:>12.4f}"
        )

    print()
    print("=" * 78)


if __name__ == "__main__":
    main()