"""Tabular and autoregressive regression forecasters."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor

try:
    from lightgbm import LGBMRegressor
except ImportError:  # pragma: no cover - handled explicitly by the orchestrator
    LGBMRegressor = None


@dataclass
class ForecastModel:
    """Fitted forecaster and its human-readable implementation name."""

    name: str
    estimator: object


def fit_ridge(
    features: np.ndarray,
    targets: np.ndarray,
    alpha: float = 1.0,
) -> ForecastModel:
    """Fit ridge regression for one target or multiple horizons."""
    estimator = Ridge(alpha=alpha)
    if targets.ndim == 2 and targets.shape[1] > 1:
        estimator = MultiOutputRegressor(estimator)
    estimator.fit(features, targets)
    return ForecastModel("ridge", estimator)


def fit_lightgbm(
    features: np.ndarray,
    targets: np.ndarray,
    seed: int = 42,
) -> ForecastModel:
    """Fit LightGBM, or raise a clear dependency error when it is unavailable."""
    if LGBMRegressor is None:
        raise RuntimeError("lightgbm must be installed to use the lightgbm forecaster")
    estimator = LGBMRegressor(
        objective="regression",
        n_estimators=300,
        learning_rate=0.05,
        random_state=seed,
        verbosity=-1,
    )
    if targets.ndim == 2 and targets.shape[1] > 1:
        estimator = MultiOutputRegressor(estimator)
    estimator.fit(features, targets)
    return ForecastModel("lightgbm", estimator)
