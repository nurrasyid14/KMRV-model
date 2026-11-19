from __future__ import annotations

import importlib
import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from fastapi import FastAPI, HTTPException, Query, Request
from xgboost import XGBClassifier

HORIZONS = (1, 3, 6)
PHASE_LABELS = {0: "La Niña", 1: "Netral", 2: "El Niño"}

LSTM_MODULE = importlib.import_module("src.ml.2lstm")
CausalLSTM = LSTM_MODULE.CausalLSTM
MODEL_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = MODEL_ROOT.parent


class InferenceEngine:
    def __init__(self, artifact_dir: Path, features_path: Path) -> None:
        self.artifact_dir = artifact_dir
        self.features_path = features_path
        self.models: dict[int, dict[str, object]] = {}
        torch.set_num_threads(1)

        for horizon in HORIZONS:
            model_dir = artifact_dir / f"enso_ensemble_{horizon}m"
            checkpoint = torch.load(
                model_dir / f"lstm_horizon_{horizon}m.pt",
                map_location="cpu",
                weights_only=True,
            )
            feature_columns = checkpoint["feature_columns"]
            window = int(checkpoint["window"])
            lstm = CausalLSTM(
                len(feature_columns),
                int(checkpoint["hidden_size"]),
                dropout=0.1,
            )
            lstm.load_state_dict(checkpoint["state_dict"])
            lstm.eval()

            classifier = XGBClassifier()
            classifier.load_model(
                str(model_dir / f"xgboost_horizon_{horizon}m.json")
            )
            classifier_features = classifier.get_booster().feature_names
            expected_features = feature_columns + ["lstm_oni_forecast"]
            if classifier_features != expected_features:
                raise ValueError(
                    f"Horizon {horizon} classifier features do not match "
                    "the LSTM checkpoint"
                )

            feature_scaler = joblib.load(
                model_dir / f"feature_scaler_horizon_{horizon}m.joblib"
            )
            target_scaler = joblib.load(
                model_dir / f"target_scaler_horizon_{horizon}m.joblib"
            )
            if int(feature_scaler.n_features_in_) != len(feature_columns):
                raise ValueError(
                    f"Horizon {horizon} feature scaler has an unexpected shape"
                )

            self.models[horizon] = {
                "lstm": lstm,
                "classifier": classifier,
                "feature_columns": feature_columns,
                "classifier_features": classifier_features,
                "feature_scaler": feature_scaler,
                "target_scaler": target_scaler,
                "window": window,
            }

    def predict_latest(self, horizon: int) -> dict[str, object]:
        if horizon not in HORIZONS:
            raise ValueError(f"horizon must be one of {HORIZONS}")

        frame = pd.read_csv(self.features_path)
        if frame.empty or "time" not in frame.columns:
            raise ValueError("Feature data must contain at least one row and a time column")
        frame["time"] = pd.to_datetime(frame["time"], errors="raise")
        frame = frame.sort_values("time").reset_index(drop=True)

        model = self.models[horizon]
        feature_columns = model["feature_columns"]
        missing_columns = sorted(set(feature_columns) - set(frame.columns))
        if missing_columns:
            raise ValueError(f"Feature data is missing columns: {missing_columns}")

        window = int(model["window"])
        if len(frame) < window:
            raise ValueError(
                f"Feature data has {len(frame)} rows; at least {window} are required"
            )

        latest_features = frame.loc[:, feature_columns]
        if not np.isfinite(latest_features.to_numpy(dtype=np.float64)).all():
            raise ValueError("Feature data contains missing or non-finite values")

        scaler = model["feature_scaler"]
        scaled = scaler.transform(latest_features.tail(window)).astype(np.float32)
        inputs = torch.from_numpy(scaled).unsqueeze(0)
        with torch.no_grad():
            scaled_forecast = model["lstm"](inputs).numpy().reshape(-1, 1)

        forecast = float(
            model["target_scaler"].inverse_transform(scaled_forecast)[0, 0]
        )
        classifier_row = frame.loc[frame.index[-1], feature_columns].to_dict()
        classifier_row["lstm_oni_forecast"] = forecast
        classifier_input = pd.DataFrame(
            [classifier_row],
            columns=model["classifier_features"],
        )
        classifier = model["classifier"]
        phase_id = int(classifier.predict(classifier_input)[0])
        class_probabilities = classifier.predict_proba(classifier_input)[0]
        probabilities = {label: 0.0 for label in PHASE_LABELS.values()}
        for class_id, probability in zip(
            classifier.classes_,
            class_probabilities,
            strict=True,
        ):
            probabilities[PHASE_LABELS[int(class_id)]] = round(
                float(probability),
                6,
            )

        input_through = frame.iloc[-1]["time"]
        target_month = input_through + pd.DateOffset(months=horizon)
        return {
            "model": "causal_lstm_xgboost",
            "horizon_months": horizon,
            "input_through": input_through.strftime("%Y-%m"),
            "target_month": target_month.strftime("%Y-%m"),
            "predicted_oni": round(forecast, 4),
            "predicted_phase": {
                "class_id": phase_id,
                "label": PHASE_LABELS[phase_id],
            },
            "phase_probabilities": probabilities,
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    artifact_dir = Path(os.getenv("MODEL_ARTIFACTS_DIR", str(MODEL_ROOT)))
    features_path = Path(
        os.getenv(
            "FEATURES_FILE",
            str(PROJECT_ROOT / "dataset" / "features_master_unscaled.csv"),
        )
    )
    app.state.inference_engine = InferenceEngine(artifact_dir, features_path)
    yield


app = FastAPI(title="ENSO Model Inference API", lifespan=lifespan)


@app.get("/health")
def health(request: Request) -> dict[str, object]:
    engine: InferenceEngine = request.app.state.inference_engine
    return {"status": "ok", "available_horizons": sorted(engine.models)}


@app.get("/api/v1/forecast/latest")
def predict_latest(
    request: Request,
    horizon: int = Query(default=1),
) -> dict[str, object]:
    if horizon not in HORIZONS:
        raise HTTPException(
            status_code=422,
            detail=f"horizon must be one of {HORIZONS}",
        )
    engine: InferenceEngine = request.app.state.inference_engine
    try:
        return engine.predict_latest(horizon)
    except (OSError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
