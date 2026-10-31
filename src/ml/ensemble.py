"""Forecast orchestration for statistical, tabular, and deep-learning models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from . import classif, deepl, forecast, stats


@dataclass(frozen=True)
class ForecastRunConfig:
    """Experiment settings shared by all forecasters."""

    horizons: tuple[int, ...] = (1, 3, 6, 12)
    window_size: int = 12
    seed: int = 42
    enabled_models: tuple[str, ...] = ("persistence", "climatology", "ridge")


@dataclass
class ForecastRunResult:
    """Predictions and metadata returned by one orchestration run."""

    predictions: dict[str, np.ndarray] = field(default_factory=dict)
    probabilities: dict[str, np.ndarray] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ForecastOrchestrator:
    """Route a target series and features to the selected forecasting stages."""

    def __init__(self, config: ForecastRunConfig | None = None) -> None:
        self.config = config or ForecastRunConfig()
        unknown = set(self.config.enabled_models) - {
            "persistence",
            "climatology",
            "seasonal_naive",
            "ridge",
            "lightgbm",
            "lstm",
            "enso_classifier",
        }
        if unknown:
            raise ValueError(f"Unknown forecast models: {sorted(unknown)}")

    def run_baselines(
        self,
        training_values: pd.Series,
        forecast_dates: pd.DatetimeIndex,
    ) -> ForecastRunResult:
        """Run persistence and climatology baseline models."""
        training_values = stats.validate_series(training_values)
        horizon = len(forecast_dates)
        predictions: dict[str, np.ndarray] = {}

        if "persistence" in self.config.enabled_models:
            predictions["persistence"] = stats.persistence_forecast(
                training_values, horizon
            ).prediction
        if "climatology" in self.config.enabled_models:
            predictions["climatology"] = stats.seasonal_climatology(
                training_values, forecast_dates
            ).prediction
        if "seasonal_naive" in self.config.enabled_models:
            predictions["seasonal_naive"] = stats.seasonal_naive(
                training_values,
                horizon,
                forecast_dates=forecast_dates,
            ).prediction

        return ForecastRunResult(
            predictions=predictions,
            metadata={"forecast_dates": forecast_dates.copy()},
        )

    def run_tabular(
        self,
        features: np.ndarray,
        targets: np.ndarray,
    ) -> ForecastRunResult:
        """Fit ridge and optionally LightGBM from the requested configuration."""
        features = np.asarray(features)
        targets = np.asarray(targets)
        predictions: dict[str, np.ndarray] = {}
        models: dict[str, object] = {}

        if "ridge" in self.config.enabled_models:
            models["ridge"] = forecast.fit_ridge(features, targets).estimator
            predictions["ridge"] = models["ridge"].predict(features)
        if "lightgbm" in self.config.enabled_models:
            models["lightgbm"] = forecast.fit_lightgbm(
                features, targets, self.config.seed
            ).estimator
            predictions["lightgbm"] = models["lightgbm"].predict(features)

        return ForecastRunResult(predictions=predictions, metadata={"models": models})

    def run_enso_classifier(
        self,
        features: np.ndarray,
        oni_anomaly: np.ndarray,
    ) -> ForecastRunResult:
        """Create calibrated ENSO-phase probabilities and discrete labels."""
        labels = classif.enso_phase(oni_anomaly)
        model = classif.fit_calibrated_classifier(
            features,
            labels,
            seed=self.config.seed,
        )
        probabilities = model.predict_proba(features)
        return ForecastRunResult(
            predictions={"enso_phase": np.asarray(model.predict(features))},
            probabilities={"enso_phase": probabilities},
            metadata={"classes": list(getattr(model, "classes_", classif.ENSO_CLASSES))},
        )

    def run_sequence(
        self,
        features: np.ndarray,
        targets: np.ndarray,
    ) -> ForecastRunResult:
        """Validate sequence windows and construct the configured PyTorch model."""
        windows = deepl.make_sequence_windows(
            features,
            targets,
            self.config.window_size,
        )
        input_size = windows.features.shape[-1]
        output_size = (
            1 if windows.targets.ndim == 1 else int(windows.targets.shape[-1])
        )
        model = deepl.ClimateLSTM(
            input_size=input_size,
            output_size=output_size,
        ) if "lstm" in self.config.enabled_models else None
        return ForecastRunResult(
            predictions={},
            metadata={
                "window_shape": windows.features.shape,
                "target_shape": windows.targets.shape,
                "model": model,
            },
        )
