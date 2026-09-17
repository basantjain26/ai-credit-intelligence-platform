from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import joblib


@dataclass
class ModelMetadata:
    model_name: str
    model_version: str
    model_type: str
    target: str
    training_rows: int
    validation_rows: int
    validation_roc_auc: float
    validation_pr_ap: float
    created_at_utc: str


def save_model_artifact(
    model,
    metadata: ModelMetadata,
    model_path: Path,
    metadata_path: Path,
) -> None:

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        model_path,
    )

    metadata_path.write_text(
        json.dumps(
            asdict(metadata),
            indent=2,
        )
    )


def load_model_artifact(
    model_path: Path,
):

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: "
            f"{model_path}"
        )

    return joblib.load(
        model_path
    )


def current_utc_timestamp() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()