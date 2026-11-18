"""ENSO training orchestration, model checkpointing, and report generation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_squared_error,
    precision_score,
    recall_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "model"
REPORT_DIR = PROJECT_ROOT / "reports"
ENSEMBLE_SCRIPT = PROJECT_ROOT / "src" / "ml" / "ensemble.py"
PHASE_NAMES = {0: "La Nina", 1: "Neutral", 2: "El Nino"}
SEASONS = ("DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ",
           "JJA", "JAS", "ASO", "SON", "OND", "NDJ")


def tri_monthly_season(date: pd.Timestamp) -> str:
    """Return the named three-month season for a target month."""
    return SEASONS[int(pd.Timestamp(date).month) - 1]


def validate_horizons(horizons: Iterable[int]) -> tuple[int, ...]:
    selected = tuple(dict.fromkeys(horizons))
    unsupported = set(selected) - {1, 3, 6}
    if unsupported:
        raise ValueError(f"Unsupported forecast horizons: {sorted(unsupported)}")
    if not selected:
        raise ValueError("At least one forecast horizon is required")
    return selected


def train_ensemble(
    horizons: Iterable[int] = (1, 3, 6),
    epochs: int = 300,
    seed: int = 42,
) -> dict[int, Path]:
    """Train each horizon through the implemented src/ml/ensemble.py entry point."""
    selected = validate_horizons(horizons)
    output_dirs: dict[int, Path] = {}

    for horizon in selected:
        output_dir = MODEL_DIR / f"enso_ensemble_{horizon}m"
        output_dir.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            str(ENSEMBLE_SCRIPT),
            "--horizon",
            str(horizon),
            "--epochs",
            str(epochs),
            "--seed",
            str(seed),
            "--output-dir",
            str(output_dir),
        ]
        result = subprocess.run(command, cwd=PROJECT_ROOT, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"ENSO ensemble training failed for {horizon}-month horizon "
                f"with exit code {result.returncode}"
            )
        output_dirs[horizon] = output_dir

    return output_dirs


def save_model_checkpoints(output_dirs: dict[int, Path]) -> dict[str, Path]:
    """Create recent_model.pt from the latest run and best_model.pt by validation RMSE."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    ranking: list[tuple[float, int, Path]] = []

    for horizon, output_dir in output_dirs.items():
        checkpoint = output_dir / f"lstm_horizon_{horizon}m.pt"
        metrics_file = output_dir / f"metrics_horizon_{horizon}m.json"
        if not checkpoint.exists() or not metrics_file.exists():
            raise FileNotFoundError(
                f"Incomplete ensemble artifacts for horizon {horizon}: "
                f"{checkpoint} or {metrics_file} is missing"
            )
        metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
        ranking.append(
            (float(metrics["validation"]["lstm_oni_rmse"]), horizon, checkpoint)
        )

    recent_checkpoint = ranking[-1][2]
    best_checkpoint = min(ranking, key=lambda row: row[0])[2]
    recent_path = MODEL_DIR / "recent_model.pt"
    best_path = MODEL_DIR / "best_model.pt"
    shutil.copy2(recent_checkpoint, recent_path)
    shutil.copy2(best_checkpoint, best_path)

    manifest = {
        "recent_model": recent_path.relative_to(PROJECT_ROOT).as_posix(),
        "best_model": best_path.relative_to(PROJECT_ROOT).as_posix(),
        "best_validation_horizon_months": min(ranking, key=lambda row: row[0])[1],
        "horizon_artifacts": {
            str(horizon): output_dir.resolve().relative_to(PROJECT_ROOT).as_posix()
            for horizon, output_dir in output_dirs.items()
        },
    }
    (MODEL_DIR / "model_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return {"recent": recent_path, "best": best_path}


def collect_metrics(output_dirs: dict[int, Path]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, object]] = []
    prediction_frames: list[pd.DataFrame] = []
    gradient_frames: list[pd.DataFrame] = []

    for horizon, output_dir in output_dirs.items():
        predictions = pd.read_csv(
            output_dir / f"test_predictions_horizon_{horizon}m.csv",
            parse_dates=["time"],
        )
        predictions["forecast_horizon_months"] = horizon
        predictions["tri_monthly_season"] = predictions["time"].map(tri_monthly_season)
        prediction_frames.append(predictions)

        gradient = pd.read_csv(
            output_dir / f"gradient_descent_horizon_{horizon}m.csv"
        )
        gradient["forecast_horizon_months"] = horizon
        gradient_frames.append(gradient)

        actual_phase = predictions[f"actual_phase_lead_{horizon}m"].to_numpy()
        predicted_phase = predictions[f"predicted_phase_lead_{horizon}m"].to_numpy()
        actual_oni = predictions[f"actual_oni_lead_{horizon}m"].to_numpy()
        forecast_oni = predictions[f"lstm_oni_lead_{horizon}m"].to_numpy()
        metric_rows.append({
            "split": "test",
            "forecast_horizon_months": horizon,
            "accuracy": accuracy_score(actual_phase, predicted_phase),
            "macro_f1": f1_score(actual_phase, predicted_phase, average="macro", zero_division=0),
            "macro_precision": precision_score(
                actual_phase,
                predicted_phase,
                average="macro",
                zero_division=0,
            ),
            "macro_recall": recall_score(
                actual_phase,
                predicted_phase,
                average="macro",
                zero_division=0,
            ),
            "oni_mse": mean_squared_error(actual_oni, forecast_oni),
        })
        plot_confusion_matrix(actual_phase, predicted_phase, horizon)

    metrics = pd.DataFrame(metric_rows)
    predictions = pd.concat(prediction_frames, ignore_index=True)
    gradients = pd.concat(gradient_frames, ignore_index=True)
    return metrics, predictions, gradients


def write_reports(
    metrics: pd.DataFrame,
    predictions: pd.DataFrame,
    gradients: pd.DataFrame,
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(REPORT_DIR / "enso_metrics.csv", index=False)
    predictions.to_csv(REPORT_DIR / "enso_forecast_predictions.csv", index=False)
    gradients.to_csv(REPORT_DIR / "gradient_descent.csv", index=False)
    plot_forecast_horizons(predictions)
    plot_gradient_descent(gradients)

    report = {
        "metrics": metrics.to_dict(orient="records"),
        "forecast_horizons_months": [
            int(value) for value in metrics["forecast_horizon_months"].unique()
        ],
        "tri_monthly_seasons": sorted(SEASONS),
        "output_directory": REPORT_DIR.resolve().as_posix(),
    }
    (REPORT_DIR / "enso_training_report.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )


def aggregate_and_report(output_dirs: dict[int, Path]) -> dict[str, object]:
    metrics, predictions, gradients = collect_metrics(output_dirs)
    write_reports(metrics, predictions, gradients)
    return json.loads((REPORT_DIR / "enso_training_report.json").read_text(encoding="utf-8"))


def plot_confusion_matrix(actual: np.ndarray, predicted: np.ndarray, horizon: int) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    labels = np.array([0, 1, 2])
    matrix = confusion_matrix(actual, predicted, labels=labels)
    display = ConfusionMatrixDisplay(
        matrix,
        display_labels=[PHASE_NAMES[label] for label in labels],
    )
    display.plot(cmap="Blues", colorbar=False)
    plt.title(f"ENSO Phase Confusion Matrix ({horizon}-Month Forecast)")
    plt.tight_layout()
    plt.savefig(REPORT_DIR / f"confusion_matrix_{horizon}m.png", dpi=150)
    plt.close()


def plot_gradient_descent(gradients: pd.DataFrame) -> None:
    fig, axis = plt.subplots(figsize=(9, 5))
    for horizon, frame in gradients.groupby("forecast_horizon_months"):
        axis.plot(frame["epoch"], frame["validation_mse"], label=f"{horizon}-month")
    axis.set_title("Validation Gradient Descent: MSE by Epoch")
    axis.set_xlabel("Epoch")
    axis.set_ylabel("Validation MSE")
    axis.grid(alpha=0.25)
    axis.legend()
    fig.tight_layout()
    fig.savefig(REPORT_DIR / "gradient_descent.png", dpi=150)
    plt.close(fig)


def plot_forecast_horizons(predictions: pd.DataFrame) -> None:
    fig, axis = plt.subplots(figsize=(12, 5))
    for horizon, frame in predictions.groupby("forecast_horizon_months"):
        frame = frame.sort_values("time")
        axis.plot(
            frame["time"],
            frame[f"actual_oni_lead_{horizon}m"],
            marker="o",
            linewidth=1,
            alpha=0.45,
            label=f"Actual {horizon}m",
        )
        axis.plot(
            frame["time"],
            frame[f"lstm_oni_lead_{horizon}m"],
            marker="x",
            linewidth=2,
            label=f"LSTM {horizon}m",
        )
    axis.axhline(0.5, color="red", linestyle="--", alpha=0.6)
    axis.axhline(-0.5, color="blue", linestyle="--", alpha=0.6)
    axis.axhline(0, color="gray", linestyle=":", alpha=0.5)
    axis.set_title("ENSO ONI Forecast Range by Horizon and Tri-Monthly Season")
    axis.set_xlabel("Target date")
    axis.set_ylabel("ONI / forecast anomaly")
    axis.grid(alpha=0.25)
    axis.legend(ncol=2)
    fig.tight_layout()
    fig.savefig(REPORT_DIR / "forecast_horizons.png", dpi=150)
    plt.close(fig)


def run(
    horizons: Iterable[int] = (1, 3, 6),
    epochs: int = 300,
    seed: int = 42,
) -> dict[str, object]:
    output_dirs = train_ensemble(horizons=horizons, epochs=epochs, seed=seed)
    checkpoints = save_model_checkpoints(output_dirs)
    report = aggregate_and_report(output_dirs)
    report["models"] = {name: str(path) for name, path in checkpoints.items()}
    return report
