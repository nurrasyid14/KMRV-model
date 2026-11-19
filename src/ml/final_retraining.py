"""Final forecasting-model retraining, separate from historical evaluation."""

from __future__ import annotations

import importlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import matplotlib
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.ml.backtesting import (
    LSTMConfig,
    _balanced_class_weights,
    _classifier_features,
    _oof_lstm_forecasts,
    _seed_everything,
)
from src.ml.ensemble import predict_lstm, train_lstm
from src.ml.lgbm_classifier import create_phase_classifier as create_lgbm_classifier
from src.ml.temporal import (
    PHASE_CLASSES,
    SUPPORTED_HORIZONS,
    BacktestFold,
    load_feature_data,
    resolve_feature_columns,
    windows_for_origins,
)
from src.ml.xgb_classifier import create_phase_classifier as create_xgb_classifier

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "dataset" / "features_master_unscaled.csv"
DEFAULT_SELECTION_PATH = PROJECT_ROOT / "reports" / "model_comparison" / "model_selection.json"
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "model" / "final_retrained"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports"
SELECTION_METADATA_DIR = PROJECT_ROOT / "model" / "backtesting_final_holdout"
EXPECTED_SELECTION = {
    1: ("XGBoost", "balanced"),
    3: ("LightGBM", "unweighted"),
    6: ("XGBoost", "balanced"),
}
PHASE_LABELS = {0: "La Nina", 1: "Neutral", 2: "El Nino"}

LSTM_MODULE = importlib.import_module("src.ml.2lstm")
CausalLSTM = LSTM_MODULE.CausalLSTM


def eligible_training_origins(
    frame: pd.DataFrame,
    horizon: int,
    window: int,
) -> np.ndarray:
    """Return origins whose horizon target is observed by the final data date."""
    if horizon not in SUPPORTED_HORIZONS:
        raise ValueError(f"Unsupported forecast horizon: {horizon}")
    if window < 1:
        raise ValueError("Sliding window must be positive")

    last_target_row = len(frame) - 1
    last_origin = last_target_row - horizon
    if last_origin < window - 1:
        raise ValueError(
            f"Not enough history for a {window}-month window and "
            f"{horizon}-month target"
        )

    origins = np.arange(window - 1, last_origin + 1, dtype=np.int64)
    target_times = frame["time"].iloc[origins + horizon].to_numpy()
    origin_times = frame["time"].iloc[origins].to_numpy()
    if not np.all(target_times > origin_times):
        raise ValueError(f"{horizon}-month targets must follow their origins")
    if np.any(target_times > frame["time"].iloc[-1].to_datetime64()):
        raise ValueError(f"{horizon}-month training targets exceed the data cutoff")
    return origins


def forecast_support(forecast_months: int) -> list[dict[str, object]]:
    if forecast_months <= 0:
        raise ValueError("Forecast months must be a positive integer")
    return [
        {
            "horizon_months": horizon,
            "forecast_generated": horizon in SUPPORTED_HORIZONS,
            "status": (
                "direct_model_forecast"
                if horizon in SUPPORTED_HORIZONS
                else "unsupported_by_current_model"
            ),
            "reason": (
                None
                if horizon in SUPPORTED_HORIZONS
                else "No validated direct model exists for this lead; no interpolation or recursion is applied."
            ),
        }
        for horizon in range(1, forecast_months + 1)
    ]


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_safe(payload), indent=2, allow_nan=False),
        encoding="utf-8",
    )


def _read_frozen_configuration(
    selection_path: Path,
    horizon: int,
    feature_columns: list[str],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if selection.get("test_metrics_used_for_selection") is not False:
        raise ValueError("Frozen model selection does not prove test-independent selection")

    choice = selection.get("selected_models", {}).get(str(horizon))
    expected_family, expected_strategy = EXPECTED_SELECTION[horizon]
    if not isinstance(choice, dict):
        raise ValueError(f"No frozen model-selection record for horizon {horizon}")
    if (
        choice.get("model") != expected_family
        or choice.get("imbalance_strategy") != expected_strategy
        or choice.get("selection_uses_test_metrics") is not False
        or choice.get("selection_is_provisional") is not True
        or choice.get("selection_status") != "provisional_candidate"
        or choice.get("validation_actual_class_coverage") != 3
    ):
        raise ValueError(
            f"Horizon {horizon} selection record is missing, invalid, "
            "or differs from the frozen validation-only candidate"
        )

    metadata_dir = (
        SELECTION_METADATA_DIR
        / f"horizon_{horizon}m"
        / f"{expected_family.lower()}_{expected_strategy}"
    )
    metadata_path = metadata_dir / "metadata.json"
    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"Selected model metadata is unavailable: {metadata_path}"
        )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    saved_features = metadata.get("feature_configuration", {}).get(
        "feature_columns"
    )
    if (
        metadata.get("classifier") != expected_family
        or metadata.get("imbalance_strategy") != expected_strategy
        or metadata.get("selection_is_provisional") is not True
        or saved_features != feature_columns
        or metadata.get("forecast_horizon_months") != horizon
    ):
        raise ValueError(
            f"Horizon {horizon} model metadata does not match the frozen selection "
            "or current feature schema"
        )

    validation_keys = (
        "selection_validation_fold",
        "selection_status",
        "validation_macro_f1",
        "validation_balanced_accuracy",
        "validation_macro_precision",
        "validation_macro_recall",
        "validation_log_loss",
        "validation_multiclass_brier_score",
        "validation_top_label_ece_10_bins",
        "validation_actual_class_coverage",
        "validation_oni_rmse",
        "selection_uses_test_metrics",
        "selection_is_provisional",
    )
    validation_summary = {key: choice.get(key) for key in validation_keys}
    return choice, metadata, validation_summary


def _classifier_for_final_fit(
    family: str,
    strategy: str,
    selected_params: dict[str, Any],
    labels: np.ndarray,
) -> tuple[Any, np.ndarray | None, dict[int, float]]:
    iterations = int(selected_params["n_estimators"])
    random_state = int(selected_params["random_state"])
    if family == "XGBoost":
        classifier = create_xgb_classifier(
            random_state=random_state,
            iterations=iterations,
            early_stopping_rounds=None,
        )
        weights = (
            compute_sample_weight(class_weight="balanced", y=labels)
            if strategy == "balanced"
            else None
        )
        return classifier, weights, {}
    if family == "LightGBM":
        class_weights = (
            _balanced_class_weights(labels) if strategy == "balanced" else {}
        )
        return (
            create_lgbm_classifier(
                random_state=random_state,
                iterations=iterations,
                class_weight=class_weights or None,
            ),
            None,
            class_weights,
        )
    raise ValueError(f"Unsupported selected classifier: {family}")


def _validate_classifier_parameters(family: str, selected: dict[str, Any]) -> None:
    if family == "XGBoost":
        model = create_xgb_classifier(
            random_state=int(selected["random_state"]),
            iterations=int(selected["n_estimators"]),
            early_stopping_rounds=None,
        )
        keys = (
            "objective",
            "num_class",
            "learning_rate",
            "max_depth",
            "min_child_weight",
            "subsample",
            "colsample_bytree",
            "reg_lambda",
            "tree_method",
            "eval_metric",
            "n_jobs",
        )
    elif family == "LightGBM":
        model = create_lgbm_classifier(
            random_state=int(selected["random_state"]),
            iterations=int(selected["n_estimators"]),
            class_weight=None,
        )
        keys = (
            "objective",
            "num_class",
            "learning_rate",
            "max_depth",
            "num_leaves",
            "min_child_samples",
            "subsample",
            "colsample_bytree",
            "reg_lambda",
            "verbosity",
        )
    else:
        raise ValueError(f"Unsupported selected classifier: {family}")

    actual_params = model.get_params()
    mismatches = {
        key: {"selected": selected.get(key), "factory": actual_params.get(key)}
        for key in keys
        if selected.get(key) != actual_params.get(key)
    }
    if mismatches:
        raise ValueError(
            f"Selected {family} parameters cannot be reproduced: {mismatches}"
        )


def _train_horizon(
    frame: pd.DataFrame,
    feature_columns: list[str],
    horizon: int,
    choice: dict[str, Any],
    metadata: dict[str, Any],
    validation_summary: dict[str, Any],
    model_version: str,
    forecast_origin: pd.Timestamp,
    artifact_dir: Path,
    selection_path: Path,
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    parameters = metadata["hyperparameters"]
    lstm_parameters = parameters["lstm"]
    classifier_parameters = parameters["classifier"]
    window = int(lstm_parameters["window"])
    hidden_size = int(lstm_parameters["hidden_size"])
    refit_epochs = int(lstm_parameters["refit_epochs"])
    if refit_epochs <= 0:
        raise ValueError(f"Horizon {horizon} has an invalid frozen LSTM epoch count")
    _validate_classifier_parameters(choice["model"], classifier_parameters)

    origins = eligible_training_origins(frame, horizon, window)
    max_origin = int(origins[-1])
    target_column = f"target_oni_lead_{horizon}m"
    phase_column = f"target_phase_lead_{horizon}m"

    feature_scaler = StandardScaler()
    feature_scaler.fit(frame.iloc[:max_origin + 1][feature_columns])
    scaled_features = feature_scaler.transform(frame[feature_columns]).astype(
        np.float32
    )
    target_scaler = StandardScaler()
    eligible_targets = frame.iloc[origins][target_column].to_numpy(
        dtype=np.float64
    )
    scaled_targets = target_scaler.fit_transform(
        eligible_targets.reshape(-1, 1)
    ).reshape(-1).astype(np.float32)
    training_windows = windows_for_origins(scaled_features, origins, window)
    _seed_everything(seed + horizon)
    lstm = train_lstm(
        (training_windows, scaled_targets),
        None,
        len(feature_columns),
        hidden_size,
        refit_epochs,
        int(lstm_parameters["batch_size"]),
        float(lstm_parameters["learning_rate"]),
        seed + horizon,
    )

    final_window = scaled_features[-window:][None, ...]
    scaled_forecast = predict_lstm(lstm, final_window)
    predicted_oni = float(
        target_scaler.inverse_transform(scaled_forecast.reshape(-1, 1))[0, 0]
    )

    cutoff_fold = BacktestFold(
        fold_id=int(choice["selection_validation_fold"]),
        train_end=len(frame),
        validation_end=len(frame),
        test_end=len(frame),
    )
    config = LSTMConfig(
        window=window,
        hidden_size=hidden_size,
        epochs=int(lstm_parameters["epochs"]),
        batch_size=int(lstm_parameters["batch_size"]),
        learning_rate=float(lstm_parameters["learning_rate"]),
    )
    oof_origins, oof_oni = _oof_lstm_forecasts(
        frame,
        feature_columns,
        target_column,
        cutoff_fold,
        horizon,
        config,
        seed,
    )
    if (
        len(np.unique(oof_origins)) != len(oof_origins)
        or np.any(oof_origins + horizon >= len(frame))
    ):
        raise ValueError(f"Horizon {horizon} OOF origins cross the data cutoff")
    oof_features = _classifier_features(
        frame,
        feature_columns,
        oof_origins,
        oof_oni,
    )
    oof_labels = frame.iloc[oof_origins][phase_column].to_numpy(dtype=np.int64)
    if set(oof_labels.tolist()) != set(PHASE_CLASSES.tolist()):
        raise ValueError(
            f"Horizon {horizon} OOF training labels do not contain all phases"
        )

    classifier, sample_weights, final_class_weights = _classifier_for_final_fit(
        choice["model"],
        choice["imbalance_strategy"],
        classifier_parameters,
        oof_labels,
    )
    fit_kwargs = {}
    if sample_weights is not None:
        fit_kwargs["sample_weight"] = sample_weights
    classifier.fit(oof_features, oof_labels, **fit_kwargs)
    forecast_features = frame.loc[[frame.index[-1]], feature_columns].copy()
    forecast_features["lstm_oni_forecast"] = predicted_oni
    forecast_features = forecast_features[oof_features.columns]
    probabilities = classifier.predict_proba(forecast_features)[0]
    classes = np.asarray(classifier.classes_, dtype=np.int64)
    if not np.array_equal(classes, PHASE_CLASSES) or len(probabilities) != 3:
        raise ValueError(
            f"Horizon {horizon} classifier probabilities do not cover all phases"
        )
    predicted_phase = int(classifier.predict(forecast_features)[0])

    model_dir = artifact_dir / f"horizon_{horizon}m"
    lstm_dir = model_dir / "lstm"
    classifier_dir = model_dir / "classifier"
    preprocessing_dir = model_dir / "preprocessing"
    metadata_dir = model_dir / "metadata"
    for directory in (lstm_dir, classifier_dir, preprocessing_dir, metadata_dir):
        directory.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "state_dict": lstm.state_dict(),
        "feature_columns": feature_columns,
        "hidden_size": hidden_size,
        "window": window,
        "horizon_months": horizon,
        "model_version": model_version,
        "loss_history": getattr(lstm, "loss_history", []),
    }
    torch.save(checkpoint, lstm_dir / "model.pt")
    if choice["model"] == "LightGBM":
        classifier.booster_.save_model(str(classifier_dir / "lightgbm.txt"))
        classifier_filename = "lightgbm.txt"
    else:
        classifier.save_model(str(classifier_dir / "xgboost.json"))
        classifier_filename = "xgboost.json"
    joblib.dump(feature_scaler, preprocessing_dir / "feature_scaler.joblib")
    joblib.dump(target_scaler, preprocessing_dir / "target_scaler.joblib")
    _write_json(
        preprocessing_dir / "feature_columns.json",
        {"feature_columns": feature_columns},
    )

    target_times = frame["time"].iloc[origins + horizon]
    oof_target_times = frame["time"].iloc[oof_origins + horizon]
    feature_fit_end = frame["time"].iloc[max_origin]
    model_metadata = {
        "model_name": f"causal_lstm_{choice['model'].lower()}",
        "artifact_kind": "final_forecasting_model",
        "promotion_status": "experimental_not_production_ready",
        "model_version": model_version,
        "horizon_months": horizon,
        "forecast_origin": forecast_origin.date().isoformat(),
        "training_data": {
            "historical_range": {
                "start": frame["time"].iloc[0].date().isoformat(),
                "end": forecast_origin.date().isoformat(),
            },
            "eligible_origin_range": {
                "start": frame["time"].iloc[origins[0]].date().isoformat(),
                "end": frame["time"].iloc[origins[-1]].date().isoformat(),
            },
            "eligible_target_range": {
                "start": target_times.iloc[0].date().isoformat(),
                "end": target_times.iloc[-1].date().isoformat(),
            },
            "eligible_sample_count": int(len(origins)),
            "validation_and_test_reused_for_final_fit": True,
            "independent_final_test_score_reported": False,
        },
        "feature_configuration": {
            "window_months": window,
            "feature_columns": feature_columns,
            "feature_count": len(feature_columns),
            "target_columns_excluded": True,
            "imputation": "none; incomplete or non-finite inputs are rejected",
            "feature_selection": "none; frozen historical schema",
        },
        "preprocessing": {
            "feature_scaler": {
                "type": "StandardScaler",
                "fit_start": frame["time"].iloc[0].date().isoformat(),
                "fit_end": feature_fit_end.date().isoformat(),
                "fit_row_count": int(max_origin + 1),
            },
            "target_scaler": {
                "type": "StandardScaler",
                "fit_target_time_start": target_times.iloc[0].date().isoformat(),
                "fit_target_time_end": target_times.iloc[-1].date().isoformat(),
                "fit_target_count": int(len(origins)),
            },
        },
        "lstm": {
            "architecture": "CausalLSTM",
            "hidden_size": hidden_size,
            "dropout": 0.1,
            "batch_size": int(lstm_parameters["batch_size"]),
            "learning_rate": float(lstm_parameters["learning_rate"]),
            "final_refit_epochs": refit_epochs,
            "epoch_count_source": "frozen pre-test training metadata",
            "training_windows": int(len(origins)),
        },
        "classifier": {
            "family": choice["model"],
            "imbalance_strategy": choice["imbalance_strategy"],
            "artifact_file": classifier_filename,
            "parameters": {
                key: classifier_parameters.get(key)
                for key in (
                    "objective",
                    "num_class",
                    "n_estimators",
                    "learning_rate",
                    "max_depth",
                    "num_leaves",
                    "min_child_samples",
                    "min_child_weight",
                    "subsample",
                    "colsample_bytree",
                    "reg_lambda",
                    "random_state",
                )
                if key in classifier_parameters
            },
            "oof_training_origins": int(len(oof_origins)),
            "oof_origin_start": frame["time"].iloc[oof_origins[0]].date().isoformat(),
            "oof_origin_end": frame["time"].iloc[oof_origins[-1]].date().isoformat(),
            "oof_target_end": oof_target_times.iloc[-1].date().isoformat(),
            "oof_class_counts": {
                str(int(class_id)): int(np.count_nonzero(oof_labels == class_id))
                for class_id in PHASE_CLASSES
            },
            "final_class_weights": {
                str(key): value for key, value in final_class_weights.items()
            },
            "probabilities_calibrated": False,
        },
        "model_selection_provenance": {
            "selection_file": str(selection_path),
            "selection_source": "validation metrics only",
            "test_metrics_used_for_selection": False,
            "candidate_status": "provisional_candidate",
            "production_promotion": "not approved; only one validation and one test period",
            "validation_summary": validation_summary,
        },
        "random_seed": seed + horizon,
    }
    _write_json(metadata_dir / "training_metadata.json", model_metadata)

    forecast_row = {
        "forecast_origin": forecast_origin.date().isoformat(),
        "forecast_date": (
            forecast_origin + pd.DateOffset(months=horizon)
        ).date().isoformat(),
        "horizon_months": horizon,
        "predicted_oni": predicted_oni,
        "predicted_phase": PHASE_LABELS[predicted_phase],
        "probability_la_nina": float(probabilities[0]),
        "probability_neutral": float(probabilities[1]),
        "probability_el_nino": float(probabilities[2]),
        "phase_confidence": float(np.max(probabilities)),
        "probabilities_calibrated": False,
        "model_name": model_metadata["model_name"],
        "model_version": model_version,
        "is_forecast": True,
    }
    audit_horizon = {
        "eligible_origins": int(len(origins)),
        "eligible_origin_start": frame["time"].iloc[origins[0]].date().isoformat(),
        "eligible_origin_end": frame["time"].iloc[origins[-1]].date().isoformat(),
        "eligible_target_end": target_times.iloc[-1].date().isoformat(),
        "feature_scaler_fit_end": feature_fit_end.date().isoformat(),
        "target_scaler_fit_end": target_times.iloc[-1].date().isoformat(),
        "oof_forecast_count": int(len(oof_origins)),
        "oof_origin_start": frame["time"].iloc[oof_origins[0]].date().isoformat(),
        "oof_origin_end": frame["time"].iloc[oof_origins[-1]].date().isoformat(),
        "oof_target_end": oof_target_times.iloc[-1].date().isoformat(),
        "oof_targets_at_or_before_forecast_origin": bool(
            (oof_target_times <= frame["time"].iloc[-1]).all()
        ),
    }
    return forecast_row, {
        "metadata": model_metadata,
        "audit": audit_horizon,
        "classifier": classifier,
    }


def _phase_from_oni(values: pd.Series) -> np.ndarray:
    oni = values.to_numpy(dtype=np.float64)
    return np.where(oni < -0.5, 0, np.where(oni > 0.5, 2, 1)).astype(np.int64)


def _plot_forecasts(
    frame: pd.DataFrame,
    forecasts: pd.DataFrame,
    report_dir: Path,
) -> list[str]:
    plot_dir = report_dir / "final_retrained"
    plot_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    historical_phase = _phase_from_oni(frame["oni_anom"])
    phase_y = {0: -1, 1: 0, 2: 1}
    colors = {0: "#2563eb", 1: "#6b7280", 2: "#dc2626"}

    fig, axis = plt.subplots(figsize=(12, 5))
    axis.plot(frame["time"], frame["oni_anom"], color="#1f2937", label="Observed ONI")
    axis.scatter(
        pd.to_datetime(forecasts["forecast_date"]),
        forecasts["predicted_oni"],
        color="#f59e0b",
        marker="D",
        s=65,
        label="Direct model forecasts (1/3/6-month leads)",
        zorder=3,
    )
    axis.axhline(0.5, color="#dc2626", linestyle=":", linewidth=1)
    axis.axhline(-0.5, color="#2563eb", linestyle=":", linewidth=1)
    axis.set(title="Observed ONI and supported direct forecasts", ylabel="ONI anomaly")
    axis.legend()
    fig.tight_layout()
    path = plot_dir / "historical_and_forecast_oni.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    created.append(str(path.relative_to(PROJECT_ROOT)))

    fig, axis = plt.subplots(figsize=(12, 4))
    axis.scatter(
        frame["time"],
        [phase_y[int(phase)] for phase in historical_phase],
        color=[colors[int(phase)] for phase in historical_phase],
        s=16,
        label="Observed ONI-derived phase",
    )
    forecast_phases = forecasts["predicted_phase"].map(
        {"La Nina": 0, "Neutral": 1, "El Nino": 2}
    )
    axis.scatter(
        pd.to_datetime(forecasts["forecast_date"]),
        [phase_y[int(phase)] for phase in forecast_phases],
        marker="D",
        color=[colors[int(phase)] for phase in forecast_phases],
        s=65,
        label="Predicted phase",
    )
    axis.set_yticks([-1, 0, 1], ["La Nina", "Neutral", "El Nino"])
    axis.set(title="Observed and predicted ENSO phase", ylabel="Phase")
    axis.legend()
    fig.tight_layout()
    path = plot_dir / "historical_and_forecast_phase.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    created.append(str(path.relative_to(PROJECT_ROOT)))

    fig, axis = plt.subplots(figsize=(10, 5))
    for column, label, color in (
        ("probability_la_nina", "La Nina", colors[0]),
        ("probability_neutral", "Neutral", colors[1]),
        ("probability_el_nino", "El Nino", colors[2]),
    ):
        axis.plot(
            pd.to_datetime(forecasts["forecast_date"]),
            forecasts[column],
            marker="o",
            label=label,
            color=color,
        )
    axis.set_ylim(0, 1)
    axis.set(title="Uncalibrated classifier probabilities at supported leads", ylabel="Probability")
    axis.legend()
    fig.tight_layout()
    path = plot_dir / "forecast_phase_probabilities.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    created.append(str(path.relative_to(PROJECT_ROOT)))

    for horizon in SUPPORTED_HORIZONS:
        rows = forecasts.loc[forecasts["horizon_months"] == horizon]
        fig, axes = plt.subplots(3, 1, figsize=(11, 9))
        axes[0].plot(frame["time"], frame["oni_anom"], color="#1f2937")
        axes[0].scatter(
            pd.to_datetime(rows["forecast_date"]),
            rows["predicted_oni"],
            color="#f59e0b",
            marker="D",
            s=65,
        )
        axes[0].axhline(0.5, color="#dc2626", linestyle=":")
        axes[0].axhline(-0.5, color="#2563eb", linestyle=":")
        axes[0].set_ylabel("ONI")
        axes[0].set_title(f"Direct {horizon}-month forecast")

        axes[1].scatter(
            frame["time"],
            [phase_y[int(phase)] for phase in historical_phase],
            color="#6b7280",
            s=12,
        )
        if not rows.empty:
            phase_id = int(
                rows["predicted_phase"].map(
                    {"La Nina": 0, "Neutral": 1, "El Nino": 2}
                ).iloc[0]
            )
            axes[1].scatter(
                pd.to_datetime(rows["forecast_date"]),
                [phase_y[phase_id]],
                color=colors[phase_id],
                marker="D",
                s=65,
            )
        axes[1].set_yticks([-1, 0, 1], ["La Nina", "Neutral", "El Nino"])
        axes[1].set_ylabel("Phase")

        if not rows.empty:
            forecast_date = pd.to_datetime(rows["forecast_date"].iloc[0])
            axes[2].bar(
                ["La Nina", "Neutral", "El Nino"],
                [
                    rows["probability_la_nina"].iloc[0],
                    rows["probability_neutral"].iloc[0],
                    rows["probability_el_nino"].iloc[0],
                ],
                color=[colors[0], colors[1], colors[2]],
            )
            axes[2].set_title(f"Uncalibrated phase probabilities for {forecast_date:%Y-%m}")
        axes[2].set_ylim(0, 1)
        axes[2].set_ylabel("Probability")
        fig.tight_layout()
        path = plot_dir / f"forecast_horizon_{horizon}m.png"
        fig.savefig(path, dpi=150)
        plt.close(fig)
        created.append(str(path.relative_to(PROJECT_ROOT)))
    return created


def _write_final_report(
    report_path: Path,
    forecast_origin: pd.Timestamp,
    forecast_months: int,
    forecast_rows: list[dict[str, Any]],
    support: list[dict[str, object]],
    plots: list[str],
) -> None:
    generated = [row for row in support if row["forecast_generated"]]
    unsupported = [row for row in support if not row["forecast_generated"]]
    lines = [
        "# Final ENSO forecasting model and forecast",
        "",
        f"- Forecast origin: **{forecast_origin:%Y-%m}**.",
        f"- Requested period: **{forecast_months} months**.",
        f"- Model-supported direct leads: **{', '.join(str(row['horizon_months']) for row in generated)}**.",
        f"- Unsupported requested leads: **{len(unsupported)}**; these are not interpolated or recursively forecast.",
        "- Model status: **experimental forecasting candidate; not approved for production**.",
        "- Phase probabilities are classifier outputs and are **not calibrated probabilities**.",
        "",
        "## Retraining and evaluation separation",
        "",
        "The separate `model/final_retrained/` artifacts use all target observations whose target month is no later than the final historical data month. This includes rows previously used in training, validation, and test. Historical backtesting outputs are not changed. No final retraining score is reported as an independent test result, and no test metric is used to choose the frozen model family or imbalance strategy.",
        "",
        "Candidates are frozen from the existing validation-only selection record: XGBoost/balanced at 1 and 6 months, and LightGBM/unweighted at 3 months. They remain provisional because the historical record has one validation and one test period, and validation also informed tree early stopping.",
        "",
        "## Leakage controls",
        "",
        "- Target rows are eligible only when `origin + horizon <= forecast origin`; the 12-month input window ends at its origin.",
        "- LSTM feature and target scalers are fitted only on eligible historical features/targets for each lead. No imputer or feature selection is used.",
        "- Classifier fitting uses chronological expanding-window out-of-fold LSTM forecasts; no in-sample LSTM predictions are used.",
        "- Future climate features and future ONI are not generated or read for inference. The direct forecast uses the latest historical feature window.",
        "- Notebook engineering constructs lag features with positive shifts and rolling features from lag-1 values; no target columns enter the feature schema.",
        "- Continuous ONI and phase are separate model outputs; the classifier phase can disagree with the LSTM's ONI threshold.",
        "",
        "## Feature availability and forecast limitations",
        "",
        "The dataset does not record source-specific publication/availability timestamps. Contemporary ONI, SST, MHW, SOI/DMI, and rainfall values are used at the forecast origin, so the forecasts are conditional on those monthly values having been finalized and available at issuance. This has not been independently verified; the audit records it as an unresolved operational limitation. Accordingly, the audit is not marked fully passed and the artifacts are not production-approved.",
        "",
        "Current models support direct leads 1, 3, and 6 only. For an 18-month request, only July 2025, September 2025, and December 2025 are predicted for a June 2025 origin. The other 15 months are explicitly unsupported. Full monthly coverage requires separately trained and temporally evaluated direct models for each lead, or a separately validated recursive system that forecasts every required input variable.",
        "",
        "## Forecast rows",
        "",
        "| Lead (months) | Target month | Predicted ONI | Predicted phase |",
        "| ---: | --- | ---: | --- |",
    ]
    for row in forecast_rows:
        lines.append(
            f"| {row['horizon_months']} | {row['forecast_date'][:7]} | "
            f"{row['predicted_oni']:.4f} | {row['predicted_phase']} |"
        )
    lines.extend(["", "## Visualizations", ""])
    lines.extend(f"- `{path}`" for path in plots)
    lines.extend(
        [
            "",
            "The exact machine-readable audit is in `reports/final_retraining_leakage_audit.json`; supported forecast rows are in `reports/final_retrained/forecast.csv` and `forecast.json`.",
            "",
            "## Run",
            "",
            "```powershell",
            "python main.py --final-retrain --forecast-months 18",
            "```",
            "",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_final_retraining(
    forecast_months: int = 18,
    data_path: Path = DEFAULT_DATA_PATH,
    selection_path: Path = DEFAULT_SELECTION_PATH,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
) -> dict[str, Any]:
    if forecast_months <= 0:
        raise ValueError("Forecast months must be a positive integer")
    artifact_dir = artifact_dir.resolve()
    report_dir = report_dir.resolve()
    report_output_dir = report_dir / "final_retrained"
    audit_path = report_dir / "final_retraining_leakage_audit.json"

    required_history = (
        report_dir / "final_audit" / "final_recommendation.md",
        report_dir / "final_audit" / "leakage_audit.md",
    )
    missing_history = [str(path) for path in required_history if not path.is_file()]
    if missing_history:
        raise FileNotFoundError(
            "Historical evaluation/audit is incomplete; final retraining requires "
            f"these reports: {missing_history}"
        )
    if not selection_path.is_file():
        raise FileNotFoundError(f"Frozen model selection is unavailable: {selection_path}")

    frame = load_feature_data(data_path, verify_target_alignment=True)
    feature_columns = resolve_feature_columns(frame)
    if not feature_columns or any(column.startswith("target_") for column in feature_columns):
        raise ValueError("The final model feature schema is empty or contains targets")
    forecast_origin = pd.Timestamp(frame["time"].iloc[-1])
    model_version = datetime.now(timezone.utc).strftime("final-%Y%m%dT%H%M%SZ")
    support = forecast_support(forecast_months)

    selected: dict[int, tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = {}
    for horizon in SUPPORTED_HORIZONS:
        selected[horizon] = _read_frozen_configuration(
            selection_path,
            horizon,
            feature_columns,
        )

    audit: dict[str, Any] = {
        "audit_version": 1,
        "model_version": model_version,
        "forecast_origin": forecast_origin.date().isoformat(),
        "historical_data_range": {
            "start": frame["time"].iloc[0].date().isoformat(),
            "end": forecast_origin.date().isoformat(),
            "row_count": int(len(frame)),
        },
        "validation_test_reuse": {
            "historical_train_validation_test_observations_reused": True,
            "historical_evaluation_reports_modified": False,
            "final_retraining_scored_as_independent_test": False,
            "test_metrics_used_for_selection": False,
        },
        "feature_timestamp_checks": {
            "monthly_index_ordered_unique_contiguous": True,
            "target_columns_excluded_from_features": True,
            "source_as_of_timestamps_available": False,
            "status": "not_independently_verified",
            "warning": "Contemporaneous source values must be finalized and available by issuance; source-specific release timestamps are not recorded.",
        },
        "target_alignment_checks": {
            "validated_against_shifted_observed_oni": True,
            "target_month_strictly_after_each_origin": True,
            "eligible_target_cutoff": "origin + horizon <= forecast origin",
        },
        "sliding_window_checks": {
            "window_months": 12,
            "window_ends_at_forecast_origin": True,
            "future_features_used": False,
        },
        "scaler_and_imputer_checks": {
            "feature_scalers_fit_on_eligible_rows_only": True,
            "target_scalers_fit_on_eligible_targets_only": True,
            "imputation_used": False,
        },
        "lstm_stacking_checks": {
            "classifier_features_use_chronological_oof_lstm_forecasts": True,
            "in_sample_lstm_predictions_used_for_classifier": False,
        },
        "phase_output_relationship": {
            "phase_probabilities_come_from_selected_classifier": True,
            "predicted_oni_comes_from_lstm_regressor": True,
            "outputs_are_independently_predicted_and_may_disagree": True,
        },
        "future_feature_availability": {
            "future_climate_features_fabricated": False,
            "future_oni_used_as_input": False,
            "required_input": "Observed feature window ending at the forecast origin; source release timing remains unverified.",
        },
        "model_selection_provenance": {
            "selection_file": str(selection_path),
            "test_metrics_used_for_selection": False,
            "selection_is_provisional": True,
            "promotion_status": "experimental_not_production_ready",
            "candidates": {},
        },
        "forecast_support": {
            "requested_months": forecast_months,
            "supported_direct_horizons": list(SUPPORTED_HORIZONS),
            "generated_leads_within_request": [
                row["horizon_months"] for row in support if row["forecast_generated"]
            ],
            "unsupported_leads": [
                row["horizon_months"] for row in support if not row["forecast_generated"]
            ],
            "interpolation_or_recursion_used": False,
            "probabilities_calibrated": False,
        },
        "per_horizon": {},
        "leakage_warnings": [
            "Source feature availability at forecast issuance is not timestamped and remains unverified.",
            "Candidate ranking is provisional: only one validation and one test period exist, and validation is also used for tree early stopping.",
            "Current models support direct 1-, 3-, and 6-month forecasts only; the remaining requested months are unsupported.",
            "Classifier phase probabilities are not calibrated.",
            "Phase classification and continuous ONI regression are separate outputs and can disagree.",
        ],
        "overall_status": "checks_passed_with_unresolved_limitations",
        "forecast_generation_status": "in_progress",
    }
    for horizon, (choice, metadata, validation_summary) in selected.items():
        audit["model_selection_provenance"]["candidates"][str(horizon)] = {
            "model": choice["model"],
            "imbalance_strategy": choice["imbalance_strategy"],
            "selection_validation_fold": choice["selection_validation_fold"],
            "selection_status": choice["selection_status"],
            "selection_uses_test_metrics": choice["selection_uses_test_metrics"],
            "validation_summary": validation_summary,
            "lstm_refit_epochs": metadata["hyperparameters"]["lstm"]["refit_epochs"],
        }
    _write_json(audit_path, audit)

    forecasts: list[dict[str, Any]] = []
    trained: dict[int, dict[str, Any]] = {}
    for horizon in SUPPORTED_HORIZONS:
        if horizon > forecast_months:
            continue
        choice, metadata, validation_summary = selected[horizon]
        row, training_details = _train_horizon(
            frame,
            feature_columns,
            horizon,
            choice,
            metadata,
            validation_summary,
            model_version,
            forecast_origin,
            artifact_dir,
            selection_path,
            seed=42,
        )
        forecasts.append(row)
        trained[horizon] = training_details
        audit["per_horizon"][str(horizon)] = training_details["audit"]
        _write_json(audit_path, audit)

    if not forecasts:
        raise ValueError(
            "No supported direct horizon falls within the requested forecast period"
        )
    forecast_frame = pd.DataFrame(forecasts).sort_values("horizon_months")
    report_output_dir.mkdir(parents=True, exist_ok=True)
    forecast_frame.to_csv(report_output_dir / "forecast.csv", index=False)
    unsupported = [
        row for row in support if not row["forecast_generated"]
    ]
    forecast_payload = {
        "forecast_origin": forecast_origin.date().isoformat(),
        "forecast_months_requested": forecast_months,
        "model_version": model_version,
        "probabilities_calibrated": False,
        "forecast_rows": forecasts,
        "unsupported_months": unsupported,
        "promotion_status": "experimental_not_production_ready",
    }
    _write_json(report_output_dir / "forecast.json", forecast_payload)
    _write_json(report_output_dir / "forecast_support.json", {
        "forecast_origin": forecast_origin.date().isoformat(),
        "forecast_months_requested": forecast_months,
        "supported_horizons": list(SUPPORTED_HORIZONS),
        "months": support,
    })

    plots = _plot_forecasts(frame, forecast_frame, report_dir)
    _write_final_report(
        report_dir / "final_retraining_report.md",
        forecast_origin,
        forecast_months,
        forecasts,
        support,
        plots,
    )
    _write_json(
        artifact_dir / "model_manifest.json",
        {
            "model_version": model_version,
            "artifact_kind": "final_forecasting_models",
            "promotion_status": "experimental_not_production_ready",
            "forecast_origin": forecast_origin.date().isoformat(),
            "forecast_horizons": list(trained),
            "feature_columns": feature_columns,
            "model_directories": {
                str(horizon): f"horizon_{horizon}m" for horizon in trained
            },
        },
    )
    audit["overall_status"] = "not_fully_verified"
    audit["forecast_generation_status"] = (
        "partial_support; only direct model leads were forecast"
        if unsupported
        else "completed_for_all_requested_leads"
    )
    audit["visualizations"] = plots
    audit["forecast_output"] = {
        "csv": str((report_output_dir / "forecast.csv").relative_to(PROJECT_ROOT)),
        "json": str((report_output_dir / "forecast.json").relative_to(PROJECT_ROOT)),
        "support": str((report_output_dir / "forecast_support.json").relative_to(PROJECT_ROOT)),
    }
    _write_json(audit_path, audit)
    return {
        "model_version": model_version,
        "forecast_origin": forecast_origin.date().isoformat(),
        "forecast_rows": forecasts,
        "unsupported_month_count": len(unsupported),
        "audit_status": audit["overall_status"],
        "audit_path": str(audit_path),
        "artifact_dir": str(artifact_dir),
    }
