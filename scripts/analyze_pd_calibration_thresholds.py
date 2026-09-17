from pathlib import Path

import pandas as pd

from sklearn.calibration import (
    calibration_curve,
)

from sklearn.metrics import (
    brier_score_loss,
    precision_score,
    recall_score,
    f1_score,
)

from src.credit_risk.data_split import (
    create_train_validation_test_split,
)

from src.credit_risk.features import (
    split_features_and_target,
)

from src.credit_risk.models import (
    build_logistic_regression_model,
)


DATA_PATH = Path(
    "data/ml/raw/historical_credit_applications.csv"
)


THRESHOLDS = [
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.40,
    0.50,
]


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

    model = (
        build_logistic_regression_model()
    )

    model.fit(
        split.X_train,
        split.y_train,
    )

    probabilities = (
        model.predict_proba(
            split.X_validation
        )[:, 1]
    )

    #
    # CALIBRATION
    #

    brier = brier_score_loss(
        split.y_validation,
        probabilities,
    )

    print()
    print("=" * 80)
    print("PD CALIBRATION")
    print("=" * 80)

    print()
    print(
        "Validation default rate : "
        f"{split.y_validation.mean():.4f}"
    )

    print(
        "Average predicted PD    : "
        f"{probabilities.mean():.4f}"
    )

    print(
        "Brier score             : "
        f"{brier:.4f}"
    )

    actual_rate, predicted_rate = (
        calibration_curve(
            split.y_validation,
            probabilities,
            n_bins=10,
            strategy="quantile",
        )
    )

    print()
    print("CALIBRATION BINS")
    print("-" * 80)

    print(
        f"{'Predicted PD':>15}"
        f"{'Actual Default Rate':>25}"
    )

    for predicted, actual in zip(
        predicted_rate,
        actual_rate,
    ):
        print(
            f"{predicted:>15.4f}"
            f"{actual:>25.4f}"
        )

    #
    # THRESHOLD ANALYSIS
    #

    print()
    print("=" * 80)
    print("THRESHOLD ANALYSIS")
    print("=" * 80)

    print()
    print(
        f"{'Threshold':>12}"
        f"{'Precision':>12}"
        f"{'Recall':>12}"
        f"{'F1':>12}"
        f"{'Flagged':>12}"
    )

    print("-" * 80)

    for threshold in THRESHOLDS:

        predictions = (
            probabilities >= threshold
        ).astype(int)

        precision = precision_score(
            split.y_validation,
            predictions,
            zero_division=0,
        )

        recall = recall_score(
            split.y_validation,
            predictions,
            zero_division=0,
        )

        f1 = f1_score(
            split.y_validation,
            predictions,
            zero_division=0,
        )

        flagged = predictions.sum()

        print(
            f"{threshold:>12.2f}"
            f"{precision:>12.4f}"
            f"{recall:>12.4f}"
            f"{f1:>12.4f}"
            f"{flagged:>12}"
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()