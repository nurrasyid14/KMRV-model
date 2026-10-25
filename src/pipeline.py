"""Current data and model pipeline stages.

Statuses distinguish implemented data preparation from planned model stages;
this module records progress and does not run the pipeline.
"""

from typing import NamedTuple


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
        "planned",
        "LSTM temporal feature learning followed by LightGBM prediction; workflow documented in learning.py.",
    ),
    PipelineStage(
        "Inference and prediction persistence",
        "planned",
        "Run the trained model on new data and save results to mhw_predictions.",
    ),
)
