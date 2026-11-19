import math
import os
import unittest
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import requests
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
model_service = import_module("model.service")
backend = import_module("backend.main")
InferenceEngine = model_service.InferenceEngine


class ModelInferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = InferenceEngine(
            ROOT / "model",
            ROOT / "dataset" / "features_master_unscaled.csv",
        )

    def test_latest_forecast_uses_loaded_horizon_artifacts(self):
        latest_input = pd.read_csv(ROOT / "dataset" / "features_master_unscaled.csv")[
            "time"
        ].iloc[-1]
        expected_input_month = pd.Timestamp(latest_input).strftime("%Y-%m")

        for horizon in (1, 3, 6):
            with self.subTest(horizon=horizon):
                forecast = self.engine.predict_latest(horizon)
                probabilities = forecast["phase_probabilities"]

                self.assertEqual(forecast["horizon_months"], horizon)
                self.assertEqual(forecast["input_through"], expected_input_month)
                self.assertTrue(math.isfinite(forecast["predicted_oni"]))
                self.assertIn(
                    forecast["predicted_phase"]["label"],
                    {"La Niña", "Netral", "El Niño"},
                )
                self.assertEqual(
                    set(probabilities),
                    {"La Niña", "Netral", "El Niño"},
                )
                self.assertAlmostEqual(sum(probabilities.values()), 1.0, places=5)

    def test_unsupported_horizon_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.predict_latest(2)

    def test_frontend_api_proxies_model_inference(self):
        with patch.dict(
            os.environ,
            {
                "MODEL_ARTIFACTS_DIR": str(ROOT / "model"),
                "FEATURES_FILE": str(
                    ROOT / "dataset" / "features_master_unscaled.csv"
                ),
            },
        ):
            with TestClient(model_service.app) as model_client:
                def request_model(url, params, timeout):
                    upstream = model_client.get(
                        "/api/v1/forecast/latest",
                        params=params,
                    )
                    response = requests.Response()
                    response.status_code = upstream.status_code
                    response._content = upstream.content
                    response.headers.update(upstream.headers)
                    response.url = url
                    return response

                with patch(
                    "backend.main.requests.get",
                    side_effect=request_model,
                ) as request:
                    with TestClient(backend.app) as frontend_client:
                        response = frontend_client.get(
                            "/api/v1/forecast/latest",
                            params={"horizon": 3},
                        )
                        invalid_response = frontend_client.get(
                            "/api/v1/forecast/latest",
                            params={"horizon": 2},
                        )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["horizon_months"], 3)
                self.assertEqual(
                    response.json()["model"],
                    "causal_lstm_xgboost",
                )
                self.assertEqual(request.call_args.kwargs["timeout"], 30)
                self.assertEqual(invalid_response.status_code, 422)
                request.assert_called_once()


if __name__ == "__main__":
    unittest.main()
