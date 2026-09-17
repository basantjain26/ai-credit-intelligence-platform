from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import shap

from src.credit_risk.features import NUMERIC_FEATURES


@dataclass
class FeatureContribution:
    feature_name: str
    feature_value: float
    shap_value: float
    direction: str


@dataclass
class CreditRiskExplanation:
    predicted_pd: float
    base_value: float
    contributions: list[FeatureContribution]


def explain_logistic_prediction(
    model_pipeline,
    background_data: pd.DataFrame,
    borrower_data: pd.DataFrame,
    top_n: int = 10,
) -> CreditRiskExplanation:

    preprocessor = (
        model_pipeline.named_steps[
            "preprocessor"
        ]
    )

    classifier = (
        model_pipeline.named_steps[
            "classifier"
        ]
    )

    transformed_background = (
        preprocessor.transform(
            background_data
        )
    )

    transformed_borrower = (
        preprocessor.transform(
            borrower_data
        )
    )

    explainer = shap.LinearExplainer(
        classifier,
        transformed_background,
    )

    shap_values = explainer(
        transformed_borrower
    )

    predicted_pd = (
        model_pipeline.predict_proba(
            borrower_data
        )[0, 1]
    )

    values = shap_values.values[0]

    contributions = []

    for feature_name, feature_value, shap_value in zip(
        NUMERIC_FEATURES,
        borrower_data.iloc[0][
            NUMERIC_FEATURES
        ],
        values,
    ):

        direction = (
            "INCREASES_RISK"
            if shap_value > 0
            else "DECREASES_RISK"
        )

        contributions.append(
            FeatureContribution(
                feature_name=feature_name,
                feature_value=float(
                    feature_value
                ),
                shap_value=float(
                    shap_value
                ),
                direction=direction,
            )
        )

    contributions.sort(
        key=lambda item: abs(
            item.shap_value
        ),
        reverse=True,
    )

    return CreditRiskExplanation(
        predicted_pd=float(
            predicted_pd
        ),
        base_value=float(
            np.asarray(
                shap_values.base_values
            ).reshape(-1)[0]
        ),
        contributions=(
            contributions[:top_n]
        ),
    )