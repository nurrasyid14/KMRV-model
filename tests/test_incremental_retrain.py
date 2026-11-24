import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from src.incremental import (
    append_new_feature_observations,
    eligible_training_origins,
    retrain_from_full_data,
)
from src.utils import append_zarr_dataset


class IncrementalArchiveAndRetrainTests(unittest.TestCase):
    def test_append_new_feature_observations_without_rewriting_past(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "master.csv"
            initial_df = pd.DataFrame({
                "time": ["2023-01-01", "2023-02-01", "2023-03-01"],
                "sst": [28.1, 28.3, 28.5],
                "oni": [0.2, 0.4, 0.6],
            })
            initial_df.to_csv(csv_path, index=False)

            # Incoming batch with 1 existing timestamp and 2 new timestamps
            incoming_df = pd.DataFrame({
                "time": ["2023-03-01", "2023-04-01", "2023-05-01"],
                "sst": [28.5, 28.7, 28.9],
                "oni": [0.6, 0.8, 1.0],
            })

            updated_df, added = append_new_feature_observations(csv_path, incoming_df)

            self.assertEqual(added, 2)
            self.assertEqual(len(updated_df), 5)
            self.assertEqual(
                list(updated_df["time"].dt.strftime("%Y-%m-%d")),
                ["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01"],
            )

            # Test appending the same data again: 0 new rows
            updated_df2, added2 = append_new_feature_observations(csv_path, incoming_df)
            self.assertEqual(added2, 0)
            self.assertEqual(len(updated_df2), 5)

    def test_append_zarr_dataset_incrementally(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zarr_path = Path(tmpdir) / "store.zarr"

            times1 = pd.date_range("2023-01-01", periods=3, freq="MS")
            ds1 = xr.Dataset(
                {"sst": (("time", "lat", "lon"), np.ones((3, 2, 2), dtype=np.float32))},
                coords={"time": times1, "lat": [0.0, 1.0], "lon": [100.0, 101.0]},
            )
            append_zarr_dataset(ds1, zarr_path)

            # Append next month without rewriting initial chunk
            times2 = pd.date_range("2023-04-01", periods=2, freq="MS")
            ds2 = xr.Dataset(
                {"sst": (("time", "lat", "lon"), np.full((2, 2, 2), 2.0, dtype=np.float32))},
                coords={"time": times2, "lat": [0.0, 1.0], "lon": [100.0, 101.0]},
            )
            append_zarr_dataset(ds2, zarr_path)

            with xr.open_zarr(zarr_path) as opened:
                self.assertEqual(len(opened.time), 5)
                self.assertEqual(float(opened.sst[0, 0, 0]), 1.0)
                self.assertEqual(float(opened.sst[-1, 0, 0]), 2.0)

    def test_retrain_from_full_data_expanding_window(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "features.csv"
            out_dir = Path(tmpdir) / "models"
            n_rows = 60
            times = pd.date_range("2018-01-01", periods=n_rows, freq="MS")
            df = pd.DataFrame({
                "time": times,
                "f1": np.sin(np.linspace(0, 10, n_rows)),
                "f2": np.cos(np.linspace(0, 10, n_rows)),
                "target_oni_lead_1m": np.random.randn(n_rows),
                "target_phase_lead_1m": np.tile([0, 1, 2], n_rows // 3),
            })
            df.to_csv(csv_path, index=False)

            report = retrain_from_full_data(
                data_path=csv_path,
                horizons=(1,),
                epochs=5,
                window=6,
                hidden_size=8,
                seed=42,
                output_dir=out_dir,
            )

            self.assertEqual(report["status"], "success")
            self.assertFalse(report["xgb_model_warm_start_used"])
            self.assertIn("1", report["horizons"])
            h1 = report["horizons"]["1"]
            self.assertIn("ensemble_weights", h1)
            self.assertIn("lstm", h1["ensemble_weights"])
            self.assertIn("xgboost", h1["ensemble_weights"])
            self.assertAlmostEqual(sum(h1["ensemble_weights"].values()), 1.0, places=5)
            self.assertIn("latest_forecast", h1)
            self.assertIn("ensemble_predicted_oni", h1["latest_forecast"])


if __name__ == "__main__":
    unittest.main()
