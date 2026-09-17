from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class ClassificationMetrics:
    threshold: float

    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int

    accuracy: float
    precision: float
    recall: float
    f1: float

    roc_auc: float
    pr_auc: float


def evaluate_classifier(
    y_true,
    default_probabilities,
    threshold: float = 0.50,
) -> ClassificationMetrics:

    probabilities = np.asarray(
        default_probabilities
    )

    predictions = (
        probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = (
        confusion_matrix(
            y_true,
            predictions,
            labels=[0, 1],
        ).ravel()
    )

    return ClassificationMetrics(
        threshold=threshold,

        true_negatives=int(tn),
        false_positives=int(fp),
        false_negatives=int(fn),
        true_positives=int(tp),

        accuracy=accuracy_score(
            y_true,
            predictions,
        ),

        precision=precision_score(
            y_true,
            predictions,
            zero_division=0,
        ),

        recall=recall_score(
            y_true,
            predictions,
            zero_division=0,
        ),

        f1=f1_score(
            y_true,
            predictions,
            zero_division=0,
        ),

        roc_auc=roc_auc_score(
            y_true,
            probabilities,
        ),

        pr_auc=average_precision_score(
            y_true,
            probabilities,
        ),
    )