from pathlib import Path

import pandas as pd

from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
)

from sklearn.linear_model import (
    LogisticRegression,
)

from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)

from sklearn.pipeline import Pipeline

from sklearn.tree import (
    DecisionTreeClassifier,
)

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


def build_logistic_model():

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_numeric_preprocessor(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )


def build_decision_tree():

    return DecisionTreeClassifier(
        max_depth=None,
        random_state=42,
    )


def build_random_forest():

    return RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )


def build_gradient_boosting():

    return GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    )


def evaluate_model(
    name,
    model,
    split,
):

    model.fit(
        split.X_train,
        split.y_train,
    )

    train_probabilities = (
        model.predict_proba(
            split.X_train
        )[:, 1]
    )

    validation_probabilities = (
        model.predict_proba(
            split.X_validation
        )[:, 1]
    )

    train_auc = roc_auc_score(
        split.y_train,
        train_probabilities,
    )

    validation_auc = roc_auc_score(
        split.y_validation,
        validation_probabilities,
    )

    validation_pr = (
        average_precision_score(
            split.y_validation,
            validation_probabilities,
        )
    )

    return {
        "model": name,
        "train_auc": train_auc,
        "validation_auc": validation_auc,
        "validation_pr_ap": validation_pr,
        "auc_gap": (
            train_auc - validation_auc
        ),
    }


def main():

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

    models = [
        (
            "Logistic Regression",
            build_logistic_model(),
        ),
        (
            "Decision Tree",
            build_decision_tree(),
        ),
        (
            "Random Forest",
            build_random_forest(),
        ),
        (
            "Gradient Boosting",
            build_gradient_boosting(),
        ),
    ]

    results = []

    for name, model in models:

        print(
            f"Training {name}..."
        )

        result = evaluate_model(
            name,
            model,
            split,
        )

        results.append(result)

    results_df = pd.DataFrame(
        results
    )

    results_df = results_df.sort_values(
        "validation_auc",
        ascending=False,
    )

    print()
    print("=" * 90)
    print("CREDIT RISK MODEL COMPARISON")
    print("=" * 90)

    print(
        results_df.to_string(
            index=False,
            formatters={
                "train_auc":
                    "{:.4f}".format,
                "validation_auc":
                    "{:.4f}".format,
                "validation_pr_ap":
                    "{:.4f}".format,
                "auc_gap":
                    "{:.4f}".format,
            },
        )
    )

    print()
    print(
        "Validation default prevalence: "
        f"{split.y_validation.mean():.4f}"
    )

    print()
    print("=" * 90)


if __name__ == "__main__":
    main()