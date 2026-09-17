from __future__ import annotations

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


TARGET_COLUMN = "default_within_12m"

IDENTIFIER_COLUMNS = [
    "application_id",
]


NUMERIC_FEATURES = [
    "company_age_years",
    "banking_relationship_years",
    "revenue",
    "ebitda_margin",
    "debt_to_ebitda",
    "dscr",
    "current_ratio",
    "credit_score",
    "existing_exposure",
    "past_due_count_12m",
    "bureau_inquiries_6m",
    "transaction_anomaly_rate",
    "related_party_transaction_ratio",
    "requested_amount",
]


def split_features_and_target(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:

    missing_columns = [
        column
        for column in NUMERIC_FEATURES + [TARGET_COLUMN]
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required columns are missing: "
            + ", ".join(missing_columns)
        )

    features = dataframe[
        NUMERIC_FEATURES
    ].copy()

    target = dataframe[
        TARGET_COLUMN
    ].copy()

    return features, target


def build_numeric_preprocessor() -> ColumnTransformer:

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES,
            ),
        ],
        remainder="drop",
    )

    return preprocessor