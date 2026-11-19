import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.ml.audit import _class_coverage_report
from src.ml.backtesting import LSTMConfig, _fit_outer_lstm, _select_models
from src.ml.evaluation import classification_evaluation
from src.ml.reporting import (
    _fold_class_diagnostics,
    _plot_oni_forecasts,
    _plot_oni_residuals,
    _write_confusion_matrices,
    _write_final_report,
    _plot_fold_distribution,
)
from src.ml.temporal import (
    build_expanding_folds,
    fold_feasibility_sweep,
    fold_indices,
    validation_window_sweep,
)


class TemporalBacktestingTests(unittest.TestCase):
    def test_expanding_folds_are_chronological_and_cover_full_test_periods(self):
        folds = build_expanding_folds(114)

        self.assertEqual(len(folds), 2)
        self.assertEqual(
            [(fold.train_end, fold.validation_end, fold.test_end) for fold in folds],
            [(60, 78, 96), (78, 96, 114)],
        )
        self.assertGreater(folds[1].train_end, folds[0].train_end)

    def test_horizon_purge_keeps_train_and_validation_targets_before_next_split(self):
        fold = build_expanding_folds(114)[0]

        for horizon in (1, 3, 6):
            indices = fold_indices(fold, horizon, window=12)
            self.assertTrue(np.all(indices["train"] + horizon < fold.validation_start))
            self.assertTrue(np.all(indices["validation"] + horizon < fold.test_start))
            self.assertEqual(len(indices["test"]), 18)

    def test_configured_terminal_fold_has_adequate_validation_support(self):
        fold = build_expanding_folds(
            114,
            min_train_months=72,
            validation_months=24,
            test_months=18,
            step_months=18,
        )[0]
        self.assertEqual(
            (fold.train_end, fold.validation_end, fold.test_end),
            (72, 96, 114),
        )
        for horizon in (1, 3, 6):
            indices = fold_indices(fold, horizon, window=12)
            self.assertTrue(
                np.all(indices["train"] + horizon < fold.validation_start)
            )
            self.assertTrue(
                np.all(indices["validation"] + horizon < fold.test_start)
            )

    def test_validation_window_sweep_reports_coverage_and_usable_samples(self):
        frame = pd.DataFrame(
            {
                "time": pd.date_range("2016-01-01", periods=114, freq="MS"),
                **{
                    f"target_phase_lead_{horizon}m": np.tile([0, 1, 2], 38)
                    for horizon in (1, 3, 6)
                },
            }
        )

        sweep = validation_window_sweep(frame)
        configured = sweep.loc[
            (sweep["validation_months"] == 24)
            & (sweep["horizon_months"] == 6)
        ].iloc[0]

        self.assertEqual(configured["train_months"], 72)
        self.assertEqual(configured["validation_sample_count"], 18)
        self.assertEqual(configured["actual_class_coverage"], 3)
        self.assertEqual(configured["coverage_status"], "complete_class_coverage")
        self.assertTrue(configured["is_configured_window"])

    def test_fold_sweep_flags_class_support_and_prior_test_reuse(self):
        frame = pd.DataFrame(
            {
                "time": pd.date_range("2016-01-01", periods=114, freq="MS"),
                "target_phase_lead_6m": np.tile([0, 1, 2], 38),
            }
        )

        sweep = fold_feasibility_sweep(
            frame,
            horizons=(6,),
            min_train_periods=(60,),
            validation_periods=(18,),
            test_periods=(18,),
        )

        first = sweep.loc[sweep["fold"] == 1].iloc[0]
        second = sweep.loc[sweep["fold"] == 2].iloc[0]
        self.assertTrue(first["fold_accepted"])
        self.assertEqual(first["validation_class_coverage"], 3)
        self.assertIn(
            "validation_h6_Neutral=4",
            first["low_class_support_warnings"],
        )
        self.assertFalse(second["fold_accepted"])
        self.assertFalse(second["validation_independent_of_prior_test"])
        self.assertIn(
            "h6_validation_reuses_prior_test_period",
            second["rejection_reasons"],
        )

    def test_outer_lstm_epoch_selection_stays_inside_outer_training(self):
        frame = pd.DataFrame(
            {
                "time": pd.date_range("2016-01-01", periods=114, freq="MS"),
                "feature": np.linspace(0.0, 1.0, 114),
                "oni": np.sin(np.arange(114, dtype=np.float64)),
            }
        )
        fold = build_expanding_folds(
            114,
            min_train_months=72,
            validation_months=24,
            test_months=18,
            step_months=18,
        )[0]
        train_origins = fold_indices(fold, horizon=1, window=12)["train"]
        epoch_model = SimpleNamespace(
            loss_history=[
                {"epoch": 1.0, "validation_mse": 0.3},
                {"epoch": 2.0, "validation_mse": 0.1},
                {"epoch": 3.0, "validation_mse": 0.2},
            ]
        )
        with (
            patch(
                "src.ml.backtesting._fit_lstm",
                return_value=(
                    SimpleNamespace(model=epoch_model),
                    np.zeros(1),
                    np.zeros((114, 1)),
                ),
            ) as select_epochs,
            patch("src.ml.backtesting.train_lstm", return_value=object()) as refit,
            patch(
                "src.ml.backtesting._predict_oni",
                side_effect=lambda *args: np.zeros(len(args[3])),
            ),
        ):
            model, validation_predictions = _fit_outer_lstm(
                frame,
                ["feature"],
                "oni",
                train_origins,
                fold,
                horizon=1,
                config=LSTMConfig(epochs=3, window=12, hidden_size=2),
                seed=7,
            )

        inner_train = select_epochs.call_args.args[3]
        inner_validation = select_epochs.call_args.args[4]
        self.assertTrue(np.all(inner_train + 1 < inner_validation[0]))
        self.assertTrue(np.all(inner_validation + 1 < fold.train_end))
        self.assertIsNone(refit.call_args.args[1])
        self.assertEqual(refit.call_args.args[4], 2)
        self.assertEqual(model.selected_epochs, 2)
        self.assertEqual(len(validation_predictions), fold.validation_end - fold.train_end - 1)

    def test_oni_forecast_and_residual_plots_use_split_predictions(self):
        predictions = pd.DataFrame(
            [
                {
                    "fold": 1,
                    "horizon_months": horizon,
                    "split": split,
                    "target_time": pd.Timestamp("2024-01-01") + pd.DateOffset(
                        months=index
                    ),
                    "actual_oni": float(index) / 10,
                    "predicted_oni": float(index) / 12,
                    "residual_actual_minus_predicted": float(index) / 60,
                }
                for horizon in (1, 3, 6)
                for split in ("validation", "test")
                for index in range(2)
            ]
        )
        with tempfile.TemporaryDirectory() as temporary_dir:
            output = Path(temporary_dir)
            _plot_oni_forecasts(predictions, output)
            _plot_oni_residuals(predictions, output)
            self.assertTrue((output / "oni_forecast_comparison.png").exists())
            self.assertTrue((output / "oni_residuals.png").exists())

    def test_fold_class_diagnostics_include_missing_classes_and_percentages(self):
        rows = []
        for class_id, class_name, count in (
            (0, "La Nina", 2),
            (1, "Neutral", 1),
            (2, "El Nino", 0),
        ):
            rows.append(
                {
                    "fold": 1,
                    "split": "validation",
                    "horizon_months": 6,
                    "start_time": pd.Timestamp("2022-01-01"),
                    "end_time": pd.Timestamp("2023-12-01"),
                    "sample_count": 3,
                    "class_id": class_id,
                    "class_name": class_name,
                    "class_count": count,
                    "proportion": count / 3,
                    "class_missing": count == 0,
                    "purged_target_rows": 6,
                }
            )

        diagnostics = _fold_class_diagnostics(pd.DataFrame(rows))

        self.assertEqual(diagnostics["actual_class_coverage"].unique().tolist(), [2])
        self.assertEqual(
            diagnostics["missing_classes"].iloc[0],
            ["El Nino"],
        )
        self.assertAlmostEqual(
            diagnostics.loc[diagnostics["class_id"] == 0, "class_percentage"].iloc[0],
            100 * 2 / 3,
        )

    def test_confusion_matrix_writer_removes_only_stale_generated_matrices(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            output = Path(temporary_dir)
            directory = output / "backtesting" / "confusion_matrices"
            directory.mkdir(parents=True)
            stale = directory / "lightgbm_unweighted_h1m_fold2_test.csv"
            unrelated = directory / "notes.csv"
            stale.write_text("stale", encoding="utf-8")
            unrelated.write_text("keep", encoding="utf-8")

            _write_confusion_matrices(
                output,
                {
                    ("LightGBM", "unweighted", 1, 1, "test"): np.zeros(
                        (3, 3), dtype=np.int64
                    )
                },
            )

            self.assertFalse(stale.exists())
            self.assertTrue(unrelated.exists())
            self.assertTrue(
                (directory / "lightgbm_unweighted_h1m_fold1_test.csv").exists()
            )

    def test_fold_distribution_plot_accepts_fold_ids_read_from_csv(self):
        rows = [
            {
                "fold": "1",
                "split": "test",
                "horizon_months": horizon,
                "class_name": class_name,
                "class_count": count,
            }
            for horizon in (1, 3, 6)
            for class_name, count in (
                ("La Nina", 2),
                ("Neutral", 1),
                ("El Nino", 0),
            )
        ]
        with tempfile.TemporaryDirectory() as temporary_dir:
            _plot_fold_distribution(
                pd.DataFrame(rows),
                Path(temporary_dir),
            )
            self.assertTrue(
                (Path(temporary_dir) / "class_distribution_by_fold.png").exists()
            )

    def test_classification_metrics_keep_fixed_three_class_confusion_matrix(self):
        summary, report, confusion = classification_evaluation(
            np.array([1, 1, 1]),
            np.array([1, 2, 1]),
        )

        self.assertEqual(confusion.shape, (3, 3))
        self.assertEqual(summary["actual_class_counts"], {"0": 0, "1": 3, "2": 0})
        self.assertEqual(summary["predicted_class_counts"], {"0": 0, "1": 2, "2": 1})
        self.assertEqual(summary["missing_actual_classes"], ["La Nina", "El Nino"])
        self.assertEqual(len(report), 5)

    def test_model_selection_excludes_validation_after_earlier_test_periods(self):
        rows = []
        for fold in (1, 2):
            for model, first_fold_score, second_fold_score in (
                ("LightGBM", 0.7, 0.2),
                ("XGBoost", 0.6, 0.99),
            ):
                score = first_fold_score if fold == 1 else second_fold_score
                for split in ("validation", "test"):
                    rows.append(
                        {
                            "fold": fold,
                            "horizon_months": 1,
                            "model": model,
                            "imbalance_strategy": "unweighted",
                            "split": split,
                            "accuracy": score,
                            "balanced_accuracy": score,
                            "macro_precision": score,
                            "macro_recall": score,
                            "macro_f1": score,
                            "weighted_f1": score,
                            "log_loss": 0.8 if model == "LightGBM" else 0.2,
                            "multiclass_brier_score": (
                                0.7 if model == "LightGBM" else 0.25
                            ),
                            "top_label_ece_10_bins": 0.1,
                            "mean_top_label_confidence": 0.7,
                            "oni_rmse": 1.0,
                            "actual_count_0": 1,
                            "actual_count_1": 1,
                            "actual_count_2": 0,
                            "missing_actual_classes": '["El Nino"]',
                        }
                    )

        selection, _, _ = _select_models(pd.DataFrame(rows))

        selected = selection["selected_models"]["1"]
        self.assertIsNone(selected["model"])
        self.assertEqual(selected["selection_validation_fold"], 1)
        self.assertEqual(selected["validation_actual_class_coverage"], 2)
        self.assertEqual(selected["validation_missing_actual_classes"], ["El Nino"])
        self.assertEqual(selected["selection_status"], "insufficient_class_coverage")
        self.assertTrue(selected["selection_is_provisional"])
        self.assertFalse(selection["test_metrics_used_for_selection"])

    def test_model_selection_ranks_only_full_coverage_initial_validation(self):
        rows = []
        for fold, scores in (
            (1, {"LightGBM": 0.7, "XGBoost": 0.6}),
            (2, {"LightGBM": 0.2, "XGBoost": 0.99}),
        ):
            for model, score in scores.items():
                for split in ("validation", "test"):
                    rows.append(
                        {
                            "fold": fold,
                            "horizon_months": 1,
                            "model": model,
                            "imbalance_strategy": "unweighted",
                            "split": split,
                            "accuracy": score,
                            "balanced_accuracy": score,
                            "macro_precision": score,
                            "macro_recall": score,
                            "macro_f1": score,
                            "weighted_f1": score,
                            "log_loss": (
                                0.8 if model == "LightGBM" else 0.2
                            )
                            if split == "validation" and fold == 1
                            else (
                                0.1 if model == "LightGBM" else 0.9
                            ),
                            "multiclass_brier_score": (
                                0.7 if model == "LightGBM" else 0.25
                            ),
                            "top_label_ece_10_bins": 0.1,
                            "mean_top_label_confidence": 0.7,
                            "oni_rmse": 1.0,
                            "actual_count_0": 1,
                            "actual_count_1": 1,
                            "actual_count_2": 1,
                            "missing_actual_classes": "[]",
                        }
                    )

        selection, _, comparison = _select_models(pd.DataFrame(rows))

        selected = selection["selected_models"]["1"]
        self.assertEqual(selected["model"], "XGBoost")
        self.assertEqual(selected["selection_validation_fold"], 1)
        self.assertEqual(selected["validation_actual_class_coverage"], 3)
        self.assertEqual(selected["selection_status"], "provisional_candidate")
        self.assertAlmostEqual(selected["validation_log_loss"], 0.2)
        self.assertAlmostEqual(
            selected["validation_multiclass_brier_score"], 0.25
        )
        self.assertIn("validation_macro_precision_mean", comparison.columns)
        self.assertIn("validation_macro_recall_std", comparison.columns)

    def test_class_coverage_report_flags_missing_phase(self):
        distribution = pd.DataFrame(
            [
                {
                    "fold": 1,
                    "split": "validation",
                    "horizon_months": 1,
                    "start_time": "2021-01-01",
                    "end_time": "2022-05-01",
                    "sample_count": 3,
                    "post_window_sample_count": 3,
                    "class_id": class_id,
                    "class_name": class_name,
                    "class_count": count,
                    "proportion": count / 3,
                    "class_missing": count == 0,
                    "purged_target_rows": 1,
                }
                for class_id, class_name, count in (
                    (0, "La Nina", 2),
                    (1, "Neutral", 1),
                    (2, "El Nino", 0),
                )
            ]
        )

        report = _class_coverage_report(distribution)

        self.assertEqual(report["actual_class_coverage"].unique().tolist(), [2])
        self.assertEqual(
            report["coverage_status"].unique().tolist(),
            ["insufficient_class_coverage"],
        )
        self.assertEqual(
            report["missing_actual_classes"].unique().tolist(),
            ['["El Nino"]'],
        )

    def test_final_report_handles_abstained_global_selection(self):
        summary = {
            "total_samples": 114,
            "time_start": "2016-01-01",
            "time_end": "2025-06-01",
            "feature_count": 67,
            "folds": [
                {
                    "fold": 1,
                    "train_start": "2016-01-01",
                    "train_end": "2020-12-01",
                    "validation_start": "2021-01-01",
                    "validation_end": "2022-06-01",
                    "test_start": "2022-07-01",
                    "test_end": "2023-12-01",
                }
            ]
        }
        fold_metrics = pd.DataFrame(
            [
                {
                    "fold": 1,
                    "model": "LightGBM",
                    "imbalance_strategy": "unweighted",
                    "horizon_months": 1,
                    "split": split,
                    "missing_actual_classes": '["El Nino"]',
                }
                for split in ("validation", "test")
            ]
        )
        comparison = pd.DataFrame(
            [
                {
                    "horizon_months": 1,
                    "model": "LightGBM",
                    "imbalance_strategy": "unweighted",
                    "test_accuracy_mean": 0.5,
                    "test_balanced_accuracy_mean": 0.5,
                    "test_macro_f1_mean": 0.4,
                    "test_macro_f1_std": 0.1,
                    "test_weighted_f1_mean": 0.5,
                    "test_oni_rmse_mean": 1.0,
                    "test_oni_rmse_std": 0.2,
                }
            ]
        )
        selection = {
            "selected_models": {
                "1": {
                    "model": None,
                    "imbalance_strategy": None,
                    "selection_status": "insufficient_class_coverage",
                    "selection_validation_fold": 1,
                    "validation_macro_f1": None,
                    "validation_balanced_accuracy": None,
                    "validation_actual_class_coverage": 2,
                    "validation_missing_actual_classes": ["El Nino"],
                }
            }
        }

        with tempfile.TemporaryDirectory() as temporary_dir:
            path = Path(temporary_dir) / "report.md"
            validation_sweep = pd.DataFrame(
                [
                    {
                        "validation_months": 24,
                        "train_months": 72,
                        "horizon_months": 6,
                        "validation_sample_count": 18,
                        "class_0_count": 7,
                        "class_1_count": 4,
                        "class_2_count": 7,
                        "coverage_status": "complete_class_coverage",
                        "is_configured_window": True,
                    }
                ]
            )
            _write_final_report(
                path,
                summary,
                fold_metrics,
                comparison,
                selection,
                validation_sweep,
                Path(temporary_dir) / "models",
            )
            report = path.read_text(encoding="utf-8")

        self.assertIn("not selected", report)
        self.assertIn("insufficient_class_coverage", report)
        self.assertIn("2/3", report)


if __name__ == "__main__":
    unittest.main()
