import unittest
import numpy as np
import pandas as pd

from src.ml.ensemble import (
    calculate_hindcast_skill_weights,
    train_xgboost_regressor,
)


class EnsembleXGBoostSkillWeightingTests(unittest.TestCase):
    def test_skill_weights_sum_to_one(self):
        actual = np.array([0.5, 0.8, -0.2, -0.6, 1.1])
        preds_lstm = np.array([0.4, 0.7, -0.1, -0.5, 1.0])
        preds_xgb = np.array([0.6, 0.9, -0.3, -0.7, 1.2])

        weights = calculate_hindcast_skill_weights(
            actual,
            {"lstm": preds_lstm, "xgboost": preds_xgb},
        )

        self.assertIn("lstm", weights)
        self.assertIn("xgboost", weights)
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=6)
        self.assertGreater(weights["lstm"], 0.0)
        self.assertGreater(weights["xgboost"], 0.0)

    def test_skill_weights_are_dynamic_not_fixed(self):
        actual = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        # LSTM has very low error, XGBoost has higher error
        preds_lstm = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
        preds_xgb = np.array([0.5, 0.5, 0.5, 0.5, 0.5])

        weights = calculate_hindcast_skill_weights(
            actual,
            {"lstm": preds_lstm, "xgboost": preds_xgb},
        )

        # Higher skill (lower RMSE) must receive substantially higher weight
        self.assertGreater(weights["lstm"], weights["xgboost"])
        self.assertNotEqual(weights["lstm"], 0.5)
        self.assertNotEqual(weights["xgboost"], 0.5)

    def test_equal_skill_yields_equal_weights(self):
        actual = np.array([1.0, 2.0, 3.0])
        preds_1 = np.array([1.1, 2.1, 3.1])
        preds_2 = np.array([0.9, 1.9, 2.9])

        weights = calculate_hindcast_skill_weights(
            actual,
            {"model_a": preds_1, "model_b": preds_2},
        )
        self.assertAlmostEqual(weights["model_a"], 0.5, places=5)
        self.assertAlmostEqual(weights["model_b"], 0.5, places=5)

    def test_xgboost_regressor_trains_from_scratch(self):
        np.random.seed(42)
        X = pd.DataFrame({
            "feat_1": np.random.randn(50),
            "feat_2": np.random.randn(50),
        })
        y = 0.5 * X["feat_1"] - 0.3 * X["feat_2"] + 0.1 * np.random.randn(50)

        model = train_xgboost_regressor(
            X,
            y.to_numpy(),
            random_state=42,
            n_estimators=20,
        )

        preds = model.predict(X)
        self.assertEqual(len(preds), 50)
        # Verify predictions correlate well with target
        correlation = np.corrcoef(preds, y)[0, 1]
        self.assertGreater(correlation, 0.7)


if __name__ == "__main__":
    unittest.main()
