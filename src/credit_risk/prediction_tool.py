from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.credit_risk.features import NUMERIC_FEATURES
from src.credit_risk.model_artifact import load_model_artifact


DEFAULT_MODEL_VERSION = "v1"

DEFAULT_MODEL_PATH = Path(
    "data/ml/models/credit_risk_logistic_v1.joblib"
)


@dataclass
class CreditRiskPrediction:
    """
    Structured output returned by the credit-risk prediction tool.

    The ML layer returns the probability of default and model
    provenance. It does not approve/reject the loan or assign
    a business risk tier.
    """

    customer_id: str
    application_id: str

    probability_of_default: float

    model_name: str
    model_version: str

    missing_features: list[str]


class CreditRiskPredictionTool:
    """
    Production-style inference wrapper around the persisted
    commercial credit Probability of Default model.

    Responsibilities:
    - Validate the inference feature contract.
    - Load the persisted model lazily.
    - Preserve training/inference preprocessing consistency.
    - Generate Probability of Default.
    - Report features that were missing and therefore imputed.
    - Return model provenance.

    The tool does NOT:
    - calculate business approval/rejection decisions,
    - assign policy outcomes,
    - fabricate missing features,
    - retrain the model.
    """

    def __init__(
        self,
        model_path: Path = DEFAULT_MODEL_PATH,
        model_version: str = DEFAULT_MODEL_VERSION,
    ) -> None:

        self.model_path = model_path
        self.model_version = model_version

        # Lazy loading:
        # the artifact is loaded only on the first prediction.
        self._model = None

    def _load_model(self):
        """
        Load the persisted model artifact once and reuse it
        for subsequent predictions.
        """

        if self._model is None:
            self._model = load_model_artifact(
                self.model_path
            )

        return self._model

    def _validate_identifiers(
        self,
        customer_id: str,
        application_id: str,
    ) -> None:
        """
        Validate required case identifiers.
        """

        if not customer_id:
            raise ValueError(
                "customer_id is required."
            )

        if not application_id:
            raise ValueError(
                "application_id is required."
            )

    def _validate_features(
        self,
        features: dict,
    ) -> None:
        """
        Validate the inference feature contract.

        Every feature used during model training must be
        present in the request.

        A feature may contain None when the value is genuinely
        unavailable. The persisted preprocessing pipeline will
        handle that missing value using the fitted imputer.

        Missing feature key:
            contract/schema error

        Feature key with None:
            known missing value handled by preprocessing
        """

        if not isinstance(features, dict):
            raise ValueError(
                "features must be provided as a dictionary."
            )

        missing_feature_keys = [
            feature
            for feature in NUMERIC_FEATURES
            if feature not in features
        ]

        if missing_feature_keys:
            raise ValueError(
                "Missing required credit-risk feature keys: "
                f"{missing_feature_keys}"
            )

        invalid_features = []

        for feature in NUMERIC_FEATURES:

            value = features[feature]

            # None is allowed because the fitted preprocessing
            # pipeline contains the median imputer.
            if value is None:
                continue

            if not isinstance(
                value,
                (int, float),
            ):
                invalid_features.append(
                    feature
                )

        if invalid_features:
            raise ValueError(
                "Credit-risk features must be numeric "
                "or None. Invalid features: "
                f"{invalid_features}"
            )

    def _get_missing_features(
        self,
        features: dict,
    ) -> list[str]:
        """
        Return features whose values are unavailable.

        These features will be handled by the fitted
        preprocessing pipeline's imputation logic.
        """

        return [
            feature
            for feature in NUMERIC_FEATURES
            if features[feature] is None
        ]

    def _build_inference_dataframe(
        self,
        features: dict,
    ) -> pd.DataFrame:
        """
        Convert the validated feature dictionary into the exact
        feature structure expected by the sklearn pipeline.
        """

        borrower_record = {
            feature: features[feature]
            for feature in NUMERIC_FEATURES
        }

        return pd.DataFrame(
            [borrower_record]
        )

    def predict(
        self,
        customer_id: str,
        application_id: str,
        features: dict,
    ) -> CreditRiskPrediction:
        """
        Generate Probability of Default for one borrower.

        The persisted sklearn Pipeline performs both:
            preprocessing
            +
            Logistic Regression inference

        This preserves training/inference consistency.
        """

        self._validate_identifiers(
            customer_id=customer_id,
            application_id=application_id,
        )

        self._validate_features(
            features
        )

        missing_features = (
            self._get_missing_features(
                features
            )
        )

        borrower_dataframe = (
            self._build_inference_dataframe(
                features
            )
        )

        model = self._load_model()

        probabilities = model.predict_proba(
            borrower_dataframe
        )

        probability_of_default = float(
            probabilities[0, 1]
        )

        # Defensive validation:
        # a probability must always remain between 0 and 1.
        if not (
            0.0
            <= probability_of_default
            <= 1.0
        ):
            raise ValueError(
                "Model returned an invalid probability "
                f"of default: {probability_of_default}"
            )

        return CreditRiskPrediction(
            customer_id=customer_id,
            application_id=application_id,
            probability_of_default=(
                probability_of_default
            ),
            model_name=(
                "commercial_credit_pd"
            ),
            model_version=(
                self.model_version
            ),
            missing_features=(
                missing_features
            ),
        )