"""Fixed-label classification and ONI regression evaluation helpers."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_fscore_support,
    r2_score,
)

from src.ml.temporal import PHASE_CLASSES, PHASE_NAMES


def classification_evaluation(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> tuple[dict[str, object], list[dict[str, object]], np.ndarray]:
    actual = np.asarray(actual, dtype=np.int64)
    predicted = np.asarray(predicted, dtype=np.int64)
    precision, recall, f1, support = precision_recall_fscore_support(
        actual,
        predicted,
        labels=PHASE_CLASSES,
        zero_division=0,
    )
    confusion = confusion_matrix(actual, predicted, labels=PHASE_CLASSES)
    report = classification_report(
        actual,
        predicted,
        labels=PHASE_CLASSES,
        target_names=[PHASE_NAMES[int(label)] for label in PHASE_CLASSES],
        output_dict=True,
        zero_division=0,
    )
    predicted_counts = np.bincount(predicted, minlength=len(PHASE_CLASSES))
    summary: dict[str, object] = {
        "accuracy": float(accuracy_score(actual, predicted)),
        "balanced_accuracy": float(np.mean(recall[support > 0])),
        "macro_precision": float(np.mean(precision)),
        "macro_recall": float(np.mean(recall)),
        "macro_f1": float(f1_score(actual, predicted, labels=PHASE_CLASSES,
                                   average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(actual, predicted, labels=PHASE_CLASSES,
                                      average="weighted", zero_division=0)),
        "actual_class_counts": {
            str(int(label)): int(support[index])
            for index, label in enumerate(PHASE_CLASSES)
        },
        "predicted_class_counts": {
            str(int(label)): int(predicted_counts[index])
            for index, label in enumerate(PHASE_CLASSES)
        },
        "missing_actual_classes": [
            PHASE_NAMES[int(label)]
            for index, label in enumerate(PHASE_CLASSES)
            if support[index] == 0
        ],
        "missing_predicted_classes": [
            PHASE_NAMES[int(label)]
            for index, label in enumerate(PHASE_CLASSES)
            if predicted_counts[index] == 0
        ],
    }
    report_rows = []
    for class_id, class_name in PHASE_NAMES.items():
        report_rows.append(
            {
                "class_id": class_id,
                "class_name": class_name,
                "precision": float(precision[class_id]),
                "recall": float(recall[class_id]),
                "f1_score": float(f1[class_id]),
                "support": int(support[class_id]),
                "predicted_count": int(predicted_counts[class_id]),
            }
        )
    report_rows.append(
        {
            "class_id": "macro_avg",
            "class_name": "macro_avg",
            "precision": float(np.mean(precision)),
            "recall": float(np.mean(recall)),
            "f1_score": summary["macro_f1"],
            "support": int(len(actual)),
            "predicted_count": int(len(predicted)),
        }
    )
    report_rows.append(
        {
            "class_id": "weighted_avg",
            "class_name": "weighted_avg",
            "precision": float(report["weighted avg"]["precision"]),
            "recall": float(report["weighted avg"]["recall"]),
            "f1_score": float(report["weighted avg"]["f1-score"]),
            "support": int(len(actual)),
            "predicted_count": int(len(predicted)),
        }
    )
    return summary, report_rows, confusion


def regression_evaluation(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float | None]:
    actual = np.asarray(actual, dtype=np.float64)
    predicted = np.asarray(predicted, dtype=np.float64)
    if len(actual) != len(predicted) or len(actual) == 0:
        raise ValueError("ONI regression metrics require equally-sized non-empty arrays")
    variance = float(np.var(actual))
    r2 = (
        float(r2_score(actual, predicted))
        if len(actual) >= 2 and variance > 0
        else None
    )
    mse = float(mean_squared_error(actual, predicted))
    return {
        "oni_mse": mse,
        "oni_rmse": float(np.sqrt(mse)),
        "oni_mae": float(mean_absolute_error(actual, predicted)),
        "oni_r2": r2,
    }
