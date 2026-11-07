"""Runnable data and model pipeline orchestration."""

import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

from src.learning import run as run_learning
from src.etl import ExploratoryDataAnalysis

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PipelineStage(NamedTuple):
    name: str
    status: str
    details: str


PIPELINE_STAGES = (
    PipelineStage(
        "NetCDF to Zarr",
        "implemented",
        "Convert each NetCDF dataset into a mirrored Zarr v2 store.",
    ),
    PipelineStage(
        "EDA",
        "implemented",
        "Report variables, shapes, dtypes, and missing values for converted stores.",
    ),
    PipelineStage(
        "Zarr extraction and preprocessing",
        "partial",
        "Load a selected variable, replace NaNs, normalize, and create sliding windows; spatial cropping is a placeholder.",
    ),
    PipelineStage(
        "Database storage and analytics reads",
        "implemented, not integrated",
        "PostgreSQL operations cover regions, observations, climate indices, predictions, and analytics table reads.",
    ),
    PipelineStage(
        "Model learning",
        "implemented",
        "Causal LSTM ONI forecasts combined with LightGBM ENSO phase classification.",
    ),
    PipelineStage(
        "Inference and prediction persistence",
        "planned",
        "Run the trained model on new data and save results to mhw_predictions.",
    ),
)

PIPELINE_CALL_GRAPH = {
    "main.py": ["src.pipeline.run_full_pipeline"],
    "src.pipeline.run_full_pipeline": [
        "src.pipeline.run_source_eda",
        "src.pipeline.run_data_preprocessing",
        "src.pipeline.run_enso_training",
    ],
    "src.pipeline.run_source_eda": ["src.etl.ExploratoryDataAnalysis", "src.utils.NCEncoder"],
    "src.pipeline.run_data_preprocessing": ["src.preprocessing.main"],
    "src.pipeline.run_enso_training": ["src.learning.run"],
    "src.learning.run": [
        "src.learning.validate_sequence_inputs",
        "src.utils.Preprocess.create_sliding_windows",
        "src.learning.train_ensemble",
        "src.ml.ensemble",
        "src.learning.aggregate_and_report",
    ],
    "src.ml.ensemble": [
        "src.ml.2lstm.CausalLSTM",
        "src.ml.lgbm.train_phase_classifier",
    ],
}


def run_enso_training(
    horizons: tuple[int, ...] = (1, 3, 6),
    epochs: int = 300,
    seed: int = 42,
) -> dict[str, object]:
    """Train all requested ENSO horizons and generate report artifacts."""
    return run_learning(horizons=horizons, epochs=epochs, seed=seed)


def run_data_preprocessing() -> Path:
    """Run the repository Zarr preprocessing module from the orchestrator."""
    output = PROJECT_ROOT / "dataset" / "climate_dataset.zarr"
    subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "src" / "preprocessing.py"),
            "--input-dir",
            str(PROJECT_ROOT / "dataset"),
            "--output",
            str(output),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )
    return output


def run_source_eda() -> Path:
    """Process raw SST NetCDF sources through src.etl and src.utils."""
    output_dir = PROJECT_ROOT / "data" / "processed" / "zarr"
    report_path = PROJECT_ROOT / "data" / "processed" / "eda_report.csv"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = ExploratoryDataAnalysis(
        PROJECT_ROOT / "dataset" / "sst_5_wilayah",
        output_dir,
    ).process_and_report()
    report.to_csv(report_path, index=False)
    return report_path


def run_full_pipeline(
    horizons: tuple[int, ...] = (1, 3, 6),
    epochs: int = 300,
    seed: int = 42,
    prepare_data: bool = False,
    run_eda: bool = False,
) -> dict[str, object]:
    import json

    if run_eda:
        run_source_eda()
    if prepare_data:
        run_data_preprocessing()
    report = run_enso_training(horizons=horizons, epochs=epochs, seed=seed)
    report["call_graph"] = PIPELINE_CALL_GRAPH
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "pipeline_call_graph.json").write_text(
        json.dumps(PIPELINE_CALL_GRAPH, indent=2),
        encoding="utf-8",
    )
    return report
