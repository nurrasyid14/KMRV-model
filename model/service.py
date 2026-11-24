from __future__ import annotations

import importlib
import json
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
        self.model_version = "legacy"
        self.promotion_status = "legacy_unverified"
        self.model_forecast_origin: str | None = None
        torch.set_num_threads(1)

        manifest_path = artifact_dir / "model_manifest.json"
        if manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("artifact_kind") == "final_forecasting_models":
                self._load_final_models(manifest_path)
            elif "horizon_artifacts" in manifest:
                self._load_legacy_models()
            else:
                raise ValueError(f"Unsupported model manifest: {manifest_path}")
        else:
            self._load_legacy_models()

    def _load_final_models(self, manifest_path: Path) -> None:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("artifact_kind") != "final_forecasting_models":
            raise ValueError(f"Unsupported model manifest: {manifest_path}")
        if sorted(manifest.get("forecast_horizons", [])) != list(HORIZONS):
            raise ValueError(
                f"Final model manifest must contain horizons {HORIZONS}"
            )
        self.model_version = str(manifest["model_version"])
        self.promotion_status = str(manifest["promotion_status"])
        self.model_forecast_origin = str(manifest["forecast_origin"])[:7]

        for horizon in HORIZONS:
            expected_directory = f"horizon_{horizon}m"
            if (
                manifest.get("model_directories", {}).get(str(horizon))
                != expected_directory
            ):
                raise ValueError(
                    f"Horizon {horizon} has an unexpected model directory"
                )
            model_dir = self.artifact_dir / expected_directory
            metadata = json.loads(
                (model_dir / "metadata" / "training_metadata.json").read_text(
                    encoding="utf-8"
                )
            )
            checkpoint = torch.load(
                model_dir / "lstm" / "model.pt",
                map_location="cpu",
                weights_only=True,
            )
            feature_columns = checkpoint["feature_columns"]
            if (
                metadata.get("model_version") != self.model_version
                or int(metadata.get("horizon_months", -1)) != horizon
                or feature_columns != manifest["feature_columns"]
                or metadata.get("feature_configuration", {}).get(
                    "feature_columns"
                )
                != feature_columns
            ):
                raise ValueError(
                    f"Horizon {horizon} artifact metadata is inconsistent"
                )
            window = int(checkpoint["window"])
            lstm = CausalLSTM(
                len(feature_columns),
                int(checkpoint["hidden_size"]),
                dropout=0.1,
            )
            lstm.load_state_dict(checkpoint["state_dict"])
            lstm.eval()

            expected_classifier_features = feature_columns + [
                "lstm_oni_forecast"
            ]
            classifier_config = metadata["classifier"]
            classifier_family = classifier_config["family"]
            expected_artifacts = {
                "XGBoost": "xgboost.json",
                "LightGBM": "lightgbm.txt",
            }
            if classifier_config.get("artifact_file") != expected_artifacts.get(
                classifier_family
            ):
                raise ValueError(
                    f"Horizon {horizon} has an unexpected classifier artifact"
                )
            classifier_path = (
                model_dir / "classifier" / classifier_config["artifact_file"]
            )
            if classifier_family == "XGBoost":
                classifier = XGBClassifier()
                classifier.load_model(str(classifier_path))
                classifier_features = classifier.get_booster().feature_names
                classes = np.asarray(classifier.classes_, dtype=np.int64)
            elif classifier_family == "LightGBM":
                import lightgbm as lgb

                classifier = lgb.Booster(model_file=str(classifier_path))
                classifier_features = classifier.feature_name()
                classes = np.arange(3, dtype=np.int64)
            else:
                raise ValueError(
                    f"Horizon {horizon} uses unsupported classifier "
                    f"{classifier_family!r}"
                )
            if not np.array_equal(classes, np.arange(len(PHASE_LABELS))):
                raise ValueError(
                    f"Horizon {horizon} classifier does not contain all phases"
                )
            if classifier_features != expected_classifier_features:
                raise ValueError(
                    f"Horizon {horizon} classifier features do not match "
                    "the LSTM feature schema"
                )

            feature_scaler = joblib.load(
                model_dir / "preprocessing" / "feature_scaler.joblib"
            )
            target_scaler = joblib.load(
                model_dir / "preprocessing" / "target_scaler.joblib"
            )
            if int(feature_scaler.n_features_in_) != len(feature_columns):
                raise ValueError(
                    f"Horizon {horizon} feature scaler has an unexpected shape"
                )
            if int(target_scaler.n_features_in_) != 1:
                raise ValueError(
                    f"Horizon {horizon} target scaler has an unexpected shape"
                )

            self.models[horizon] = {
                "lstm": lstm,
                "classifier": classifier,
                "classifier_family": classifier_family,
                "feature_columns": feature_columns,
                "classifier_features": expected_classifier_features,
                "classes": classes,
                "feature_scaler": feature_scaler,
                "target_scaler": target_scaler,
                "window": window,
            }

    def _load_legacy_models(self) -> None:
        for horizon in HORIZONS:
            model_dir = self.artifact_dir / f"enso_ensemble_{horizon}m"
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

            xgb_reg_path = model_dir / f"xgboost_regressor_horizon_{horizon}m.json"
            xgb_regressor = None
            if xgb_reg_path.is_file():
                from xgboost import XGBRegressor
                xgb_regressor = XGBRegressor()
                xgb_regressor.load_model(str(xgb_reg_path))

            metrics_path = model_dir / f"metrics_horizon_{horizon}m.json"
            ensemble_weights = {"lstm": 0.5, "xgboost": 0.5}
            if metrics_path.is_file():
                try:
                    m_data = json.loads(metrics_path.read_text(encoding="utf-8"))
                    if "ensemble_weights" in m_data:
                        ensemble_weights = m_data["ensemble_weights"]
                except Exception:
                    pass

            self.models[horizon] = {
                "lstm": lstm,
                "classifier": classifier,
                "classifier_family": "XGBoost",
                "xgb_regressor": xgb_regressor,
                "ensemble_weights": ensemble_weights,
                "feature_columns": feature_columns,
                "classifier_features": classifier_features,
                "classes": np.asarray(classifier.classes_, dtype=np.int64),
                "feature_scaler": feature_scaler,
                "target_scaler": target_scaler,
                "window": window,
            }

    def predict_latest(self, horizon: int) -> dict[str, object]:
        if horizon not in HORIZONS:
            raise ValueError(f"horizon must be one of {HORIZONS}")

        frame = pd.read_csv(self.features_path)
        if frame.empty or "time" not in frame.columns:
            raise ValueError(
                "Feature data must contain at least one row and a time column"
            )
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

        lstm_forecast = float(
            model["target_scaler"].inverse_transform(scaled_forecast)[0, 0]
        )
        if model.get("xgb_regressor") is not None:
            latest_tabular = frame.loc[[frame.index[-1]], feature_columns]
            xgb_forecast = float(model["xgb_regressor"].predict(latest_tabular)[0])
            weights = model.get("ensemble_weights", {"lstm": 0.5, "xgboost": 0.5})
            w_l = float(weights.get("lstm", 0.5))
            w_x = float(weights.get("xgboost", 0.5))
            forecast = float(w_l * lstm_forecast + w_x * xgb_forecast)
        else:
            forecast = lstm_forecast
        classifier_row = frame.loc[frame.index[-1], feature_columns].to_dict()
        classifier_row["lstm_oni_forecast"] = forecast
        classifier_input = pd.DataFrame(
            [classifier_row],
            columns=model["classifier_features"],
        )
        classifier = model["classifier"]
        if model["classifier_family"] == "LightGBM":
            class_probabilities = np.asarray(
                classifier.predict(classifier_input),
                dtype=np.float64,
            ).reshape(-1)
        else:
            class_probabilities = np.asarray(
                classifier.predict_proba(classifier_input)[0],
                dtype=np.float64,
            )
        if (
            class_probabilities.shape != (len(PHASE_LABELS),)
            or not np.isfinite(class_probabilities).all()
            or np.any(class_probabilities < 0.0)
            or not np.isclose(class_probabilities.sum(), 1.0, atol=1e-5)
        ):
            raise ValueError(
                f"Horizon {horizon} classifier returned invalid probabilities"
            )
        classes = np.asarray(model["classes"], dtype=np.int64)
        phase_id = int(classes[int(np.argmax(class_probabilities))])
        probabilities = {label: 0.0 for label in PHASE_LABELS.values()}
        for class_id, probability in zip(
            classes,
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
            "model": f"causal_lstm_{str(model['classifier_family']).lower()}",
            "classifier_family": model["classifier_family"],
            "model_version": self.model_version,
            "promotion_status": self.promotion_status,
            "model_forecast_origin": self.model_forecast_origin,
            "horizon_months": horizon,
            "input_through": input_through.strftime("%Y-%m"),
            "target_month": target_month.strftime("%Y-%m"),
            "predicted_oni": round(forecast, 4),
            "predicted_phase": {
                "class_id": phase_id,
                "label": PHASE_LABELS[phase_id],
            },
            "phase_probabilities": probabilities,
            "phase_confidence": round(float(class_probabilities.max()), 6),
            "probabilities_calibrated": False,
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
    return {
        "status": "ok",
        "available_horizons": sorted(engine.models),
        "model_version": engine.model_version,
        "promotion_status": engine.promotion_status,
        "model_forecast_origin": engine.model_forecast_origin,
    }


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
