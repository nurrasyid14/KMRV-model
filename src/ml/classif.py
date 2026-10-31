"""ENSO and marine heatwave classification utilities."""

from __future__ import annotations

import numpy as np
from sklearn.base import ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression

ENSO_CLASSES = ("La Nina", "Neutral", "El Nino")


def enso_phase(values: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Convert continuous ONI values into the three standard phases."""
    values = np.asarray(values, dtype=float)
    return np.where(
        values >= threshold,
        "El Nino",
        np.where(values <= -threshold, "La Nina", "Neutral"),
    )


def fit_calibrated_classifier(
    features: np.ndarray,
    labels: np.ndarray,
    seed: int = 42,
) -> CalibratedClassifierCV | ClassifierMixin:
    """Fit class-balanced logistic regression with probability calibration."""
    base = LogisticRegression(
        class_weight="balanced",
        max_iter=2000,
        random_state=seed,
    )
    calibrated = CalibratedClassifierCV(base, method="sigmoid", cv=3)
    calibrated.fit(features, labels)
    return calibrated
