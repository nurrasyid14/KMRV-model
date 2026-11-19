import unittest

import numpy as np
import pandas as pd

from src.ml.final_retraining import eligible_training_origins, forecast_support


class FinalRetrainingTests(unittest.TestCase):
    def test_training_targets_stop_at_latest_observed_month(self):
        frame = pd.DataFrame(
            {"time": pd.date_range("2016-01-01", periods=114, freq="MS")}
        )

        for horizon in (1, 3, 6):
            origins = eligible_training_origins(frame, horizon, window=12)
            self.assertEqual(origins[0], 11)
            self.assertEqual(origins[-1], len(frame) - 1 - horizon)
            self.assertTrue(
                np.all(
                    frame["time"].iloc[origins + horizon].to_numpy()
                    <= frame["time"].iloc[-1].to_datetime64()
                )
            )
            self.assertTrue(
                np.all(
                    frame["time"].iloc[origins + horizon].to_numpy()
                    > frame["time"].iloc[origins].to_numpy()
                )
            )

    def test_eighteen_month_support_does_not_invent_intermediate_leads(self):
        support = forecast_support(18)

        self.assertEqual(len(support), 18)
        self.assertEqual(
            [row["horizon_months"] for row in support if row["forecast_generated"]],
            [1, 3, 6],
        )
        self.assertEqual(
            [row["horizon_months"] for row in support if not row["forecast_generated"]],
            [2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
        )

    def test_forecast_support_rejects_non_positive_months(self):
        with self.assertRaises(ValueError):
            forecast_support(0)


if __name__ == "__main__":
    unittest.main()
