from pathlib import Path

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
)

from src.credit_risk.data_split import (
    create_train_validation_test_split,
)

from src.credit_risk.features import (
    split_features_and_target,
)

from src.credit_risk.models import (
    build_baseline_model,
    build_logistic_regression_model,
)


DATA_PATH = Path(
    "data/ml/raw/historical_credit_applications.csv"
)


def evaluate_model(
    name: str,
    model,
    X,
    y,
) -> None:

    predictions = model.predict(X)

    default_probabilities = (
        model.predict_proba(X)[:, 1]
    )

    accuracy = accuracy_score(
        y,
        predictions,
    )

    roc_auc = roc_auc_score(
        y,
        default_probabilities,
    )

    print()
    print(name)
    print("-" * 60)

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"ROC-AUC  : {roc_auc:.4f}"
    )

    print(
        "Average predicted PD: "
        f"{default_probabilities.mean():.4f}"
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

    baseline_model = (
        build_baseline_model()
    )

    logistic_model = (
        build_logistic_regression_model()
    )

    #
    # FIT ONLY ON TRAINING DATA.
    #
    baseline_model.fit(
        split.X_train,
        split.y_train,
    )

    logistic_model.fit(
        split.X_train,
        split.y_train,
    )

    print()
    print("=" * 70)
    print("CREDIT RISK MODEL TRAINING")
    print("=" * 70)

    print()
    print(
        f"Training rows: "
        f"{len(split.X_train):,}"
    )

    print(
        f"Validation rows: "
        f"{len(split.X_validation):,}"
    )

    #
    # Evaluate on validation data.
    #
    evaluate_model(
        "DUMMY BASELINE",
        baseline_model,
        split.X_validation,
        split.y_validation,
    )

    evaluate_model(
        "LOGISTIC REGRESSION",
        logistic_model,
        split.X_validation,
        split.y_validation,
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()