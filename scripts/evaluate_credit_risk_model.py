from pathlib import Path

import pandas as pd

from src.credit_risk.data_split import (
    create_train_validation_test_split,
)

from src.credit_risk.evaluation import (
    evaluate_classifier,
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

    metrics = evaluate_classifier(
        y_true=split.y_validation,
        default_probabilities=probabilities,
        threshold=0.50,
    )

    print()
    print("=" * 70)
    print("CREDIT RISK MODEL EVALUATION")
    print("=" * 70)

    print()
    print(
        f"Threshold : "
        f"{metrics.threshold:.2f}"
    )

    print()
    print("CONFUSION MATRIX")
    print("-" * 70)

    print(
        f"TN: {metrics.true_negatives}"
    )

    print(
        f"FP: {metrics.false_positives}"
    )

    print(
        f"FN: {metrics.false_negatives}"
    )

    print(
        f"TP: {metrics.true_positives}"
    )

    print()
    print("CLASSIFICATION METRICS")
    print("-" * 70)

    print(
        f"Accuracy  : "
        f"{metrics.accuracy:.4f}"
    )

    print(
        f"Precision : "
        f"{metrics.precision:.4f}"
    )

    print(
        f"Recall    : "
        f"{metrics.recall:.4f}"
    )

    print(
        f"F1        : "
        f"{metrics.f1:.4f}"
    )

    print()
    print("RANKING METRICS")
    print("-" * 70)

    print(
        f"ROC-AUC   : "
        f"{metrics.roc_auc:.4f}"
    )

    print(
        f"PR-AP     : "
        f"{metrics.pr_auc:.4f}"
    )

    print()
    print(
        "Default prevalence: "
        f"{split.y_validation.mean():.4f}"
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()