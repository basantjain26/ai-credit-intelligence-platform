from __future__ import annotations

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.credit_risk.features import (
    build_numeric_preprocessor,
)


RANDOM_SEED = 42


def build_baseline_model() -> Pipeline:

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_numeric_preprocessor(),
            ),
            (
                "classifier",
                DummyClassifier(
                    strategy="prior",
                    random_state=RANDOM_SEED,
                ),
            ),
        ]
    )


def build_logistic_regression_model() -> Pipeline:

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
                    random_state=RANDOM_SEED,
                ),
            ),
        ]
    )