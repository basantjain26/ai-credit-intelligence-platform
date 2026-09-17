from pathlib import Path

import pandas as pd

from src.credit_risk.data_split import (
    create_train_validation_test_split,
)

from src.credit_risk.explainability import (
    explain_logistic_prediction,
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

    #
    # Pick one validation borrower.
    #
    borrower = (
        split.X_validation.iloc[
            [0]
        ]
    )

    actual_outcome = int(
        split.y_validation.iloc[0]
    )

    #
    # Background represents the population
    # against which SHAP compares the borrower.
    #
    background = (
        split.X_train.sample(
            n=min(
                500,
                len(split.X_train),
            ),
            random_state=42,
        )
    )

    explanation = (
        explain_logistic_prediction(
            model_pipeline=model,
            background_data=background,
            borrower_data=borrower,
            top_n=10,
        )
    )

    print()
    print("=" * 80)
    print(
        "CREDIT RISK MODEL EXPLANATION"
    )
    print("=" * 80)

    print()
    print(
        f"Actual outcome : "
        f"{actual_outcome}"
    )

    print(
        f"Predicted PD   : "
        f"{explanation.predicted_pd:.4f}"
    )

    print()
    print(
        "TOP FEATURE CONTRIBUTIONS"
    )
    print("-" * 80)

    print(
        f"{'Feature':<35}"
        f"{'Value':>12}"
        f"{'SHAP':>12}"
        f"{'Direction':>20}"
    )

    print("-" * 80)

    for contribution in (
        explanation.contributions
    ):

        print(
            f"{contribution.feature_name:<35}"
            f"{contribution.feature_value:>12.4f}"
            f"{contribution.shap_value:>12.4f}"
            f"{contribution.direction:>20}"
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()