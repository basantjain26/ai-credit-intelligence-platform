from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from sklearn.model_selection import (
    train_test_split,
)


RANDOM_SEED = 42

TRAIN_SIZE = 0.70
VALIDATION_SIZE = 0.15
TEST_SIZE = 0.15


@dataclass
class CreditRiskDataSplit:
    X_train: pd.DataFrame
    X_validation: pd.DataFrame
    X_test: pd.DataFrame

    y_train: pd.Series
    y_validation: pd.Series
    y_test: pd.Series


def create_train_validation_test_split(
    X: pd.DataFrame,
    y: pd.Series,
) -> CreditRiskDataSplit:

    #
    # First split:
    #
    # 70% training
    # 30% temporary
    #
    X_train, X_temp, y_train, y_temp = (
        train_test_split(
            X,
            y,
            test_size=(
                VALIDATION_SIZE
                + TEST_SIZE
            ),
            random_state=RANDOM_SEED,
            stratify=y,
        )
    )

    #
    # Second split:
    #
    # Split the remaining 30%
    # equally into validation/test.
    #
    validation_fraction_of_temp = (
        VALIDATION_SIZE
        / (
            VALIDATION_SIZE
            + TEST_SIZE
        )
    )

    (
        X_validation,
        X_test,
        y_validation,
        y_test,
    ) = train_test_split(
        X_temp,
        y_temp,
        train_size=(
            validation_fraction_of_temp
        ),
        random_state=RANDOM_SEED,
        stratify=y_temp,
    )

    return CreditRiskDataSplit(
        X_train=X_train,
        X_validation=X_validation,
        X_test=X_test,
        y_train=y_train,
        y_validation=y_validation,
        y_test=y_test,
    )