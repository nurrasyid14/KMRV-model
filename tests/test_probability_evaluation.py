import unittest

import numpy as np

from src.ml.evaluation import probability_evaluation


class ProbabilityEvaluationTests(unittest.TestCase):
    def test_scores_three_class_probabilities_and_top_label_calibration(self):
        labels = np.array([0, 1, 2])
        probabilities = np.array(
            [
                [0.8, 0.1, 0.1],
                [0.2, 0.7, 0.1],
                [0.2, 0.2, 0.6],
            ]
        )

        metrics = probability_evaluation(labels, probabilities)

        expected_log_loss = -np.mean(np.log([0.8, 0.7, 0.6]))
        expected_brier = np.mean(
            [
                (0.8 - 1) ** 2 + 0.1**2 + 0.1**2,
                0.2**2 + (0.7 - 1) ** 2 + 0.1**2,
                0.2**2 + 0.2**2 + (0.6 - 1) ** 2,
            ]
        )
        self.assertAlmostEqual(metrics["log_loss"], expected_log_loss)
        self.assertAlmostEqual(metrics["multiclass_brier_score"], expected_brier)
        self.assertAlmostEqual(metrics["top_label_ece_10_bins"], 0.3)
        self.assertAlmostEqual(metrics["mean_top_label_confidence"], 0.7)

    def test_rejects_malformed_probability_rows(self):
        with self.assertRaises(ValueError):
            probability_evaluation(
                np.array([0]),
                np.array([[0.5, 0.5, 0.5]]),
            )

    def test_confidently_wrong_predictions_are_penalized(self):
        labels = np.array([0])
        correct = probability_evaluation(
            labels,
            np.array([[0.8, 0.1, 0.1]]),
        )
        wrong = probability_evaluation(
            labels,
            np.array([[0.1, 0.8, 0.1]]),
        )

        self.assertGreater(wrong["log_loss"], correct["log_loss"])
        self.assertGreater(
            wrong["multiclass_brier_score"],
            correct["multiclass_brier_score"],
        )


if __name__ == "__main__":
    unittest.main()
