#!/usr/bin/env python
"""Causal LSTM + LightGBM ensemble for monthly ENSO phase forecasts.

The LSTM predicts the future ONI value. LightGBM consumes the forecast and
tabular climate features to classify El Niño, La Niña, and Neutral phases.
Every split is processed chronologically; future split observations are never
used to fit preprocessing or model parameters.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
from pathlib import Path
from typing import Iterable

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    mean_squared_error,
)
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "dataset"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "model" / "enso_ensemble"
PHASE_NAMES = {0: "La Nina", 1: "Neutral", 2: "El Nino"}
PHASE_CLASSES = np.array([0, 1, 2], dtype=np.int64)


class CausalLSTM(nn.Module):
    def __init__(self, feature_count: int, hidden_size: int, dropout: float) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=feature_count,
            hidden_size=hidden_size,
            num_layers=1,
            batch_first=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.output = nn.Linear(hidden_size, 1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        _, (hidden, _) = self.lstm(inputs)
        return self.output(self.dropout(hidden[-1])).squeeze(-1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=DEFAULT_DATA_DIR / "train_features.csv")
    parser.add_argument("--validation", type=Path, default=DEFAULT_DATA_DIR / "val_features.csv")
    parser.add_argument("--test", type=Path, default=DEFAULT_DATA_DIR / "test_features.csv")
    parser.add_argument("--horizon", type=int, choices=(1, 3, 6), default=1)
    parser.add_argument("--window", type=int, default=12)
    parser.add_argument("--hidden-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=0.003)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_split(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if "time" not in frame.columns:
        raise ValueError(f"{path} must contain a 'time' column")
    frame["time"] = pd.to_datetime(frame["time"], errors="raise")
    frame = frame.sort_values("time").reset_index(drop=True)
    return frame


def resolve_feature_columns(frame: pd.DataFrame) -> list[str]:
    return [
        column
        for column in frame.columns
        if column != "time" and not column.startswith("target_")
    ]


def make_windows(values: np.ndarray, targets: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray]:
    if len(values) < window:
        raise ValueError(
            f"{len(values)} rows are not enough for a {window}-month LSTM window"
        )
    features = np.stack([values[start:start + window] for start in range(len(values) - window + 1)])
    labels = targets[window - 1:]
    return features.astype(np.float32), labels.astype(np.float32)


def train_lstm(
    train_windows: tuple[np.ndarray, np.ndarray],
    validation_windows: tuple[np.ndarray, np.ndarray],
    feature_count: int,
    hidden_size: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    seed: int,
) -> CausalLSTM:
    seed_everything(seed)
    train_x, train_y = train_windows
    val_x, val_y = validation_windows
    model = CausalLSTM(feature_count, hidden_size, dropout=0.1)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_function = nn.MSELoss()
    loader = DataLoader(
        TensorDataset(torch.from_numpy(train_x), torch.from_numpy(train_y)),
        batch_size=batch_size,
        shuffle=True,
    )

    best_state: dict[str, torch.Tensor] | None = None
    best_loss = float("inf")
    epochs_without_improvement = 0
    val_x_tensor = torch.from_numpy(val_x)
    val_y_tensor = torch.from_numpy(val_y)

    for _ in range(epochs):
        model.train()
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            prediction = model(batch_x)
            loss = loss_function(prediction, batch_y)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            validation_loss = loss_function(model(val_x_tensor), val_y_tensor).item()
        if validation_loss < best_loss - 1e-5:
            best_loss = validation_loss
            best_state = copy.deepcopy(model.state_dict())
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
        if epochs_without_improvement >= 30:
            break

    if best_state is not None:
        model.load_state_dict(best_state)
    return model


def predict_lstm(model: CausalLSTM, windows: np.ndarray) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        prediction = model(torch.from_numpy(windows))
    return prediction.numpy().reshape(-1)


def tabular_ensemble_features(
    split: pd.DataFrame,
    feature_columns: Iterable[str],
    lstm_predictions: np.ndarray,
    window: int,
) -> pd.DataFrame:
    columns = list(feature_columns) + ["lstm_oni_forecast"]
    start = window - 1
    features = split.iloc[start:][list(feature_columns)].copy().reset_index(drop=True)
    features["lstm_oni_forecast"] = lstm_predictions
    features = features[columns].replace([np.inf, -np.inf], np.nan)
    if features.isna().any().any():
        raise ValueError("NaN or infinite values remain after creating ensemble features")
    return features


def train_lightgbm(
    features: pd.DataFrame,
    labels: np.ndarray,
    validation_features: pd.DataFrame,
    validation_labels: np.ndarray,
) -> lgb.LGBMClassifier:
    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=len(PHASE_CLASSES),
        n_estimators=300,
        learning_rate=0.03,
        num_leaves=7,
        max_depth=3,
        min_child_samples=5,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        random_state=42,
        verbose=-1,
    )
    model.fit(
        features,
        labels,
        eval_set=[(validation_features, validation_labels)],
        callbacks=[lgb.early_stopping(50, verbose=False)],
    )
    return model


def classification_metrics(labels: np.ndarray, predictions: np.ndarray) -> dict[str, float | list[int]]:
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(labels, predictions)),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=PHASE_CLASSES).tolist(),
    }


def main() -> None:
    args = parse_args()
    seed_everything(args.seed)
    train = load_split(args.train)
    validation = load_split(args.validation)
    test = load_split(args.test)

    oni_target = f"target_oni_lead_{args.horizon}m"
    phase_target = f"target_phase_lead_{args.horizon}m"
    required = {oni_target, phase_target}
    for name, split in (("train", train), ("validation", validation), ("test", test)):
        missing = required - set(split.columns)
        if missing:
            raise ValueError(f"{name} split is missing target columns: {sorted(missing)}")
        if split[list(required)].isna().any().any():
            raise ValueError(f"{name} split contains missing target values")

    feature_columns = resolve_feature_columns(train)
    missing_features = [column for column in feature_columns if column not in validation or column not in test]
    if missing_features:
        raise ValueError(f"Feature columns are missing in validation/test: {missing_features}")

    feature_scaler = StandardScaler()
    train_scaled = feature_scaler.fit_transform(train[feature_columns])
    validation_scaled = feature_scaler.transform(validation[feature_columns])
    test_scaled = feature_scaler.transform(test[feature_columns])

    target_scaler = StandardScaler()
    train_target_scaled = target_scaler.fit_transform(train[[oni_target]]).reshape(-1).astype(np.float32)
    validation_target_scaled = target_scaler.transform(validation[[oni_target]]).reshape(-1).astype(np.float32)

    train_x, train_y = make_windows(train_scaled.astype(np.float32), train_target_scaled, args.window)
    validation_x, validation_y = make_windows(
        validation_scaled.astype(np.float32),
        validation_target_scaled,
        args.window,
    )
    test_target_scaled = target_scaler.transform(test[[oni_target]]).reshape(-1).astype(np.float32)
    test_x, test_y = make_windows(test_scaled.astype(np.float32), test_target_scaled, args.window)

    lstm = train_lstm(
        (train_x, train_y),
        (validation_x, validation_y),
        len(feature_columns),
        args.hidden_size,
        args.epochs,
        args.batch_size,
        args.learning_rate,
        args.seed,
    )

    train_lstm_scaled = predict_lstm(lstm, train_x)
    validation_lstm_scaled = predict_lstm(lstm, validation_x)
    test_lstm_scaled = predict_lstm(lstm, test_x)
    train_lstm_forecast = target_scaler.inverse_transform(train_lstm_scaled.reshape(-1, 1)).reshape(-1)
    validation_lstm_forecast = target_scaler.inverse_transform(validation_lstm_scaled.reshape(-1, 1)).reshape(-1)
    test_lstm_forecast = target_scaler.inverse_transform(test_lstm_scaled.reshape(-1, 1)).reshape(-1)

    train_lgb_features = tabular_ensemble_features(
        train, feature_columns, train_lstm_forecast, args.window
    )
    validation_lgb_features = tabular_ensemble_features(
        validation, feature_columns, validation_lstm_forecast, args.window
    )
    test_lgb_features = tabular_ensemble_features(
        test, feature_columns, test_lstm_forecast, args.window
    )
    train_labels = train[phase_target].to_numpy(dtype=np.int64)[args.window - 1:]
    validation_labels = validation[phase_target].to_numpy(dtype=np.int64)[args.window - 1:]
    test_labels = test[phase_target].to_numpy(dtype=np.int64)[args.window - 1:]
    classifier = train_lightgbm(
        train_lgb_features,
        train_labels,
        validation_lgb_features,
        validation_labels,
    )

    validation_phase = classifier.predict(validation_lgb_features).astype(np.int64)
    production_features = pd.concat(
        [train_lgb_features, validation_lgb_features], ignore_index=True
    )
    production_labels = np.concatenate([train_labels, validation_labels])
    production_classifier = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=len(PHASE_CLASSES),
        n_estimators=max(1, classifier.best_iteration_),
        learning_rate=0.03,
        num_leaves=7,
        max_depth=3,
        min_child_samples=5,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        random_state=args.seed,
        verbose=-1,
    )
    production_classifier.fit(production_features, production_labels)
    test_phase = production_classifier.predict(test_lgb_features).astype(np.int64)
    validation_actual_oni = validation[oni_target].to_numpy()[args.window - 1:]
    test_actual_oni = test[oni_target].to_numpy()[args.window - 1:]
    metrics = {
        "horizon_months": args.horizon,
        "window_months": args.window,
        "model": "causal_lstm_lightgbm",
        "class_mapping": PHASE_NAMES,
        "validation": {
            **classification_metrics(validation_labels, validation_phase),
            "lstm_oni_rmse": float(
                np.sqrt(mean_squared_error(validation_actual_oni, validation_lstm_forecast))
            ),
        },
        "test": {
            **classification_metrics(test_labels, test_phase),
            "lstm_oni_rmse": float(
                np.sqrt(mean_squared_error(test_actual_oni, test_lstm_forecast))
            ),
        },
    }

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": lstm.state_dict(),
            "feature_columns": feature_columns,
            "hidden_size": args.hidden_size,
            "window": args.window,
            "horizon_months": args.horizon,
        },
        output_dir / f"lstm_horizon_{args.horizon}m.pt",
    )
    production_classifier.booster_.save_model(
        str(output_dir / f"lightgbm_horizon_{args.horizon}m.txt")
    )
    joblib.dump(feature_scaler, output_dir / f"feature_scaler_horizon_{args.horizon}m.joblib")
    joblib.dump(target_scaler, output_dir / f"target_scaler_horizon_{args.horizon}m.joblib")
    (output_dir / f"metrics_horizon_{args.horizon}m.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    predictions = pd.DataFrame(
        {
            "time": test["time"].iloc[args.window - 1:].reset_index(drop=True),
            f"actual_oni_lead_{args.horizon}m": test_actual_oni,
            f"lstm_oni_lead_{args.horizon}m": test_lstm_forecast,
            f"actual_phase_lead_{args.horizon}m": test_labels,
            f"predicted_phase_lead_{args.horizon}m": test_phase,
        }
    )
    predictions.to_csv(output_dir / f"test_predictions_horizon_{args.horizon}m.csv", index=False)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()