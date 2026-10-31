"""Statistical baselines and training-window preprocessing.

This module contains the reference models that every learned forecast must
beat. All climatology statistics must be fitted only on the training portion
of a chronological split.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BaselineResult:
    """Prediction array and optional reference values used by an evaluator."""

    prediction: np.ndarray
    reference: np.ndarray | None = None


def validate_series(values: pd.Series) -> pd.Series:
    """Validate and normalize a monthly forecast target."""
    if values.empty:
        raise ValueError("Target series is empty")
    if values.index.has_duplicates:
        raise ValueError("Target index contains duplicate timestamps")
    if not isinstance(values.index, pd.DatetimeIndex):
        raise TypeError("Target index must be a pandas DatetimeIndex")
    if not values.index.is_monotonic_increasing:
        raise ValueError("Target index must be sorted chronologically")
    return values.astype(float)


def persistence_forecast(values: pd.Series, horizon: int) -> BaselineResult:
    """Repeat the last observed value for the requested future horizon."""
    validate_series(values)
    if horizon < 1:
        raise ValueError("horizon must be at least 1 month")
    prediction = np.repeat(float(values.iloc[-1]), horizon)
    return BaselineResult(prediction, values.to_numpy(dtype=float))


def seasonal_climatology(
    training_values: pd.Series,
    forecast_dates: pd.DatetimeIndex,
) -> BaselineResult:
    """Predict each calendar month's training-period mean."""
    training_values = validate_series(training_values)
    if len(forecast_dates) == 0:
        raise ValueError("forecast_dates cannot be empty")

    climatology = training_values.groupby(training_values.index.month).mean()
    missing_months = sorted(set(forecast_dates.month) - set(climatology.index))
    if missing_months:
        raise ValueError(f"Training data has no samples for months: {missing_months}")

    prediction = np.asarray(
        [climatology.loc[int(date.month)] for date in forecast_dates],
        dtype=float,
    )
    return BaselineResult(prediction, training_values.to_numpy(dtype=float))


def seasonal_naive(
    values: pd.Series,
    horizon: int,
    years: int = 1,
    forecast_dates: pd.DatetimeIndex | None = None,
) -> BaselineResult:
    """Use the value from the same calendar month in the requested prior year."""
    validate_series(values)
    if horizon < 1 or years < 1:
        raise ValueError("horizon and years must be at least 1")
    if len(values) < 12 * years:
        raise ValueError(f"At least {12 * years} months are required")

    if forecast_dates is None:
        forecast_dates = pd.date_range(
            values.index[-1] + pd.offsets.MonthBegin(1),
            periods=horizon,
            freq="MS",
        )

    prediction = []
    for forecast_date in forecast_dates:
        reference = forecast_date - pd.DateOffset(years=years)
        candidates = values.index[
            (values.index.year == reference.year)
            & (values.index.month == reference.month)
        ]
        if len(candidates) == 0:
            raise ValueError(
                f"Training data has no month matching {reference.strftime('%Y-%m')}"
            )
        prediction.append(values.loc[candidates[0]])

    return BaselineResult(
        np.asarray(prediction, dtype=float),
        values.to_numpy(dtype=float),
    )
