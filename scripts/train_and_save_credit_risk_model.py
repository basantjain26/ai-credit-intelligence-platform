from pathlib import Path

import pandas as pd

from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
)

from src.credit_risk.data_split import (
    create_train_validation_test_split,
)

from src.credit_risk.features import (
    TARGET_COLUMN,
    split_features_and_target,
)

from src.credit_risk.model_artifact import (
    ModelMetadata,
    current_utc_timestamp,
    save_model_artifact,
)

from src.credit_risk.models import (
    build_logistic_regression_model,
)


DATA_PATH = Path(
    "data/ml/raw/historical_credit_applications.csv"
)

MODEL_VERSION = "v1"

MODEL_DIR = Path(
    "data/ml/models"
)

MODEL_PATH = (
    MODEL_DIR
    / f"credit_risk_logistic_{MODEL_VERSION}.joblib"
)

METADATA_PATH = (
    MODEL_DIR
    / f"credit_risk_logistic_{MODEL_VERSION}.json"
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

    #
    # Train only on training data.
    #
    model.fit(
        split.X_train,
        split.y_train,
    )

    validation_probabilities = (
        model.predict_proba(
            split.X_validation
        )[:, 1]
    )

    validation_roc_auc = (
        roc_auc_score(
            split.y_validation,
            validation_probabilities,
        )
    )

    validation_pr_ap = (
        average_precision_score(
            split.y_validation,
            validation_probabilities,
        )
    )

    metadata = ModelMetadata(
        model_name=(
            "commercial_credit_pd"
        ),
        model_version=MODEL_VERSION,
        model_type=(
            "LogisticRegression"
        ),
        target=TARGET_COLUMN,
        training_rows=len(
            split.X_train
        ),
        validation_rows=len(
            split.X_validation
        ),
        validation_roc_auc=float(
            validation_roc_auc
        ),
        validation_pr_ap=float(
            validation_pr_ap
        ),
        created_at_utc=(
            current_utc_timestamp()
        ),
    )

    save_model_artifact(
        model=model,
        metadata=metadata,
        model_path=MODEL_PATH,
        metadata_path=METADATA_PATH,
    )

    print()
    print("=" * 70)
    print(
        "CREDIT RISK MODEL ARTIFACT"
    )
    print("=" * 70)

    print()
    print(
        f"Version       : "
        f"{MODEL_VERSION}"
    )

    print(
        f"Model path    : "
        f"{MODEL_PATH}"
    )

    print(
        f"Metadata path : "
        f"{METADATA_PATH}"
    )

    print(
        f"Validation AUC: "
        f"{validation_roc_auc:.4f}"
    )

    print(
        f"Validation AP : "
        f"{validation_pr_ap:.4f}"
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()