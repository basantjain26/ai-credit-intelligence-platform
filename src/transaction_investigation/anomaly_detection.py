from dataclasses import dataclass
from typing import Any

from sklearn.ensemble import (
    IsolationForest,
)

from src.transaction_investigation.feature_engineering import (
    ML_FEATURES,
)


MODEL_NAME = "IsolationForest"

MODEL_VERSION = (
    "transaction_iforest_v2"
)


@dataclass(frozen=True)
class TransactionAnomalyResult:
    """
    One Isolation Forest prediction with sufficient lineage
    for downstream agent investigation.
    """

    transaction_id: str

    is_anomaly: bool

    anomaly_score: float

    raw_model_score: float

    model_prediction: int

    model_name: str

    model_version: str

    feature_version: str

    features: dict[str, float]


class TransactionAnomalyDetector:
    """
    Isolation Forest transaction anomaly detector.

    Training and inference are intentionally separate:

        fit(training_features)

        score(inference_features)

    The model detects unusual behavior.

    It does NOT classify:
    - fraud
    - AML violations
    - borrower default
    - credit approval/rejection
    """

    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 200,
        random_state: int = 42,
    ) -> None:

        if not (
            0 < contamination <= 0.5
        ):
            raise ValueError(
                "contamination must be "
                "> 0 and <= 0.5"
            )

        if n_estimators <= 0:
            raise ValueError(
                "n_estimators must be "
                "greater than 0"
            )

        self.contamination = (
            contamination
        )

        self.n_estimators = (
            n_estimators
        )

        self.random_state = (
            random_state
        )

        self.model = (
            IsolationForest(
                n_estimators=(
                    n_estimators
                ),

                contamination=(
                    contamination
                ),

                random_state=(
                    random_state
                ),
            )
        )

        self._is_fitted = False

        self.training_transaction_count = 0

    # =========================================================
    # TRAIN
    # =========================================================

    def fit(
        self,
        training_feature_rows: list[
            dict[str, Any]
        ],
    ) -> "TransactionAnomalyDetector":
        """
        Train Isolation Forest on historical baseline
        transactions.

        No y exists because this is unsupervised learning.
        """

        self._validate_feature_rows(
            training_feature_rows
        )

        if (
            len(training_feature_rows)
            < 20
        ):
            raise ValueError(
                "At least 20 historical "
                "transactions are required."
            )

        X_train = (
            self._build_matrix(
                training_feature_rows
            )
        )

        self.model.fit(
            X_train
        )

        self.training_transaction_count = (
            len(
                training_feature_rows
            )
        )

        self._is_fitted = True

        return self

    # =========================================================
    # INFERENCE
    # =========================================================

    def score(
        self,
        feature_rows: list[
            dict[str, Any]
        ],
    ) -> list[
        TransactionAnomalyResult
    ]:
        """
        Score new transactions using the already fitted model.

        sklearn:

            decision_function > 0
                more normal

            decision_function < 0
                more anomalous

        Application convention:

            anomaly_score =
                -decision_function

        Therefore:

            HIGHER anomaly_score
                =
            MORE anomalous
        """

        self._require_fitted()

        self._validate_feature_rows(
            feature_rows
        )

        X = self._build_matrix(
            feature_rows
        )

        raw_scores = (
            self.model
            .decision_function(
                X
            )
        )

        predictions = (
            self.model.predict(
                X
            )
        )

        results: list[
            TransactionAnomalyResult
        ] = []

        for (
            row,
            raw_score,
            prediction,
        ) in zip(
            feature_rows,
            raw_scores,
            predictions,
            strict=True,
        ):

            raw_score_value = float(
                raw_score
            )

            prediction_value = int(
                prediction
            )

            result = (
                TransactionAnomalyResult(
                    transaction_id=str(
                        row[
                            "transaction_id"
                        ]
                    ),

                    is_anomaly=(
                        prediction_value
                        == -1
                    ),

                    anomaly_score=(
                        -raw_score_value
                    ),

                    raw_model_score=(
                        raw_score_value
                    ),

                    model_prediction=(
                        prediction_value
                    ),

                    model_name=(
                        MODEL_NAME
                    ),

                    model_version=(
                        MODEL_VERSION
                    ),

                    feature_version=str(
                        row[
                            "feature_version"
                        ]
                    ),

                    features={
                        feature_name: float(
                            row[
                                feature_name
                            ]
                        )
                        for feature_name
                        in ML_FEATURES
                    },
                )
            )

            results.append(
                result
            )

        return results

    # =========================================================
    # RANKING
    # =========================================================

    @staticmethod
    def get_anomalies(
        results: list[
            TransactionAnomalyResult
        ],
    ) -> list[
        TransactionAnomalyResult
    ]:

        return sorted(
            [
                result
                for result in results
                if result.is_anomaly
            ],
            key=lambda result: (
                result.anomaly_score
            ),
            reverse=True,
        )

    @staticmethod
    def rank_by_anomaly(
        results: list[
            TransactionAnomalyResult
        ],
    ) -> list[
        TransactionAnomalyResult
    ]:

        return sorted(
            results,
            key=lambda result: (
                result.anomaly_score
            ),
            reverse=True,
        )

    # =========================================================
    # MATRIX
    # =========================================================

    @staticmethod
    def _build_matrix(
        feature_rows: list[
            dict[str, Any]
        ],
    ) -> list[list[float]]:

        return [
            [
                float(
                    row[
                        feature_name
                    ]
                )
                for feature_name
                in ML_FEATURES
            ]
            for row in feature_rows
        ]

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_feature_rows(
        feature_rows: list[
            dict[str, Any]
        ],
    ) -> None:

        if not feature_rows:
            raise ValueError(
                "Feature rows cannot be empty."
            )

        expected_feature_version: (
            str | None
        ) = None

        for row in feature_rows:

            transaction_id = (
                row.get(
                    "transaction_id"
                )
            )

            if not transaction_id:
                raise ValueError(
                    "transaction_id is required"
                )

            feature_version = (
                row.get(
                    "feature_version"
                )
            )

            if not feature_version:
                raise ValueError(
                    "feature_version missing for "
                    f"{transaction_id}"
                )

            if (
                expected_feature_version
                is None
            ):
                expected_feature_version = (
                    str(
                        feature_version
                    )
                )

            elif (
                str(feature_version)
                != expected_feature_version
            ):
                raise ValueError(
                    "Mixed feature versions "
                    "detected in the same batch."
                )

            for feature_name in (
                ML_FEATURES
            ):

                if (
                    feature_name
                    not in row
                ):
                    raise ValueError(
                        f"Missing feature "
                        f"'{feature_name}' "
                        f"for {transaction_id}"
                    )

                if (
                    row[
                        feature_name
                    ]
                    is None
                ):
                    raise ValueError(
                        f"Feature "
                        f"'{feature_name}' "
                        f"is None for "
                        f"{transaction_id}"
                    )

    def _require_fitted(
        self,
    ) -> None:

        if not self._is_fitted:
            raise RuntimeError(
                "Isolation Forest has not "
                "been fitted. Call fit() first."
            )