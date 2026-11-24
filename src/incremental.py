"""Incremental archive updates and full expanding-window retraining.

Supports:
1. Ingesting new observations into tabular and Zarr archives without rewriting
   the existing historical record.
2. Full retraining from scratch on the expanded history (expanding window),
   strictly without using `xgb_model=` warm starts to avoid sequential drift.
3. Skill-weighted ensembling of LSTM and XGBoost tabular models.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier, XGBRegressor

from src.ml.ensemble import (
    CausalLSTM,
    calculate_hindcast_skill_weights,
    make_windows,
    predict_lstm,
    tabular_ensemble_features,
    train_lstm,
    train_xgboost_regressor,
)
from src.ml.evaluation import classification_evaluation, regression_evaluation
from src.ml.temporal import PHASE_CLASSES, PHASE_NAMES, SUPPORTED_HORIZONS

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "dataset" / "features_master_unscaled.csv"
DEFAULT_RETRAIN_DIR = PROJECT_ROOT / "model" / "final_retrained"


def append_new_feature_observations(
    master_path: Path | str,
    new_data: pd.DataFrame | Path | str,
    time_col: str = "time",
) -> tuple[pd.DataFrame, int]:
    """Append new observations to the master dataset without rewriting the past.

    Parameters
    ----------
    master_path : Path | str
        Path to existing master features CSV.
    new_data : pd.DataFrame | Path | str
        DataFrame or path to CSV containing new incoming data rows.
    time_col : str
        Name of timestamp column.

    Returns
    -------
    tuple[pd.DataFrame, int]
        (updated_dataframe, number_of_new_rows_appended)
    """
    master_file = Path(master_path)
    if not master_file.is_file():
        raise FileNotFoundError(f"Master dataset not found: {master_file}")

    existing_df = pd.read_csv(master_file)
    if existing_df.empty or time_col not in existing_df.columns:
        raise ValueError(f"Existing master dataset is invalid or missing {time_col}")

    existing_df[time_col] = pd.to_datetime(existing_df[time_col])
    existing_timestamps = set(existing_df[time_col])
    latest_timestamp = existing_df[time_col].max()

    if isinstance(new_data, (str, Path)):
        new_df = pd.read_csv(new_data)
    else:
        new_df = new_data.copy()

    if time_col not in new_df.columns:
        raise ValueError(f"New data must contain '{time_col}' column")

    new_df[time_col] = pd.to_datetime(new_df[time_col])

    # Filter strictly new timestamps not present in archive
    novel_mask = ~new_df[time_col].isin(existing_timestamps)
    novel_rows = new_df[novel_mask].copy()

    if novel_rows.empty:
        logger.info("No new timestamps found. Archive remains unchanged at %s", latest_timestamp)
        return existing_df, 0

    # Align columns
    missing_cols = set(existing_df.columns) - set(novel_rows.columns)
    if missing_cols:
        for col in missing_cols:
            novel_rows[col] = np.nan

    novel_rows = novel_rows[existing_df.columns]

    # Append to existing archive without reprocessing past entries
    updated_df = pd.concat([existing_df, novel_rows], ignore_index=True)
    updated_df = updated_df.sort_values(time_col).reset_index(drop=True)
    updated_df.to_csv(master_file, index=False)

    logger.info(
        "Successfully appended %d new observation(s) through %s to %s",
        len(novel_rows),
        updated_df[time_col].max().strftime("%Y-%m"),
        master_file,
    )
    return updated_df, len(novel_rows)


def eligible_training_origins(
    frame: pd.DataFrame,
    horizon: int,
    window: int,
) -> np.ndarray:
    """Return origins whose horizon target is observed within the expanding window."""
    last_target_row = len(frame) - 1
    last_origin = last_target_row - horizon
    if last_origin < window - 1:
        raise ValueError(
            f"Not enough history for a {window}-month window and {horizon}-month lead"
        )
    return np.arange(window - 1, last_origin + 1, dtype=np.int64)


def retrain_from_full_data(
    data_path: Path | str | None = None,
    horizons: tuple[int, ...] = (1, 3, 6),
    epochs: int = 150,
    window: int = 12,
    hidden_size: int = 32,
    seed: int = 42,
    output_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Retrain all models from scratch on the full expanding window.

    CRITICAL:
    Does NOT use `xgb_model=` warm starts for XGBoost, because incremental
    boosting continuation leads to severe concept drift on time series.
    Instead, models are trained from scratch across all eligible historical data.

    Weights of the LSTM + XGBoost ensemble are dynamically computed from
    hindcast validation skill, not fixed constant values.
    """
    feature_file = Path(data_path or DEFAULT_DATA_PATH)
    target_dir = Path(output_dir or DEFAULT_RETRAIN_DIR)
    target_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(feature_file)
    frame["time"] = pd.to_datetime(frame["time"])
    frame = frame.sort_values("time").reset_index(drop=True)

    feature_columns = [
        c for c in frame.columns
        if c != "time" and not c.startswith("target_")
    ]
    cutoff_month = frame["time"].iloc[-1].strftime("%Y-%m")

    retrain_report: dict[str, Any] = {
        "status": "success",
        "retrain_mode": "expanding_window_full_retrain",
        "xgb_model_warm_start_used": False,
        "data_cutoff": cutoff_month,
        "sample_count": len(frame),
        "horizons": {},
    }

    for horizon in horizons:
        if horizon not in SUPPORTED_HORIZONS:
            continue

        oni_target = f"target_oni_lead_{horizon}m"
        phase_target = f"target_phase_lead_{horizon}m"

        origins = eligible_training_origins(frame, horizon, window)
        if len(origins) < 24:
            raise ValueError(f"Insufficient history ({len(origins)} origins) for lead {horizon}m")

        # Split expanding window into train and validation hindcast split
        # to assess out-of-sample skill without lookahead
        val_size = min(18, len(origins) // 4)
        train_origins = origins[:-val_size]
        val_origins = origins[-val_size:]

        # Fit scalers strictly on train origins
        feature_scaler = StandardScaler()
        train_scaled = feature_scaler.fit_transform(
            frame.iloc[: int(train_origins[-1]) + 1][feature_columns]
        ).astype(np.float32)
        all_scaled_features = feature_scaler.transform(frame[feature_columns]).astype(np.float32)

        target_scaler = StandardScaler()
        train_targets = frame.iloc[train_origins][oni_target].to_numpy(dtype=np.float64)
        target_scaler.fit(train_targets.reshape(-1, 1))

        # Windows for LSTM
        train_scaled_targets = target_scaler.transform(train_targets.reshape(-1, 1)).reshape(-1)
        train_windows = np.stack([
            all_scaled_features[orig - window + 1 : orig + 1]
            for orig in train_origins
        ])

        val_targets = frame.iloc[val_origins][oni_target].to_numpy(dtype=np.float64)
        val_scaled_targets = target_scaler.transform(val_targets.reshape(-1, 1)).reshape(-1)
        val_windows = np.stack([
            all_scaled_features[orig - window + 1 : orig + 1]
            for orig in val_origins
        ])

        # 1. Train CausalLSTM from scratch (fresh optimizer, fresh state)
        lstm = train_lstm(
            (train_windows, train_scaled_targets),
            (val_windows, val_scaled_targets),
            feature_count=len(feature_columns),
            hidden_size=hidden_size,
            epochs=epochs,
            batch_size=16,
            learning_rate=0.003,
            seed=seed + horizon,
        )

        val_lstm_scaled = predict_lstm(lstm, val_windows)
        val_lstm_forecast = target_scaler.inverse_transform(
            val_lstm_scaled.reshape(-1, 1)
        ).reshape(-1)

        # 2. Train XGBoost tabular regressor from scratch (xgb_model=None)
        train_tabular = frame.iloc[train_origins][feature_columns]
        val_tabular = frame.iloc[val_origins][feature_columns]

        xgb_reg = train_xgboost_regressor(
            train_tabular,
            train_targets,
            val_tabular,
            val_targets,
            random_state=seed + horizon,
        )
        val_xgb_forecast = xgb_reg.predict(val_tabular)

        # 3. Dynamic ensemble weighting from hindcast skill (inverse RMSE)
        ensemble_weights = calculate_hindcast_skill_weights(
            val_targets,
            {"lstm": val_lstm_forecast, "xgboost": val_xgb_forecast},
        )
        w_l = ensemble_weights["lstm"]
        w_x = ensemble_weights["xgboost"]

        val_ensemble_forecast = w_l * val_lstm_forecast + w_x * val_xgb_forecast
        val_ensemble_eval = regression_evaluation(val_targets, val_ensemble_forecast)

        # 4. Fit phase classifier on full expanding history with ensemble ONI
        all_train_windows = np.stack([
            all_scaled_features[orig - window + 1 : orig + 1]
            for orig in origins
        ])
        all_lstm_scaled = predict_lstm(lstm, all_train_windows)
        all_lstm_forecast = target_scaler.inverse_transform(
            all_lstm_scaled.reshape(-1, 1)
        ).reshape(-1)
        all_xgb_forecast = xgb_reg.predict(frame.iloc[origins][feature_columns])
        all_ensemble_oni = w_l * all_lstm_forecast + w_x * all_xgb_forecast

        classifier_features = frame.iloc[origins][feature_columns].copy().reset_index(drop=True)
        classifier_features["lstm_oni_forecast"] = all_ensemble_oni
        classifier_labels = frame.iloc[origins][phase_target].to_numpy(dtype=np.int64)

        classifier = XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=4,
            random_state=seed + horizon,
            n_jobs=-1,
        )
        # Full retrain from scratch without warm start:
        classifier.fit(classifier_features, classifier_labels, verbose=False)

        # Latest forecast from current latest data origin
        latest_window = all_scaled_features[-window:][None, ...]
        latest_lstm_scaled = predict_lstm(lstm, latest_window)
        latest_lstm_oni = float(
            target_scaler.inverse_transform(latest_lstm_scaled.reshape(-1, 1))[0, 0]
        )
        latest_tabular = frame.iloc[[-1]][feature_columns]
        latest_xgb_oni = float(xgb_reg.predict(latest_tabular)[0])
        latest_ensemble_oni = float(w_l * latest_lstm_oni + w_x * latest_xgb_oni)

        pred_row = latest_tabular.copy()
        pred_row["lstm_oni_forecast"] = latest_ensemble_oni
        phase_probs = classifier.predict_proba(pred_row)[0]
        predicted_phase_id = int(classifier.predict(pred_row)[0])

        horizon_dir = target_dir / f"horizon_{horizon}m"
        horizon_dir.mkdir(parents=True, exist_ok=True)
        (horizon_dir / "lstm").mkdir(parents=True, exist_ok=True)
        (horizon_dir / "classifier").mkdir(parents=True, exist_ok=True)
        (horizon_dir / "preprocessing").mkdir(parents=True, exist_ok=True)
        (horizon_dir / "metadata").mkdir(parents=True, exist_ok=True)

        torch.save(
            {
                "state_dict": lstm.state_dict(),
                "feature_columns": feature_columns,
                "hidden_size": hidden_size,
                "window": window,
                "horizon_months": horizon,
            },
            horizon_dir / "lstm" / "model.pt",
        )
        classifier.save_model(str(horizon_dir / "classifier" / "xgboost.json"))
        xgb_reg.save_model(str(horizon_dir / "xgboost_regressor.json"))
        joblib.dump(feature_scaler, horizon_dir / "preprocessing" / "feature_scaler.joblib")
        joblib.dump(target_scaler, horizon_dir / "preprocessing" / "target_scaler.joblib")

        horizon_metadata = {
            "horizon_months": horizon,
            "data_cutoff": cutoff_month,
            "training_samples": len(origins),
            "ensemble_weights": ensemble_weights,
            "validation_metrics": val_ensemble_eval,
            "latest_forecast": {
                "origin_month": cutoff_month,
                "target_month": (frame["time"].iloc[-1] + pd.DateOffset(months=horizon)).strftime("%Y-%m"),
                "lstm_predicted_oni": latest_lstm_oni,
                "xgboost_predicted_oni": latest_xgb_oni,
                "ensemble_predicted_oni": latest_ensemble_oni,
                "predicted_phase": PHASE_NAMES.get(predicted_phase_id, "Unknown"),
                "phase_probabilities": {
                    PHASE_NAMES[i]: float(phase_probs[i]) for i in range(len(phase_probs))
                },
            },
        }
        (horizon_dir / "metadata" / "training_metadata.json").write_text(
            json.dumps(horizon_metadata, indent=2), encoding="utf-8"
        )
        retrain_report["horizons"][str(horizon)] = horizon_metadata

    manifest = {
        "artifact_kind": "final_forecasting_models",
        "model_version": f"retrained_{cutoff_month}",
        "forecast_origin": cutoff_month,
        "forecast_horizons": list(horizons),
        "promotion_status": "experimental_not_production_ready",
        "feature_columns": feature_columns,
        "model_directories": {
            str(h): f"horizon_{h}m" for h in horizons
        },
    }
    (target_dir / "model_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return retrain_report


def update_pipeline_and_retrain(
    new_data: pd.DataFrame | Path | str,
    master_path: Path | str | None = None,
    horizons: tuple[int, ...] = (1, 3, 6),
    epochs: int = 150,
    seed: int = 42,
    force_retrain: bool = False,
) -> dict[str, Any]:
    """Incrementally ingest new data and perform full expanding-window retraining."""
    target_master = Path(master_path or DEFAULT_DATA_PATH)
    updated_df, added_rows = append_new_feature_observations(target_master, new_data)

    if added_rows == 0 and not force_retrain:
        return {
            "status": "up_to_date",
            "message": "No new records to append; retrain skipped.",
            "data_cutoff": updated_df["time"].max().strftime("%Y-%m"),
            "rows_appended": 0,
        }

    retrain_report = retrain_from_full_data(
        data_path=target_master,
        horizons=horizons,
        epochs=epochs,
        seed=seed,
    )
    retrain_report["rows_appended"] = added_rows
    return retrain_report
