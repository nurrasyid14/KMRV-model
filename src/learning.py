"""Train and report the ENSO forecasting models used by the project pipeline."""

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
from src.utils import Preprocess


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"
MODEL_DIR = PROJECT_ROOT / "model"
REPORT_DIR = PROJECT_ROOT / "reports"
ENSEMBLE_SCRIPT = Path(__file__).resolve().parent / "ml" / "ensemble.py"
SEASON_NAMES = {
    1: "DJF",
    2: "JFM",
    3: "FMA",
    4: "MAM",
    5: "AMJ",
    6: "MJJ",
    7: "JJA",
    8: "JAS",
    9: "ASO",
    10: "SON",
    11: "OND",
    12: "NDJ",
}
PHASE_NAMES = {0: "La Nina", 1: "Neutral", 2: "El Nino"}


def tri_monthly_label(month: pd.Timestamp) -> str:
    """Return the 3-month season label centered on the supplied month."""
    return SEASON_NAMES[int(pd.Timestamp(month).month)]


def validate_sequence_inputs(data_dir: Path = DATASET_DIR) -> dict[str, list[int]]:
    """Exercise the shared sliding-window utility against every training split."""
    train_path = data_dir / "train_features.csv"
    frame = pd.read_csv(train_path)
    values = torch_tensor(frame["oni_anom"].to_numpy(dtype=np.float32))
    shapes: dict[str, list[int]] = {}
    for horizon in (1, 3, 6):
        windows, targets = Preprocess.create_sliding_windows(
            values,
            input_window=12,
            horizon=horizon,
        )
        shapes[str(horizon)] = [list(windows.shape), list(targets.shape)]
    return shapes


def torch_tensor(values: np.ndarray):
    import torch

    return torch.tensor(values, dtype=torch.float32)


def train_ensemble(
    horizons: Iterable[int] = (1, 3, 6),
    epochs: int = 300,
    seed: int = 42,
) -> dict[int, Path]:
    """Run the ensemble training script once for each requested horizon."""
    output_dirs: dict[int, Path] = {}
    for horizon in horizons:
        if horizon not in (1, 3, 6):
            raise ValueError("Supported ENSO horizons are 1, 3, and 6 months")
        output_dir = MODEL_DIR / f"enso_ensemble_{horizon}m"
        output_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
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
            ],
            cwd=PROJECT_ROOT,
            check=True,
        )
        output_dirs[horizon] = output_dir
    return output_dirs


def save_model_checkpoints(output_dirs: dict[int, Path]) -> dict[str, Path]:
    """Keep one recent checkpoint per run and the strongest validation checkpoint."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    recent_path = MODEL_DIR / "recent_model.pt"
    best_path = MODEL_DIR / "best_model.pt"
    ranked: list[tuple[float, int, Path]] = []
    for horizon, output_dir in output_dirs.items():
        checkpoint = output_dir / f"lstm_horizon_{horizon}m.pt"
        metrics_path = output_dir / f"metrics_horizon_{horizon}m.json"
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        rmse = metrics["validation"]["lstm_oni_rmse"]
        ranked.append((rmse, horizon, checkpoint))

    newest = ranked[-1][2]
    shutil.copy2(newest, recent_path)
    _, best_horizon, best_checkpoint = min(ranked, key=lambda item: item[0])
    shutil.copy2(best_checkpoint, best_path)
    write_model_manifest(output_dirs, recent_path, best_path, best_horizon)
    return {"recent": recent_path, "best": best_path}


def write_model_manifest(
    output_dirs: dict[int, Path],
    recent_path: Path,
    best_path: Path,
    best_horizon: int,
) -> None:
    manifest = {
        "recent_model": str(recent_path.relative_to(PROJECT_ROOT)),
        "best_model": str(best_path.relative_to(PROJECT_ROOT)),
        "best_validation_horizon_months": best_horizon,
        "horizon_artifacts": {
            str(horizon): str(path.resolve().relative_to(PROJECT_ROOT))
            for horizon, path in output_dirs.items()
        },
    }
    (MODEL_DIR / "model_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def aggregate_and_report(output_dirs: dict[int, Path]) -> dict[str, object]:
    """Build metrics, forecasts, confusion matrices, and learning curves."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    metrics_rows: list[dict[str, object]] = []
    prediction_frames: list[pd.DataFrame] = []
    gradient_frames: list[pd.DataFrame] = []

    for horizon, output_dir in output_dirs.items():
        metrics = json.loads(
            (output_dir / f"metrics_horizon_{horizon}m.json").read_text(encoding="utf-8")
        )
        predictions = pd.read_csv(
            output_dir / f"test_predictions_horizon_{horizon}m.csv",
            parse_dates=["time"],
        )
        predictions["forecast_horizon_months"] = horizon
        predictions["tri_monthly_season"] = predictions["time"].map(tri_monthly_label)
        prediction_frames.append(predictions)

        gradient = pd.read_csv(
            output_dir / f"gradient_descent_horizon_{horizon}m.csv"
        )
        gradient["forecast_horizon_months"] = horizon
        gradient_frames.append(gradient)

        actual_phase = predictions[f"actual_phase_lead_{horizon}m"].to_numpy()
        predicted_phase = predictions[f"predicted_phase_lead_{horizon}m"].to_numpy()
        metrics_rows.append({
            "split": "test",
            "forecast_horizon_months": horizon,
            "accuracy": accuracy_score(actual_phase, predicted_phase),
            "balanced_accuracy": metrics["test"]["balanced_accuracy"],
            "macro_f1": f1_score(actual_phase, predicted_phase, average="macro", zero_division=0),
            "macro_precision": precision_score(
                actual_phase, predicted_phase, average="macro", zero_division=0
            ),
            "macro_recall": recall_score(
                actual_phase, predicted_phase, average="macro", zero_division=0
            ),
            "oni_mse": mean_squared_error(
                predictions[f"actual_oni_lead_{horizon}m"],
                predictions[f"lstm_oni_lead_{horizon}m"],
            ),
            "oni_rmse": metrics["test"]["lstm_oni_rmse"],
        })
        plot_confusion_matrix(actual_phase, predicted_phase, horizon)

    predictions = pd.concat(prediction_frames, ignore_index=True)
    gradients = pd.concat(gradient_frames, ignore_index=True)
    metrics_frame = pd.DataFrame(metrics_rows)
    predictions.to_csv(REPORT_DIR / "enso_forecast_predictions.csv", index=False)
    gradients.to_csv(REPORT_DIR / "gradient_descent.csv", index=False)
    metrics_frame.to_csv(REPORT_DIR / "enso_metrics.csv", index=False)
    plot_forecast_horizons(predictions)
    plot_gradient_descent(gradients)
    report = {
        "metrics": metrics_frame.to_dict(orient="records"),
        "output_directory": str(REPORT_DIR),
        "forecast_horizons_months": sorted(output_dirs),
        "tri_monthly_seasons": sorted(predictions["tri_monthly_season"].unique()),
    }
    (REPORT_DIR / "enso_training_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    return report


def plot_confusion_matrix(actual: np.ndarray, predicted: np.ndarray, horizon: int) -> None:
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
    validate_sequence_inputs()
    output_dirs = train_ensemble(horizons=horizons, epochs=epochs, seed=seed)
    checkpoints = save_model_checkpoints(output_dirs)
    report = aggregate_and_report(output_dirs)
    report["models"] = {name: str(path) for name, path in checkpoints.items()}
    return report
