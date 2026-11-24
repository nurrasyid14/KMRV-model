"""Expanding-window backtesting for the Causal LSTM + GBDT ENSO models."""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import torch
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight, compute_sample_weight

from src.ml.ensemble import calculate_hindcast_skill_weights, predict_lstm, train_lstm
from src.ml.evaluation import (
    classification_evaluation,
    probability_evaluation,
    regression_evaluation,
)
from src.ml.lgbm_classifier import create_phase_classifier as create_lgbm_classifier
from src.ml.temporal import (
    BACKTEST_MIN_TRAIN_MONTHS,
    BACKTEST_STEP_MONTHS,
    BACKTEST_TEST_MONTHS,
    BACKTEST_VALIDATION_MONTHS,
    PHASE_CLASSES,
    PHASE_NAMES,
    BacktestFold,
    audit_tables,
    build_expanding_folds,
    fold_feasibility_sweep,
    fold_indices,
    load_feature_data,
    resolve_feature_columns,
    distribution_rows as make_distribution_rows,
    validation_window_sweep,
    windows_for_origins,
)
from src.ml.xgb_classifier import create_phase_classifier as create_xgb_classifier

INNER_VALIDATION_MONTHS = 12
OOF_BLOCK_MONTHS = 6
MIN_INNER_TRAIN_WINDOWS = 12
TREE_ITERATIONS = 300
TREE_EARLY_STOPPING_ROUNDS = 50


@dataclass(frozen=True)
class LSTMConfig:
    window: int = 12
    hidden_size: int = 32
    epochs: int = 300
    batch_size: int = 16
    learning_rate: float = 0.003


@dataclass
class FoldLSTM:
    model: torch.nn.Module
    feature_scaler: StandardScaler
    target_scaler: StandardScaler
    selected_epochs: int | None = None
    early_stopping_period: dict[str, str] | None = None


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _fit_lstm(
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    train_origins: np.ndarray,
    validation_origins: np.ndarray,
    config: LSTMConfig,
    seed: int,
) -> tuple[FoldLSTM, np.ndarray, np.ndarray]:
    if len(train_origins) == 0 or len(validation_origins) == 0:
        raise ValueError("LSTM training requires non-empty train and validation periods")

    feature_scaler = StandardScaler()
    feature_scaler.fit(frame.iloc[:int(train_origins[-1]) + 1][feature_columns])
    scaled_features = feature_scaler.transform(frame[feature_columns]).astype(np.float32)

    target_values = frame[target_column].to_numpy(dtype=np.float64)
    target_scaler = StandardScaler()
    target_scaler.fit(target_values[train_origins].reshape(-1, 1))
    scaled_targets = target_scaler.transform(
        target_values.reshape(-1, 1)
    ).reshape(-1).astype(np.float32)

    train_windows = (
        windows_for_origins(scaled_features, train_origins, config.window),
        scaled_targets[train_origins],
    )
    validation_windows = (
        windows_for_origins(scaled_features, validation_origins, config.window),
        scaled_targets[validation_origins],
    )
    model = train_lstm(
        train_windows,
        validation_windows,
        len(feature_columns),
        config.hidden_size,
        config.epochs,
        config.batch_size,
        config.learning_rate,
        seed,
    )
    fold_model = FoldLSTM(
        model=model,
        feature_scaler=feature_scaler,
        target_scaler=target_scaler,
    )
    validation_predictions = _predict_oni(
        fold_model, frame, feature_columns, validation_origins, config.window
    )
    return fold_model, validation_predictions, scaled_features


def _fit_outer_lstm(
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    train_origins: np.ndarray,
    fold: BacktestFold,
    horizon: int,
    config: LSTMConfig,
    seed: int,
) -> tuple[FoldLSTM, np.ndarray]:
    inner_validation_start = fold.train_end - INNER_VALIDATION_MONTHS
    inner_train_origins = np.arange(
        config.window - 1,
        inner_validation_start - horizon,
        dtype=np.int64,
    )
    inner_validation_origins = np.arange(
        inner_validation_start,
        fold.train_end - horizon,
        dtype=np.int64,
    )
    if len(inner_train_origins) < MIN_INNER_TRAIN_WINDOWS:
        raise ValueError(
            f"Fold {fold.fold_id}, horizon {horizon}: insufficient historical "
            "training rows for a train-only early-stopping period"
        )
    if len(inner_validation_origins) == 0:
        raise ValueError(
            f"Fold {fold.fold_id}, horizon {horizon}: empty train-only "
            "early-stopping period"
        )

    epoch_selection_model, _, _ = _fit_lstm(
        frame,
        feature_columns,
        target_column,
        inner_train_origins,
        inner_validation_origins,
        config,
        seed,
    )
    validation_history = epoch_selection_model.model.loss_history
    best_epoch = int(
        min(
            validation_history,
            key=lambda row: row["validation_mse"],
        )["epoch"]
    )

    feature_scaler = StandardScaler()
    feature_scaler.fit(
        frame.iloc[: int(train_origins[-1]) + 1][feature_columns]
    )
    scaled_features = feature_scaler.transform(frame[feature_columns]).astype(np.float32)
    target_values = frame[target_column].to_numpy(dtype=np.float64)
    target_scaler = StandardScaler()
    target_scaler.fit(target_values[train_origins].reshape(-1, 1))
    scaled_targets = target_scaler.transform(
        target_values.reshape(-1, 1)
    ).reshape(-1).astype(np.float32)
    train_windows = (
        windows_for_origins(scaled_features, train_origins, config.window),
        scaled_targets[train_origins],
    )
    model = train_lstm(
        train_windows,
        None,
        len(feature_columns),
        config.hidden_size,
        best_epoch,
        config.batch_size,
        config.learning_rate,
        seed + 1,
    )
    fold_model = FoldLSTM(
        model=model,
        feature_scaler=feature_scaler,
        target_scaler=target_scaler,
        selected_epochs=best_epoch,
        early_stopping_period={
            "start": frame["time"].iloc[inner_validation_origins[0]].date().isoformat(),
            "end": frame["time"].iloc[inner_validation_origins[-1]].date().isoformat(),
        },
    )
    validation_origins = np.arange(
        fold.validation_start,
        fold.validation_end - horizon,
        dtype=np.int64,
    )
    predictions = _predict_oni(
        fold_model,
        frame,
        feature_columns,
        validation_origins,
        config.window,
    )
    return fold_model, predictions


def _predict_oni(
    fold_model: FoldLSTM,
    frame: pd.DataFrame,
    feature_columns: list[str],
    origins: np.ndarray,
    window: int,
) -> np.ndarray:
    scaled_features = fold_model.feature_scaler.transform(
        frame[feature_columns]
    ).astype(np.float32)
    windows = windows_for_origins(scaled_features, origins, window)
    scaled_predictions = predict_lstm(fold_model.model, windows)
    return fold_model.target_scaler.inverse_transform(
        scaled_predictions.reshape(-1, 1)
    ).reshape(-1)


def _oof_lstm_forecasts(
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    fold: BacktestFold,
    horizon: int,
    config: LSTMConfig,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    train_stop = fold.train_end - horizon
    first_block = math.ceil(
        (
            INNER_VALIDATION_MONTHS
            + horizon
            + config.window
            + MIN_INNER_TRAIN_WINDOWS
            - 1
        )
        / OOF_BLOCK_MONTHS
    ) * OOF_BLOCK_MONTHS
    forecast_origins: list[int] = []
    forecast_values: list[float] = []

    for block_start in range(first_block, train_stop, OOF_BLOCK_MONTHS):
        block_end = min(block_start + OOF_BLOCK_MONTHS, train_stop)
        inner_validation_start = block_start - INNER_VALIDATION_MONTHS
        inner_train_origins = np.arange(
            config.window - 1,
            inner_validation_start - horizon,
            dtype=np.int64,
        )
        inner_validation_origins = np.arange(
            inner_validation_start,
            block_start - horizon,
            dtype=np.int64,
        )
        block_origins = np.arange(block_start, block_end, dtype=np.int64)
        if len(inner_train_origins) < MIN_INNER_TRAIN_WINDOWS:
            continue
        if len(inner_validation_origins) == 0 or len(block_origins) == 0:
            continue

        model, _, _ = _fit_lstm(
            frame,
            feature_columns,
            target_column,
            inner_train_origins,
            inner_validation_origins,
            config,
            seed + horizon * 10000 + fold.fold_id * 1000 + block_start,
        )
        forecast_origins.extend(block_origins.tolist())
        forecast_values.extend(
            _predict_oni(
                model,
                frame,
                feature_columns,
                block_origins,
                config.window,
            ).tolist()
        )

    origins = np.asarray(forecast_origins, dtype=np.int64)
    forecasts = np.asarray(forecast_values, dtype=np.float64)
    if len(origins) == 0:
        raise ValueError(
            f"Fold {fold.fold_id}, horizon {horizon}: not enough history for "
            "leakage-free LSTM out-of-fold forecasts"
        )
    actual_labels = frame.iloc[origins][f"target_phase_lead_{horizon}m"].to_numpy(dtype=int)
    missing = sorted(set(PHASE_CLASSES.tolist()) - set(actual_labels.tolist()))
    if missing:
        raise ValueError(
            f"Fold {fold.fold_id}, horizon {horizon}: OOF classifier training "
            f"does not contain all phase classes; missing {missing}"
        )
    return origins, forecasts


def _classifier_features(
    frame: pd.DataFrame,
    feature_columns: list[str],
    origins: np.ndarray,
    oni_forecasts: np.ndarray,
) -> pd.DataFrame:
    features = frame.iloc[origins][feature_columns].copy().reset_index(drop=True)
    features["lstm_oni_forecast"] = oni_forecasts
    if not np.isfinite(features.to_numpy(dtype=np.float64)).all():
        raise ValueError("Classifier features contain non-finite values")
    return features


def _balanced_class_weights(labels: np.ndarray) -> dict[int, float]:
    classes = np.unique(labels)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=labels)
    return {int(class_id): float(weight) for class_id, weight in zip(classes, weights)}


def _fit_classifier(
    model_family: str,
    imbalance_strategy: str,
    train_features: pd.DataFrame,
    train_labels: np.ndarray,
    validation_features: pd.DataFrame,
    validation_labels: np.ndarray,
    seed: int,
) -> tuple[Any, int, dict[int, float]]:
    class_weights = (
        _balanced_class_weights(train_labels)
        if imbalance_strategy == "balanced"
        else {}
    )
    if model_family == "LightGBM":
        model = create_lgbm_classifier(
            random_state=seed,
            iterations=TREE_ITERATIONS,
            class_weight=class_weights or None,
        )
        model.fit(
            train_features,
            train_labels,
            eval_set=[(validation_features, validation_labels)],
            callbacks=[
                lgb.early_stopping(TREE_EARLY_STOPPING_ROUNDS, verbose=False),
                lgb.log_evaluation(0),
            ],
        )
        best_iteration = int(model.best_iteration_ or TREE_ITERATIONS)
    elif model_family == "XGBoost":
        model = create_xgb_classifier(
            random_state=seed,
            iterations=TREE_ITERATIONS,
            early_stopping_rounds=TREE_EARLY_STOPPING_ROUNDS,
        )
        sample_weights = (
            compute_sample_weight(class_weight="balanced", y=train_labels)
            if imbalance_strategy == "balanced"
            else None
        )
        model.fit(
            train_features,
            train_labels,
            sample_weight=sample_weights,
            eval_set=[(validation_features, validation_labels)],
            verbose=False,
        )
        best_iteration = int(model.best_iteration + 1)
    else:
        raise ValueError(f"Unsupported classifier family: {model_family}")
    return model, best_iteration, class_weights


def _expanded_metric_row(
    context: dict[str, object],
    metrics: dict[str, object],
) -> dict[str, object]:
    row = {**context, **metrics}
    actual_counts = row.pop("actual_class_counts")
    predicted_counts = row.pop("predicted_class_counts")
    for class_id in PHASE_CLASSES:
        row[f"actual_count_{class_id}"] = actual_counts[str(int(class_id))]
        row[f"predicted_count_{class_id}"] = predicted_counts[str(int(class_id))]
    row["missing_actual_classes"] = json.dumps(row["missing_actual_classes"])
    row["missing_predicted_classes"] = json.dumps(row["missing_predicted_classes"])
    return row


def _fit_xgboost_regressor(
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    train_origins: np.ndarray,
    validation_origins: np.ndarray,
    seed: int,
) -> tuple[xgb.XGBRegressor, np.ndarray]:
    train_x = frame.iloc[train_origins][feature_columns]
    train_y = frame.iloc[train_origins][target_column].to_numpy(dtype=np.float64)
    val_x = frame.iloc[validation_origins][feature_columns]
    val_y = frame.iloc[validation_origins][target_column].to_numpy(dtype=np.float64)

    model = xgb.XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=seed,
        n_jobs=-1,
        early_stopping_rounds=30,
    )
    model.fit(
        train_x,
        train_y,
        eval_set=[(val_x, val_y)],
        verbose=False,
    )
    val_preds = model.predict(val_x)
    return model, val_preds


def _fit_period(
    frame: pd.DataFrame,
    feature_columns: list[str],
    horizon: int,
    fold: BacktestFold,
    indices: dict[str, np.ndarray],
    config: LSTMConfig,
    seed: int,
) -> tuple[FoldLSTM, dict[str, np.ndarray], dict[str, np.ndarray], np.ndarray]:
    target_column = f"target_oni_lead_{horizon}m"
    train_origins = indices["train"]
    validation_origins = indices["validation"]
    test_origins = indices["test"]

    oof_origins, oof_forecasts = _oof_lstm_forecasts(
        frame,
        feature_columns,
        target_column,
        fold,
        horizon,
        config,
        seed,
    )
    model, validation_forecasts = _fit_outer_lstm(
        frame,
        feature_columns,
        target_column,
        train_origins,
        fold,
        horizon,
        config,
        seed + horizon * 10000 + fold.fold_id * 1000,
    )
    test_forecasts = _predict_oni(
        model, frame, feature_columns, test_origins, config.window
    )

    # Train XGBoost tabular regressor as benchmark comparison model
    xgb_reg, val_xgb_forecasts = _fit_xgboost_regressor(
        frame,
        feature_columns,
        target_column,
        train_origins,
        validation_origins,
        seed + horizon * 10000 + fold.fold_id * 1000,
    )
    val_actual = frame.iloc[validation_origins][target_column].to_numpy(dtype=np.float64)
    weights = calculate_hindcast_skill_weights(
        val_actual,
        {"lstm": validation_forecasts, "xgboost": val_xgb_forecasts},
    )
    w_l = weights["lstm"]
    w_x = weights["xgboost"]

    train_xgb_forecasts = xgb_reg.predict(frame.iloc[oof_origins][feature_columns])
    test_xgb_forecasts = xgb_reg.predict(frame.iloc[test_origins][feature_columns])

    oof_ensemble = w_l * oof_forecasts + w_x * train_xgb_forecasts
    val_ensemble = w_l * validation_forecasts + w_x * val_xgb_forecasts
    test_ensemble = w_l * test_forecasts + w_x * test_xgb_forecasts

    forecast_map = {
        "train": oof_ensemble,
        "validation": val_ensemble,
        "test": test_ensemble,
        "lstm_validation": validation_forecasts,
        "xgb_validation": val_xgb_forecasts,
        "lstm_test": test_forecasts,
        "xgb_test": test_xgb_forecasts,
        "ensemble_weights": weights,
    }
    origin_map = {
        "train": oof_origins,
        "validation": validation_origins,
        "test": test_origins,
    }
    return model, origin_map, forecast_map, oof_origins


def _jsonable_params(model: Any) -> dict[str, object]:
    def convert(value: Any) -> object:
        if isinstance(value, dict):
            return {str(key): convert(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [convert(item) for item in value]
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        return str(value)

    return {str(key): convert(value) for key, value in model.get_params().items()}


def _save_selected_model(
    model_dir: Path,
    horizon: int,
    selected_family: str,
    selected_strategy: str,
    selected_candidate: dict[str, Any],
    feature_columns: list[str],
    config: LSTMConfig,
) -> Path:
    fold: BacktestFold = selected_candidate["fold"]
    frame: pd.DataFrame = selected_candidate["frame"]
    indices: dict[str, np.ndarray] = selected_candidate["indices"]
    lstm_model: FoldLSTM = selected_candidate["lstm"]
    classifier = selected_candidate["classifier"]
    directory = (
        model_dir
        / f"horizon_{horizon}m"
        / f"{selected_family.lower()}_{selected_strategy}"
    )
    directory.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "state_dict": lstm_model.model.state_dict(),
        "feature_columns": feature_columns,
        "hidden_size": lstm_model.model.lstm.hidden_size,
        "window": config.window,
        "horizon_months": horizon,
        "fold": fold.fold_id,
        "loss_history": getattr(lstm_model.model, "loss_history", []),
    }
    torch.save(checkpoint, directory / "lstm_checkpoint.pt")
    joblib.dump(lstm_model.feature_scaler, directory / "feature_scaler.joblib")
    joblib.dump(lstm_model.target_scaler, directory / "target_scaler.joblib")

    if selected_family == "LightGBM":
        classifier.booster_.save_model(str(directory / "classifier.txt"))
    else:
        classifier.save_model(str(directory / "classifier.json"))

    training_origins = indices["train"]
    validation_origins = indices["validation"]
    metadata = {
        "model_architecture": f"CausalLSTM + {selected_family}",
        "classifier": selected_family,
        "imbalance_strategy": selected_strategy,
        "forecast_horizon_months": horizon,
        "training_period": {
            "start": frame["time"].iloc[training_origins[0]].date().isoformat(),
            "end": frame["time"].iloc[training_origins[-1]].date().isoformat(),
        },
        "validation_period": {
            "start": frame["time"].iloc[validation_origins[0]].date().isoformat(),
            "end": frame["time"].iloc[validation_origins[-1]].date().isoformat(),
        },
        "test_period": {
            "start": frame["time"].iloc[fold.test_start].date().isoformat(),
            "end": frame["time"].iloc[fold.test_end - 1].date().isoformat(),
        },
        "classifier_training_period": {
            "start": frame["time"].iloc[
                selected_candidate["classifier_train_origins"][0]
            ].date().isoformat(),
            "end": frame["time"].iloc[
                selected_candidate["classifier_train_origins"][-1]
            ].date().isoformat(),
            "samples": len(selected_candidate["classifier_train_origins"]),
        },
        "feature_configuration": {
            "window_months": config.window,
            "feature_columns": feature_columns,
            "classifier_extra_feature": "lstm_oni_forecast",
            "training_forecasts": "causal expanding-window out-of-fold",
        },
        "hyperparameters": {
            "lstm": {
                **asdict(config),
                "dropout": 0.1,
                "refit_epochs": lstm_model.selected_epochs,
                "epoch_selection_period": lstm_model.early_stopping_period,
            },
            "classifier": _jsonable_params(classifier),
            "class_weights_from_classifier_training_only": selected_candidate["class_weights"],
        },
        "validation_metrics": selected_candidate["validation_metrics"],
        "selected_using": "validation metrics only; test metrics were not used for selection",
        "selection_validation_fold": fold.fold_id,
        "selection_is_provisional": True,
        "training_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    (directory / "metadata.json").write_text(
        json.dumps(metadata, indent=2, default=str),
        encoding="utf-8",
    )
    return directory


def run_backtesting(
    data_path: Path,
    horizons: tuple[int, ...] = (1, 3, 6, 9, 12),
    epochs: int = 300,
    seed: int = 42,
    reports_dir: Path | None = None,
    model_dir: Path | None = None,
) -> dict[str, object]:
    from src.ml.reporting import write_backtest_reports

    data_path = data_path.resolve()
    frame = load_feature_data(data_path)
    feature_columns = resolve_feature_columns(frame)
    config = LSTMConfig(epochs=epochs)
    folds = build_expanding_folds(
        len(frame),
        min_train_months=BACKTEST_MIN_TRAIN_MONTHS,
        validation_months=BACKTEST_VALIDATION_MONTHS,
        test_months=BACKTEST_TEST_MONTHS,
        step_months=BACKTEST_STEP_MONTHS,
    )
    validation_sweep = validation_window_sweep(frame, horizons)
    fold_sweep = fold_feasibility_sweep(
        frame,
        horizons=horizons,
        window=config.window,
    )
    reports_dir = reports_dir or data_path.parents[1] / "reports"
    model_dir = model_dir or data_path.parents[1] / "model" / "backtesting_selected"
    summary, class_distribution, split_distribution = audit_tables(
        frame,
        data_path.parent,
        folds,
        horizons,
        config.window,
    )

    metric_rows: list[dict[str, object]] = []
    report_rows: list[dict[str, object]] = []
    prediction_rows: list[dict[str, object]] = []
    regression_metric_rows: list[dict[str, object]] = []
    regression_prediction_rows: list[dict[str, object]] = []
    confusion_matrices: dict[tuple[str, str, int, int, str], np.ndarray] = {}
    candidates: dict[tuple[int, str, str, int], dict[str, Any]] = {}
    oof_distribution_rows: list[dict[str, object]] = []

    for horizon in horizons:
        oni_target = f"target_oni_lead_{horizon}m"
        phase_target = f"target_phase_lead_{horizon}m"
        for fold in folds:
            indices = fold_indices(fold, horizon, config.window)
            lstm_model, origin_map, forecast_map, oof_origins = _fit_period(
                frame,
                feature_columns,
                horizon,
                fold,
                indices,
                config,
                seed,
            )
            train_labels = frame.iloc[oof_origins][phase_target].to_numpy(dtype=np.int64)
            oof_frame = frame.iloc[oof_origins]
            oof_distribution_rows.extend(
                {
                    "fold": fold.fold_id,
                    "split": "classifier_train_oof",
                    "horizon_months": horizon,
                    "start_time": oof_frame["time"].iloc[0],
                    "end_time": oof_frame["time"].iloc[-1],
                    "sample_count": len(oof_frame),
                    "post_window_sample_count": len(oof_frame),
                    "class_id": row["class_id"],
                    "class_name": row["class_name"],
                    "class_count": row["class_count"],
                    "proportion": row["proportion"],
                    "class_missing": row["class_missing"],
                    "purged_target_rows": 0,
                }
                for row in make_distribution_rows(
                    oof_frame, horizon, f"fold_{fold.fold_id}", "classifier_train_oof"
                )
            )
            feature_frames = {
                split: _classifier_features(
                    frame,
                    feature_columns,
                    origin_map[split],
                    forecast_map[split],
                )
                for split in ("train", "validation", "test")
            }
            labels_by_split = {
                split: frame.iloc[origin_map[split]][phase_target].to_numpy(dtype=np.int64)
                for split in ("validation",)
            }
            validation_origins = origin_map["validation"]
            validation_actual_oni = frame.iloc[validation_origins][
                oni_target
            ].to_numpy(dtype=np.float64)
            validation_predicted_oni = forecast_map["validation"]
            validation_times = frame.iloc[validation_origins]["time"]
            validation_target_times = validation_times + pd.DateOffset(
                months=horizon
            )
            validation_regression = regression_evaluation(
                validation_actual_oni,
                validation_predicted_oni,
            )
            regression_metric_rows.append(
                {
                    "fold": fold.fold_id,
                    "horizon_months": horizon,
                    "split": "validation",
                    "start_time": validation_times.iloc[0],
                    "end_time": validation_times.iloc[-1],
                    "sample_count": len(validation_origins),
                    **validation_regression,
                    "actual_oni_mean": float(np.mean(validation_actual_oni)),
                    "actual_oni_std": float(np.std(validation_actual_oni)),
                    "predicted_oni_mean": float(
                        np.mean(validation_predicted_oni)
                    ),
                    "predicted_oni_std": float(
                        np.std(validation_predicted_oni)
                    ),
                    "mean_residual_actual_minus_predicted": float(
                        np.mean(validation_actual_oni - validation_predicted_oni)
                    ),
                }
            )
            regression_prediction_rows.extend(
                {
                    "fold": fold.fold_id,
                    "horizon_months": horizon,
                    "split": "validation",
                    "origin_time": frame["time"].iloc[int(origin)],
                    "target_time": target_time,
                    "actual_oni": float(actual),
                    "predicted_oni": float(predicted),
                    "residual_actual_minus_predicted": float(actual - predicted),
                }
                for origin, target_time, actual, predicted in zip(
                    validation_origins,
                    validation_target_times,
                    validation_actual_oni,
                    validation_predicted_oni,
                )
            )

            for model_family in ("LightGBM", "XGBoost"):
                for strategy in ("unweighted", "balanced"):
                    classifier, best_iteration, class_weights = _fit_classifier(
                        model_family,
                        strategy,
                        feature_frames["train"],
                        train_labels,
                        feature_frames["validation"],
                        labels_by_split["validation"],
                        seed + horizon * 10000 + fold.fold_id * 100 + int(strategy == "balanced"),
                    )
                    candidate_key = (horizon, model_family, strategy, fold.fold_id)
                    candidate_metrics: dict[str, dict[str, object]] = {}
                    for split in ("validation",):
                        origins = origin_map[split]
                        actual = labels_by_split[split]
                        probabilities = classifier.predict_proba(
                            feature_frames[split]
                        )
                        predicted = classifier.predict(feature_frames[split]).astype(np.int64)
                        class_metrics, class_report, confusion = classification_evaluation(
                            actual,
                            predicted,
                        )
                        class_metrics.update(
                            probability_evaluation(actual, probabilities)
                        )
                        period = frame.iloc[origins]["time"]
                        context = {
                            "fold": fold.fold_id,
                            "model": model_family,
                            "imbalance_strategy": strategy,
                            "horizon_months": horizon,
                            "split": split,
                            "start_time": period.iloc[0],
                            "end_time": period.iloc[-1],
                            "sample_count": len(actual),
                            "best_iteration": best_iteration,
                            **validation_regression,
                        }
                        metric_rows.append(_expanded_metric_row(context, class_metrics))
                        candidate_metrics[split] = {
                            **class_metrics,
                            **validation_regression,
                        }
                        for row in class_report:
                            report_rows.append(
                                {
                                    **context,
                                    **row,
                                }
                            )
                        confusion_matrices[
                            (model_family, strategy, horizon, fold.fold_id, split)
                        ] = confusion
                    candidates[candidate_key] = {
                        "fold": fold,
                        "frame": frame,
                        "indices": indices,
                        "origins": origin_map,
                        "forecasts": forecast_map,
                        "features": feature_frames,
                        "labels": labels_by_split,
                        "lstm": lstm_model,
                        "classifier": classifier,
                        "validation_metrics": candidate_metrics["validation"],
                        "best_iteration": best_iteration,
                        "class_weights": class_weights,
                        "classifier_train_origins": oof_origins,
                    }

    validation_metrics = pd.DataFrame(metric_rows)
    selection, model_comparison, horizon_comparison = _select_models(
        validation_metrics
    )
    selected_paths: dict[str, str] = {}
    test_metric_rows: list[dict[str, object]] = []
    test_report_rows: list[dict[str, object]] = []
    test_regression_metric_rows: list[dict[str, object]] = []
    test_regression_prediction_rows: list[dict[str, object]] = []
    test_fold = folds[-1]

    for horizon in horizons:
        choice = selection["selected_models"][str(horizon)]
        family = choice["model"]
        strategy = choice["imbalance_strategy"]
        test_class_metrics: dict[str, object] | None = None
        test_probabilities: np.ndarray | None = None
        if family is not None:
            selected_fold = int(choice["selection_validation_fold"])
            selected_key = (horizon, str(family), str(strategy), selected_fold)
            selected_candidate = candidates[selected_key]
            model_path = _save_selected_model(
                model_dir,
                horizon,
                str(family),
                str(strategy),
                selected_candidate,
                feature_columns,
                config,
            )
            choice["saved_model_directory"] = str(model_path)
            choice["saved_model_fold"] = selected_fold
            selected_paths[str(horizon)] = str(model_path)

            origins = selected_candidate["origins"]["test"]
            target_column = f"target_phase_lead_{horizon}m"
            actual = frame.iloc[origins][target_column].to_numpy(dtype=np.int64)
            oni_target = f"target_oni_lead_{horizon}m"
            actual_oni = frame.iloc[origins][oni_target].to_numpy(dtype=np.float64)
            predicted_oni = selected_candidate["forecasts"]["test"]
            test_regression_result = regression_evaluation(
                actual_oni,
                predicted_oni,
            )
            predicted = selected_candidate["classifier"].predict(
                selected_candidate["features"]["test"]
            ).astype(np.int64)
            test_probabilities = selected_candidate["classifier"].predict_proba(
                selected_candidate["features"]["test"]
            )
            test_class_metrics, test_class_report, test_confusion = (
                classification_evaluation(actual, predicted)
            )
            test_class_metrics.update(
                probability_evaluation(actual, test_probabilities)
            )
            test_times = frame.iloc[origins]["time"]
            test_context = {
                "fold": selected_fold,
                "model": family,
                "imbalance_strategy": strategy,
                "horizon_months": horizon,
                "split": "test",
                "start_time": test_times.iloc[0],
                "end_time": test_times.iloc[-1],
                "sample_count": len(actual),
                "best_iteration": selected_candidate["best_iteration"],
                "final_holdout_evaluation": True,
                **test_regression_result,
            }
            test_metric_rows.append(
                _expanded_metric_row(test_context, test_class_metrics)
            )
            for row in test_class_report:
                test_report_rows.append({**test_context, **row})
            confusion_matrices[
                (str(family), str(strategy), horizon, selected_fold, "test")
            ] = test_confusion
            if family is not None:
                assert test_probabilities is not None
                for origin, target_time, true_phase, predicted_phase, oni, oni_hat, phase_probabilities in zip(
                    origins,
                    frame.iloc[origins]["time"] + pd.DateOffset(months=horizon),
                    actual,
                    predicted,
                    actual_oni,
                    predicted_oni,
                    test_probabilities,
                    strict=True,
                ):
                    prediction_rows.append(
                        {
                            "fold": selected_fold,
                            "model": family,
                            "imbalance_strategy": strategy,
                            "horizon_months": horizon,
                            "origin_time": frame["time"].iloc[int(origin)],
                            "target_time": target_time,
                            "actual_phase": int(true_phase),
                            "predicted_phase": int(predicted_phase),
                            "phase_confidence": float(np.max(phase_probabilities)),
                            "probability_la_nina": float(phase_probabilities[0]),
                            "probability_neutral": float(phase_probabilities[1]),
                            "probability_el_nino": float(phase_probabilities[2]),
                            "probabilities_calibrated": False,
                            "actual_oni": float(oni),
                            "predicted_oni": float(oni_hat),
                        }
                    )

        regression_candidate = next(
            candidate
            for key, candidate in candidates.items()
            if key[0] == horizon and key[3] == test_fold.fold_id
        )
        test_origins = regression_candidate["origins"]["test"]
        test_actual_oni = frame.iloc[test_origins][
            f"target_oni_lead_{horizon}m"
        ].to_numpy(dtype=np.float64)
        test_predicted_oni = regression_candidate["forecasts"]["test"]
        test_times = frame.iloc[test_origins]["time"]
        regression_result = regression_evaluation(
            test_actual_oni,
            test_predicted_oni,
        )
        choice["final_holdout_evaluation"] = {
            "classification": test_class_metrics,
            "oni_regression": regression_result,
            "test_period": {
                "start": test_times.iloc[0].date().isoformat(),
                "end": test_times.iloc[-1].date().isoformat(),
            },
        }
        if family is not None:
            metadata_path = (
                Path(choice["saved_model_directory"]) / "metadata.json"
            )
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["final_holdout_evaluation"] = choice[
                "final_holdout_evaluation"
            ]
            metadata_path.write_text(
                json.dumps(metadata, indent=2, default=str),
                encoding="utf-8",
            )
        test_regression_metric_rows.append(
            {
                "fold": test_fold.fold_id,
                "horizon_months": horizon,
                "split": "test",
                "final_holdout_evaluation": True,
                "start_time": test_times.iloc[0],
                "end_time": test_times.iloc[-1],
                "sample_count": len(test_origins),
                **regression_result,
                "actual_oni_mean": float(np.mean(test_actual_oni)),
                "actual_oni_std": float(np.std(test_actual_oni)),
                "predicted_oni_mean": float(np.mean(test_predicted_oni)),
                "predicted_oni_std": float(np.std(test_predicted_oni)),
                "mean_residual_actual_minus_predicted": float(
                    np.mean(test_actual_oni - test_predicted_oni)
                ),
            }
        )
        test_regression_prediction_rows.extend(
            {
                "fold": test_fold.fold_id,
                "horizon_months": horizon,
                "split": "test",
                "final_holdout_evaluation": True,
                "origin_time": frame["time"].iloc[int(origin)],
                "target_time": target_time,
                "actual_oni": float(actual),
                "predicted_oni": float(predicted),
                "residual_actual_minus_predicted": float(actual - predicted),
            }
            for origin, target_time, actual, predicted in zip(
                test_origins,
                frame.iloc[test_origins]["time"] + pd.DateOffset(months=horizon),
                test_actual_oni,
                test_predicted_oni,
            )
        )

    fold_metrics = pd.concat(
        [validation_metrics, pd.DataFrame(test_metric_rows)],
        ignore_index=True,
    )
    test_aggregation = {
        metric: ["mean", "std"]
        for metric in (
            "accuracy",
            "balanced_accuracy",
            "macro_precision",
            "macro_recall",
            "macro_f1",
            "weighted_f1",
            "log_loss",
            "multiclass_brier_score",
            "top_label_ece_10_bins",
            "mean_top_label_confidence",
            "oni_rmse",
        )
    }
    test_comparison = (
        fold_metrics.loc[fold_metrics["split"] == "test"]
        .groupby(["horizon_months", "model", "imbalance_strategy"])
        .agg(test_aggregation)
    )
    test_comparison.columns = [
        f"test_{metric}_{stat}" for metric, stat in test_comparison.columns
    ]
    test_comparison = test_comparison.reset_index()
    model_comparison = model_comparison.drop(
        columns=[
            column
            for column in model_comparison.columns
            if column.startswith("test_")
        ],
        errors="ignore",
    ).merge(
        test_comparison,
        on=["horizon_months", "model", "imbalance_strategy"],
        how="left",
    )
    horizon_comparison = model_comparison.sort_values(
        ["horizon_months", "model", "imbalance_strategy"]
    ).reset_index(drop=True)
    classification_reports = pd.DataFrame(report_rows + test_report_rows)
    test_predictions = pd.DataFrame(prediction_rows)
    regression_metrics = pd.concat(
        [
            pd.DataFrame(regression_metric_rows),
            pd.DataFrame(test_regression_metric_rows),
        ],
        ignore_index=True,
    )
    regression_predictions = pd.concat(
        [
            pd.DataFrame(regression_prediction_rows),
            pd.DataFrame(test_regression_prediction_rows),
        ],
        ignore_index=True,
    )
    split_distribution = pd.concat(
        [split_distribution, pd.DataFrame(oof_distribution_rows)],
        ignore_index=True,
    )
    selection["test_metrics_used_for_selection"] = False
    selection["selected_model_paths"] = selected_paths

    report = write_backtest_reports(
        reports_dir=reports_dir,
        model_dir=model_dir,
        frame=frame,
        summary=summary,
        folds=folds,
        class_distribution=class_distribution,
        split_distribution=split_distribution,
        fold_metrics=fold_metrics,
        classification_reports=classification_reports,
        confusion_matrices=confusion_matrices,
        test_predictions=test_predictions,
        regression_metrics=regression_metrics,
        regression_predictions=regression_predictions,
        model_comparison=model_comparison,
        horizon_comparison=horizon_comparison,
        selection=selection,
        validation_sweep=validation_sweep,
        fold_sweep=fold_sweep,
        horizons=horizons,
        window=config.window,
        epochs=epochs,
    )
    return report


def _select_models(
    fold_metrics: pd.DataFrame,
) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    validation = fold_metrics.loc[fold_metrics["split"] == "validation"].copy()
    grouping = ["horizon_months", "model", "imbalance_strategy"]
    aggregations = {
        metric: ["mean", "std"]
        for metric in (
            "accuracy",
            "balanced_accuracy",
            "macro_precision",
            "macro_recall",
            "macro_f1",
            "weighted_f1",
            "log_loss",
            "multiclass_brier_score",
            "top_label_ece_10_bins",
            "mean_top_label_confidence",
            "oni_rmse",
        )
    }
    comparison = validation.groupby(grouping).agg(aggregations)
    comparison.columns = [f"validation_{metric}_{stat}" for metric, stat in comparison.columns]
    comparison = comparison.reset_index()
    class_coverage = (
        validation.groupby(grouping)[["actual_count_0", "actual_count_1", "actual_count_2"]]
        .sum()
        .gt(0)
        .sum(axis=1)
        .rename("validation_actual_class_coverage")
        .reset_index()
    )
    comparison = comparison.merge(class_coverage, on=grouping, how="left")

    test = fold_metrics.loc[fold_metrics["split"] == "test"].copy()
    test_comparison = test.groupby(grouping).agg(aggregations)
    test_comparison.columns = [f"test_{metric}_{stat}" for metric, stat in test_comparison.columns]
    test_comparison = test_comparison.reset_index()
    model_comparison = comparison.merge(test_comparison, on=grouping, how="left")
    horizon_comparison = model_comparison.sort_values(grouping).reset_index(drop=True)

    selection_fold = int(validation["fold"].min())
    selection_validation = validation.loc[validation["fold"] == selection_fold]
    selection_validation = selection_validation.copy()
    selection_validation["actual_class_coverage"] = selection_validation[
        [f"actual_count_{class_id}" for class_id in PHASE_CLASSES]
    ].gt(0).sum(axis=1)
    selected_models: dict[str, object] = {}
    for horizon in sorted(validation["horizon_months"].unique()):
        candidates = selection_validation.loc[
            selection_validation["horizon_months"] == horizon
        ].copy()
        candidates["actual_class_coverage"] = candidates[
            [f"actual_count_{class_id}" for class_id in PHASE_CLASSES]
        ].gt(0).sum(axis=1)
        eligible = candidates.loc[candidates["actual_class_coverage"] == len(PHASE_CLASSES)]
        if eligible.empty:
            representative = candidates.iloc[0]
            selected_models[str(int(horizon))] = {
                "model": None,
                "imbalance_strategy": None,
                "selection_validation_fold": selection_fold,
                "selection_status": "insufficient_class_coverage",
                "validation_macro_f1": None,
                "validation_balanced_accuracy": None,
                "validation_macro_precision": None,
                "validation_macro_recall": None,
                "validation_log_loss": None,
                "validation_multiclass_brier_score": None,
                "validation_top_label_ece_10_bins": None,
                "validation_actual_class_coverage": int(
                    representative["actual_class_coverage"]
                ),
                "validation_missing_actual_classes": json.loads(
                    representative["missing_actual_classes"]
                ),
                "selection_uses_test_metrics": False,
                "selection_is_provisional": True,
            }
            continue
        candidates = eligible.sort_values(
            [
                "log_loss",
                "multiclass_brier_score",
                "macro_f1",
                "balanced_accuracy",
                "macro_precision",
                "macro_recall",
                "oni_rmse",
            ],
            ascending=[True, True, False, False, False, False, True],
        )
        best = candidates.iloc[0]
        selected_models[str(int(horizon))] = {
            "model": best["model"],
            "imbalance_strategy": best["imbalance_strategy"],
            "selection_validation_fold": selection_fold,
            "selection_status": "provisional_candidate",
            "validation_macro_f1": float(best["macro_f1"]),
            "validation_balanced_accuracy": float(best["balanced_accuracy"]),
            "validation_macro_precision": float(best["macro_precision"]),
            "validation_macro_recall": float(best["macro_recall"]),
            "validation_log_loss": float(best["log_loss"]),
            "validation_multiclass_brier_score": float(
                best["multiclass_brier_score"]
            ),
            "validation_top_label_ece_10_bins": float(
                best["top_label_ece_10_bins"]
            ),
            "validation_actual_class_coverage": int(
                best["actual_class_coverage"]
            ),
            "validation_missing_actual_classes": json.loads(
                best["missing_actual_classes"]
            ),
            "validation_oni_rmse": float(best["oni_rmse"]),
            "selection_uses_test_metrics": False,
            "selection_is_provisional": True,
        }
    selection = {
        "selection_policy": [
            f"Use only the first pre-test validation period (fold {selection_fold})",
            "Require actual validation coverage of all three fixed classes before ranking",
            "Validation multiclass log loss (ascending; primary probability score)",
            "Validation multiclass Brier score (ascending)",
            "Validation macro F1 and balanced accuracy (descending; tie-breakers)",
            "Top-label ECE is diagnostic only and is not used for ranking",
            "Validation ONI RMSE (ascending; common LSTM across classifiers)",
        ],
        "selection_note": (
            "Later validation origins overlap earlier test origins in this short "
            "record, so they are excluded from global model-family selection. "
            "No global candidate is selected for a horizon when the initial "
            "validation period lacks any ENSO phase. Validation is also used for "
            "tree-classifier early stopping, so remaining rankings are provisional. "
            "LSTM epoch selection uses a train-internal chronological segment. "
            "Probability scores use raw classifier outputs and are not calibrated."
        ),
        "selection_validation_fold": selection_fold,
        "test_metrics_used_for_selection": False,
        "probabilities_calibrated": False,
        "selected_models": selected_models,
    }
    return selection, model_comparison, horizon_comparison
