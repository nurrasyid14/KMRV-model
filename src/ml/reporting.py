"""Persist backtesting tables, selected-model metadata, and visualizations."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.ml.temporal import PHASE_NAMES


def _write_confusion_matrices(
    output_dir: Path,
    matrices: dict[tuple[str, str, int, int, str], np.ndarray],
) -> None:
    directory = output_dir / "backtesting" / "confusion_matrices"
    directory.mkdir(parents=True, exist_ok=True)
    class_names = [PHASE_NAMES[class_id] for class_id in range(3)]
    generated_names = {
        f"{model.lower()}_{strategy}_h{horizon}m_fold{fold}_{split}.csv"
        for model, strategy, horizon, fold, split in matrices
    }
    generated_pattern = re.compile(
        r"(lightgbm|xgboost)_(unweighted|balanced)_h[1-6]m_fold\d+_(validation|test)\.csv"
    )
    for existing_path in directory.iterdir():
        if (
            existing_path.is_file()
            and generated_pattern.fullmatch(existing_path.name)
            and existing_path.name not in generated_names
        ):
            existing_path.unlink()
    for (model, strategy, horizon, fold, split), matrix in matrices.items():
        pd.DataFrame(matrix, index=class_names, columns=class_names).to_csv(
            directory
            / f"{model.lower()}_{strategy}_h{horizon}m_fold{fold}_{split}.csv",
            index_label="actual",
        )


def _plot_class_distribution(frame: pd.DataFrame, output_dir: Path) -> None:
    yearly = frame.assign(year=frame["time"].dt.year)
    figure, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    for axis, horizon in zip(axes, (1, 3, 6)):
        target = f"target_phase_lead_{horizon}m"
        counts = pd.crosstab(yearly["year"], yearly[target]).reindex(
            columns=[0, 1, 2],
            fill_value=0,
        )
        counts.columns = [PHASE_NAMES[class_id] for class_id in range(3)]
        counts.plot(kind="bar", stacked=True, ax=axis, color=["#377eb8", "#999999", "#e41a1c"])
        axis.set_title(f"ENSO phase labels by year — {horizon}-month lead")
        axis.set_ylabel("Samples")
        axis.legend(title="Phase", ncol=3, loc="upper left")
    axes[-1].set_xlabel("Year")
    figure.tight_layout()
    figure.savefig(output_dir / "class_distribution.png", dpi=160)
    plt.close(figure)


def _plot_fold_distribution(
    split_distribution: pd.DataFrame,
    output_dir: Path,
) -> None:
    fold_numbers = pd.to_numeric(split_distribution["fold"], errors="coerce")
    folds = split_distribution.loc[
        split_distribution["split"].isin(["train", "validation", "test"])
        & fold_numbers.notna()
    ].copy()
    folds["fold"] = fold_numbers.loc[folds.index].astype(int)
    folds = folds.loc[folds["split"] == "test"]
    figure, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    for axis, horizon in zip(axes, (1, 3, 6)):
        subset = folds.loc[folds["horizon_months"] == horizon]
        pivot = subset.pivot_table(
            index="fold",
            columns="class_name",
            values="class_count",
            aggfunc="first",
            fill_value=0,
        ).reindex(columns=[PHASE_NAMES[class_id] for class_id in range(3)], fill_value=0)
        pivot.plot(kind="bar", stacked=True, ax=axis, color=["#377eb8", "#999999", "#e41a1c"])
        axis.set_title(f"Purged test class distribution — {horizon}-month lead")
        axis.set_ylabel("Samples")
        axis.legend(title="Phase", ncol=3, loc="upper left")
    axes[-1].set_xlabel("Fold")
    figure.tight_layout()
    figure.savefig(output_dir / "class_distribution_by_fold.png", dpi=160)
    plt.close(figure)


def _plot_confusion_comparison(
    output_dir: Path,
    matrices: dict[tuple[str, str, int, int, str], np.ndarray],
    model_family: str,
) -> None:
    strategies = ("unweighted", "balanced")
    figure, axes = plt.subplots(2, 3, figsize=(13, 8))
    for column, horizon in enumerate((1, 3, 6)):
        for row, strategy in enumerate(strategies):
            matrix = sum(
                (
                    value
                    for (model, weight, current_horizon, _, split), value in matrices.items()
                    if model == model_family
                    and weight == strategy
                    and current_horizon == horizon
                    and split == "test"
                ),
                start=np.zeros((3, 3), dtype=np.int64),
            )
            axis = axes[row, column]
            image = axis.imshow(matrix, cmap="Blues")
            axis.set_title(f"{strategy}, {horizon}-month lead")
            axis.set_xticks(range(3), [PHASE_NAMES[index] for index in range(3)], rotation=30)
            axis.set_yticks(range(3), [PHASE_NAMES[index] for index in range(3)])
            axis.set_xlabel("Predicted")
            axis.set_ylabel("Actual")
            threshold = matrix.max() / 2 if matrix.size else 0
            for actual in range(3):
                for predicted in range(3):
                    axis.text(
                        predicted,
                        actual,
                        str(int(matrix[actual, predicted])),
                        ha="center",
                        va="center",
                        color="white" if matrix[actual, predicted] > threshold else "black",
                    )
            figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.suptitle(f"{model_family} pooled test confusion matrices by horizon")
    figure.tight_layout()
    figure.savefig(
        output_dir / "visualizations" / f"confusion_matrix_{model_family.lower()}.png",
        dpi=160,
    )
    plt.close(figure)


def _plot_metric_comparison(
    comparison: pd.DataFrame,
    metric: str,
    output_path: Path,
    title: str,
) -> None:
    variants = [
        ("LightGBM", "unweighted", "LightGBM — unweighted"),
        ("LightGBM", "balanced", "LightGBM — class-weighted"),
        ("XGBoost", "unweighted", "XGBoost — unweighted"),
        ("XGBoost", "balanced", "XGBoost — sample-weighted"),
    ]
    figure, axis = plt.subplots(figsize=(11, 6))
    positions = np.arange(3)
    width = 0.19
    for index, (model, strategy, label) in enumerate(variants):
        subset = comparison.loc[
            (comparison["model"] == model)
            & (comparison["imbalance_strategy"] == strategy)
        ].set_index("horizon_months")
        means = [subset.loc[horizon, f"test_{metric}_mean"] for horizon in (1, 3, 6)]
        stds = [
            subset.loc[horizon, f"test_{metric}_std"]
            if not pd.isna(subset.loc[horizon, f"test_{metric}_std"])
            else 0.0
            for horizon in (1, 3, 6)
        ]
        axis.bar(
            positions + (index - 1.5) * width,
            means,
            width,
            yerr=stds,
            capsize=3,
            label=label,
        )
    axis.set_xticks(positions, ["1 month", "3 months", "6 months"])
    axis.set_ylabel(metric.replace("_", " ").title())
    axis.set_title(title)
    if metric != "oni_rmse":
        axis.set_ylim(0, 1)
    axis.grid(axis="y", alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def _plot_oni_forecasts(predictions: pd.DataFrame, output_dir: Path) -> None:
    if predictions.empty:
        return
    unique_predictions = predictions.drop_duplicates(
        ["fold", "horizon_months", "split", "target_time"]
    )
    figure, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    for axis, horizon in zip(axes, (1, 3, 6)):
        subset = unique_predictions.loc[
            unique_predictions["horizon_months"] == horizon
        ].sort_values("target_time")
        if subset.empty:
            axis.set_visible(False)
            continue
        for split, split_subset in subset.groupby("split", sort=False):
            axis.plot(
                split_subset["target_time"],
                split_subset["actual_oni"],
                marker="o",
                linewidth=1.5,
                label=f"Actual ONI ({split})",
            )
            axis.plot(
                split_subset["target_time"],
                split_subset["predicted_oni"],
                marker="x",
                linewidth=1.5,
                label=f"Predicted ONI ({split})",
            )
        axis.axhline(0.5, color="red", linestyle="--", alpha=0.4)
        axis.axhline(-0.5, color="blue", linestyle="--", alpha=0.4)
        axis.set_title(f"{horizon}-month ONI forecasts by split")
        axis.set_ylabel("ONI anomaly")
        axis.legend()
        axis.grid(alpha=0.2)
    axes[-1].set_xlabel("Target month")
    figure.tight_layout()
    figure.savefig(output_dir / "oni_forecast_comparison.png", dpi=160)
    plt.close(figure)


def _plot_oni_residuals(predictions: pd.DataFrame, output_dir: Path) -> None:
    if predictions.empty:
        return
    figure, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    for axis, horizon in zip(axes, (1, 3, 6)):
        subset = predictions.loc[
            predictions["horizon_months"] == horizon
        ].sort_values("target_time")
        if subset.empty:
            axis.set_visible(False)
            continue
        for split, split_subset in subset.groupby("split", sort=False):
            axis.scatter(
                split_subset["target_time"],
                split_subset["residual_actual_minus_predicted"],
                label=split,
                alpha=0.8,
            )
        axis.axhline(0.0, color="black", linewidth=1, linestyle="--")
        axis.set_title(f"{horizon}-month ONI residuals (actual - predicted)")
        axis.set_ylabel("Residual")
        axis.grid(alpha=0.2)
        axis.legend()
    axes[-1].set_xlabel("Target month")
    figure.tight_layout()
    figure.savefig(output_dir / "oni_residuals.png", dpi=160)
    plt.close(figure)


def _plot_fold_performance(fold_metrics: pd.DataFrame, output_dir: Path) -> None:
    test = fold_metrics.loc[fold_metrics["split"] == "test"]
    figure, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    for axis, horizon in zip(axes, (1, 3, 6)):
        subset = test.loc[test["horizon_months"] == horizon]
        for (model, strategy), group in subset.groupby(["model", "imbalance_strategy"]):
            group = group.sort_values("fold")
            axis.plot(
                group["fold"],
                group["macro_f1"],
                marker="o",
                label=f"{model} — {strategy}",
            )
        axis.set_title(f"Test macro-F1 by fold — {horizon}-month lead")
        axis.set_ylabel("Macro-F1")
        axis.set_ylim(0, 1)
        axis.grid(alpha=0.2)
        axis.legend()
    axes[-1].set_xlabel("Fold")
    figure.tight_layout()
    figure.savefig(output_dir / "fold_performance.png", dpi=160)
    plt.close(figure)


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No results available._"
    display = frame.copy().fillna("—")
    headers = [str(column) for column in display.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in display.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def _fold_class_diagnostics(split_distribution: pd.DataFrame) -> pd.DataFrame:
    rows = split_distribution.copy()
    fold_keys = rows["fold"].astype(str)
    rows = rows.loc[
        fold_keys.str.fullmatch(r"\d+")
        & rows["split"].isin(
            ("train", "classifier_train_oof", "validation", "test")
        )
    ].copy()
    rows["fold"] = rows["fold"].astype(int)
    group_columns = ["fold", "split", "horizon_months"]
    coverage_rows = []
    for keys, group in rows.groupby(group_columns, sort=True):
        missing = group.loc[group["class_count"] == 0, "class_name"].tolist()
        coverage_rows.append(
            {
                **dict(zip(group_columns, keys)),
                "actual_class_coverage": int((group["class_count"] > 0).sum()),
                "missing_classes": missing,
                "coverage_status": (
                    "complete_class_coverage"
                    if not missing
                    else "insufficient_class_coverage"
                ),
            }
        )
    coverage = pd.DataFrame(coverage_rows)
    rows = rows.merge(coverage, on=group_columns, how="left")
    rows["class_percentage"] = 100.0 * rows["proportion"]
    return rows[
        [
            "fold",
            "split",
            "horizon_months",
            "start_time",
            "end_time",
            "sample_count",
            "class_id",
            "class_name",
            "class_count",
            "class_percentage",
            "class_missing",
            "missing_classes",
            "actual_class_coverage",
            "coverage_status",
            "purged_target_rows",
        ]
    ].sort_values(group_columns + ["class_id"]).reset_index(drop=True)


def _write_final_report(
    path: Path,
    summary: dict[str, object],
    fold_metrics: pd.DataFrame,
    comparison: pd.DataFrame,
    selection: dict[str, Any],
    validation_sweep: pd.DataFrame,
    model_dir: Path,
    regression_metrics: pd.DataFrame | None = None,
    fold_sweep: pd.DataFrame | None = None,
) -> None:
    regression_metrics = (
        pd.DataFrame() if regression_metrics is None else regression_metrics
    )
    fold_sweep = pd.DataFrame() if fold_sweep is None else fold_sweep
    test_summary_columns = [
        "horizon_months",
        "model",
        "imbalance_strategy",
        "test_accuracy_mean",
        "test_balanced_accuracy_mean",
        "test_log_loss_mean",
        "test_multiclass_brier_score_mean",
        "test_top_label_ece_10_bins_mean",
        "test_macro_f1_mean",
        "test_macro_f1_std",
        "test_weighted_f1_mean",
        "test_oni_rmse_mean",
        "test_oni_rmse_std",
    ]
    test_summary_columns = [
        column for column in test_summary_columns if column in comparison.columns
    ]
    test_summary = comparison.loc[
        comparison["test_macro_f1_mean"].notna(),
        test_summary_columns,
    ].copy()
    numeric_columns = test_summary.select_dtypes(include="number").columns
    test_summary[numeric_columns] = test_summary[numeric_columns].round(3)
    validation_only = fold_metrics.loc[fold_metrics["split"] == "validation"]
    missing_validation = validation_only.loc[
        validation_only["missing_actual_classes"] != "[]",
        ["fold", "model", "imbalance_strategy", "horizon_months", "missing_actual_classes"],
    ].drop_duplicates()
    missing_test = fold_metrics.loc[
        (fold_metrics["split"] == "test")
        & (fold_metrics["missing_actual_classes"] != "[]"),
        ["fold", "model", "imbalance_strategy", "horizon_months", "missing_actual_classes"],
    ].drop_duplicates()
    selection_table = pd.DataFrame(
        [
            {
                "horizon_months": horizon,
                "model": choice["model"] or "not selected",
                "imbalance_strategy": choice["imbalance_strategy"] or "—",
                "selection_status": choice["selection_status"],
                "selection_validation_fold": choice["selection_validation_fold"],
                "validation_macro_f1": (
                    None
                    if choice["validation_macro_f1"] is None
                    else round(choice["validation_macro_f1"], 3)
                ),
                "validation_log_loss": (
                    None
                    if choice.get("validation_log_loss") is None
                    else round(choice["validation_log_loss"], 3)
                ),
                "validation_brier_score": (
                    None
                    if choice.get("validation_multiclass_brier_score") is None
                    else round(
                        choice["validation_multiclass_brier_score"], 3
                    )
                ),
                "validation_top_label_ece": (
                    None
                    if choice.get("validation_top_label_ece_10_bins") is None
                    else round(choice["validation_top_label_ece_10_bins"], 3)
                ),
                "validation_balanced_accuracy": (
                    None
                    if choice["validation_balanced_accuracy"] is None
                    else round(choice["validation_balanced_accuracy"], 3)
                ),
                "actual_class_coverage": (
                    f"{choice['validation_actual_class_coverage']}/3"
                ),
                "missing_actual_classes": ", ".join(
                    choice["validation_missing_actual_classes"]
                )
                or "none",
                "saved_model_fold": choice.get("saved_model_fold"),
            }
            for horizon, choice in selection["selected_models"].items()
        ]
    )

    fold_lines = []
    for fold in summary["folds"]:
        fold_lines.append(
            f"- Fold {fold['fold']}: train {fold['train_start']}–{fold['train_end']}; "
            f"validation {fold['validation_start']}–{fold['validation_end']}; "
            f"test {fold['test_start']}–{fold['test_end']}."
        )
    validation_sweep_columns = [
        "validation_months",
        "train_months",
        "horizon_months",
        "validation_sample_count",
        "class_0_count",
        "class_1_count",
        "class_2_count",
        "coverage_status",
        "is_configured_window",
    ]
    validation_sweep_table = validation_sweep[validation_sweep_columns].copy()
    validation_sweep_table = validation_sweep_table.rename(
        columns={
            "class_0_count": "la_nina_count",
            "class_1_count": "neutral_count",
            "class_2_count": "el_nino_count",
        }
    )
    regression_table_columns = [
        column
        for column in (
            "fold",
            "horizon_months",
            "split",
            "sample_count",
            "oni_mae",
            "oni_rmse",
            "oni_r2",
            "actual_oni_std",
            "predicted_oni_std",
            "mean_residual_actual_minus_predicted",
        )
        if column in regression_metrics.columns
    ]
    regression_table = regression_metrics[regression_table_columns].copy()
    if not regression_table.empty:
        numeric_columns = regression_table.select_dtypes(include="number").columns
        regression_table[numeric_columns] = regression_table[numeric_columns].round(3)
    fold_sweep_columns = [
        column
        for column in (
            "min_train_months",
            "validation_months",
            "test_months",
            "fold",
            "horizon_months",
            "train_sample_count",
            "validation_sample_count",
            "test_sample_count",
            "train_class_coverage",
            "validation_class_coverage",
            "test_class_coverage",
            "purge_ok",
            "input_window_ok",
            "validation_independent_of_prior_test",
            "fold_accepted",
            "rejection_reasons",
            "low_class_support_warnings",
        )
        if column in fold_sweep.columns
    ]
    fold_sweep_table = fold_sweep[fold_sweep_columns].copy()
    report = f"""# ENSO temporal backtesting report

## Pipeline flow

```text
monthly feature master (time-sorted)
  -> horizon-specific target-time purge
  -> expanding chronological train / validation / test folds
  -> train-only scaling + 12-month causal LSTM windows
  -> inner expanding-window out-of-fold LSTM forecasts for classifier training
  -> identical tabular features for LightGBM and XGBoost
  -> unweighted and training-only class-weighted variants
  -> fixed-label classification and separate ONI regression evaluation
  -> audit tables, fold comparisons, plots, and validation-only model selection
```

## Data audit

- Samples: **{summary['total_samples']}** monthly rows.
- Coverage: **{summary['time_start']}** through **{summary['time_end']}**.
- Numeric input features: **{summary['feature_count']}**.
- Labels: 0 = La Niña, 1 = Neutral, 2 = El Niño.
- Target alignment was checked against ONI shifted by each forecast horizon.
- Lags and rolling means were checked against trailing historical values.
- Existing fixed split files were chronological, but the prior runner reset the 12-month window at each split and discarded 11 rows per split. Its 18-row test split therefore produced only 7 evaluation origins.
- The prior fixed split also retained horizon targets that crossed train/validation boundaries. This backtest purges the final `horizon` origins from train and validation before the next period.

Existing train/validation/test and whole-dataset class counts are in `data_audit/class_distribution.csv` and `data_audit/split_distribution.csv`. The test-period omissions below are intentional observations, not resampling:

## Expanding-window folds

{chr(10).join(fold_lines)}

The configured evaluation uses one terminal fold: a 72-month initial training period, a 24-month validation period, and the final 18-month test period. A single fold is intentional: it preserves a useful training history and leaves a longer validation period with complete class coverage, without manufacturing short test folds. The 12-month LSTM context may use observed feature history before a split; target labels are purged at train/validation boundaries.

The earlier 60/18/18 layout produced two folds, but its first validation omitted El Niño and the second validation reused origins previously reported as the first test. More folds would require shorter periods; a 12-month validation leaves only six usable origins at horizon 6 after purge, so that design was not adopted.

The chronological validation-duration sweep is anchored to the same untouched final test interval. It exposes the trade-off between OOF training volume and validation support:

{_markdown_table(validation_sweep_table)}

## Fold feasibility sweep

The chronological feasibility grid checks candidate validation/test lengths against all horizons, class coverage, target purge, and the 12-month input context. It does not create extra training runs or select a model. A candidate is rejected when any required split lacks a class or a temporal check fails. Low class counts are separately flagged and should not be treated as reliable coverage.

{_markdown_table(fold_sweep_table)}

## Model selection (validation only)

{_markdown_table(selection_table)}

Selection requires actual coverage of all three classes for the horizon and uses validation metrics only; the fixed final test period is never used for selection. Candidate ranking prioritizes multiclass log loss and Brier score; macro-F1 and balanced accuracy are tie-breakers. Top-label ECE is diagnostic only. These metrics evaluate the raw classifier probabilities; they do not calibrate them. The configured 24-month validation interval has full coverage at all horizons, but horizon 6 has only 18 validation origins and four Neutral examples. Validation also controls tree-classifier early stopping, so the resulting candidate ranking is provisional rather than an independent estimate. LSTM epoch selection uses a separate internal chronological segment within outer training.

## Selected-model final holdout evaluation

{_markdown_table(test_summary)}

The test period is scored only after validation-based selection. Test metrics are reported only for the selected classifier configuration per horizon; they are final holdout results, not selection evidence. The ONI model is shared by classifier variants and is evaluated separately from phase classification. Log loss and Brier score are proper scoring rules; ECE is a small-sample diagnostic and should not be treated as a stable calibration estimate.

## ONI regression diagnostics

Regression is evaluated independently of the phase classifier. The terminal test rows below are the final holdout evaluation and were not used for model selection. Actual/predicted values and residuals are exported per origin and horizon; plots include both validation and final holdout periods.

{_markdown_table(regression_table)}

### Validation periods with absent actual classes

{_markdown_table(missing_validation)}

### Test periods with absent actual classes

{_markdown_table(missing_test)}

Confusion matrices always use the fixed order `[0, 1, 2]`. A score calculated on a period missing one or more classes is not evidence that the model recognizes those absent classes. The per-class reports and actual/predicted counts should be read alongside aggregate metrics.

## Imbalance analysis

Both unweighted and balanced variants are reported. Class weights are computed exclusively from the classifier's out-of-fold training labels; validation and test distributions are left unchanged. No random oversampling or SMOTE is used.

## Limitations

- The record contains only 114 monthly samples and supports only one terminal 18-month test fold under the configured minimum training and validation durations. The test period itself lacks at least one class at some horizons.
- Horizon-specific purge and causal out-of-fold stacking reduce the effective classifier training set. Fold-level reports include the actual sample counts.
- The 24-month validation interval has 23, 21, and 18 usable origins for horizons 1, 3, and 6. Its per-class support and the single validation period make selection noisy, especially at the six-month lead.
- There are no independent fold repetitions from which to estimate meaningful between-period variability. A longer historical record is needed for multiple independent validation and test periods.
- This experiment does not establish operational ENSO skill. Broader hindcast records and independently sourced features are needed for stronger claims.
- No synthetic samples were added and no class distributions were rearranged.

## Output locations

- Audit: `data_audit/`
- Fold metrics, reports, matrices, and predictions: `backtesting/`
- Classifier comparison and selection: `model_comparison/`
- Plots: `visualizations/`
- Selected fold checkpoints and metadata: `{model_dir.resolve()}` (only saved when the validation coverage gate passes)
"""
    path.write_text(report, encoding="utf-8")


def write_backtest_reports(
    reports_dir: Path,
    model_dir: Path,
    frame: pd.DataFrame,
    summary: dict[str, object],
    folds: list[Any],
    class_distribution: pd.DataFrame,
    split_distribution: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    classification_reports: pd.DataFrame,
    confusion_matrices: dict[tuple[str, str, int, int, str], np.ndarray],
    test_predictions: pd.DataFrame,
    model_comparison: pd.DataFrame,
    horizon_comparison: pd.DataFrame,
    selection: dict[str, Any],
    validation_sweep: pd.DataFrame,
    horizons: tuple[int, ...],
    window: int,
    epochs: int,
    regression_metrics: pd.DataFrame | None = None,
    regression_predictions: pd.DataFrame | None = None,
    fold_sweep: pd.DataFrame | None = None,
) -> dict[str, object]:
    data_audit_dir = reports_dir / "data_audit"
    backtesting_dir = reports_dir / "backtesting"
    comparison_dir = reports_dir / "model_comparison"
    visualization_dir = reports_dir / "visualizations"
    for directory in (
        data_audit_dir,
        backtesting_dir / "confusion_matrices",
        comparison_dir,
        visualization_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    class_distribution.to_csv(data_audit_dir / "class_distribution.csv", index=False)
    split_distribution.to_csv(data_audit_dir / "split_distribution.csv", index=False)
    fold_class_diagnostics = _fold_class_diagnostics(split_distribution)
    fold_class_diagnostics.to_csv(
        backtesting_dir / "class_distribution_by_fold.csv",
        index=False,
    )
    (backtesting_dir / "class_distribution_by_fold.json").write_text(
        json.dumps(
            json.loads(
                fold_class_diagnostics.to_json(
                    orient="records",
                    date_format="iso",
                    indent=2,
                )
            ),
            indent=2,
        ),
        encoding="utf-8",
    )
    validation_sweep.to_csv(
        data_audit_dir / "validation_window_sweep.csv",
        index=False,
    )
    (data_audit_dir / "validation_window_sweep.json").write_text(
        json.dumps(
            json.loads(
                validation_sweep.to_json(
                    orient="records",
                    date_format="iso",
                    indent=2,
                )
            ),
            indent=2,
        ),
        encoding="utf-8",
    )
    (data_audit_dir / "dataset_summary.json").write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )
    fold_metrics.to_csv(backtesting_dir / "fold_metrics.csv", index=False)
    classification_reports.to_csv(
        backtesting_dir / "classification_reports.csv",
        index=False,
    )
    test_predictions.to_csv(backtesting_dir / "test_predictions.csv", index=False)
    if regression_metrics is not None:
        regression_metrics.to_csv(
            backtesting_dir / "regression_metrics.csv",
            index=False,
        )
    if regression_predictions is not None:
        regression_predictions.to_csv(
            backtesting_dir / "regression_predictions.csv",
            index=False,
        )
        regression_predictions.to_json(
            backtesting_dir / "regression_predictions.json",
            orient="records",
            date_format="iso",
            indent=2,
        )
    if fold_sweep is not None:
        fold_sweep.to_csv(
            data_audit_dir / "fold_feasibility_sweep.csv",
            index=False,
        )
        fold_sweep.to_json(
            data_audit_dir / "fold_feasibility_sweep.json",
            orient="records",
            date_format="iso",
            indent=2,
        )
    _write_confusion_matrices(reports_dir, confusion_matrices)
    model_comparison.to_csv(
        comparison_dir / "lightgbm_vs_xgboost.csv",
        index=False,
    )
    horizon_comparison.to_csv(comparison_dir / "horizon_comparison.csv", index=False)
    (comparison_dir / "model_selection.json").write_text(
        json.dumps(selection, indent=2, default=str),
        encoding="utf-8",
    )

    _plot_class_distribution(frame, visualization_dir)
    _plot_fold_distribution(split_distribution, visualization_dir)
    _plot_confusion_comparison(reports_dir, confusion_matrices, "LightGBM")
    _plot_confusion_comparison(reports_dir, confusion_matrices, "XGBoost")
    _plot_metric_comparison(
        model_comparison,
        "macro_f1",
        visualization_dir / "macro_f1_comparison.png",
        "Test macro-F1 by horizon (mean ± fold standard deviation)",
    )
    _plot_metric_comparison(
        model_comparison,
        "balanced_accuracy",
        visualization_dir / "balanced_accuracy_comparison.png",
        "Test balanced accuracy by horizon (mean ± fold standard deviation)",
    )
    _plot_metric_comparison(
        model_comparison,
        "oni_rmse",
        visualization_dir / "oni_rmse_comparison.png",
        "Shared LSTM ONI RMSE by horizon (mean ± fold standard deviation)",
    )
    if regression_predictions is not None:
        _plot_oni_forecasts(regression_predictions, visualization_dir)
        _plot_oni_residuals(regression_predictions, visualization_dir)
    _plot_fold_performance(fold_metrics, visualization_dir)
    _write_final_report(
        reports_dir / "final_report.md",
        summary,
        fold_metrics,
        model_comparison,
        selection,
        validation_sweep,
        model_dir,
        regression_metrics,
        fold_sweep,
    )
    return {
        "summary": summary,
        "folds": len(folds),
        "horizons": list(horizons),
        "model_selection": selection["selected_models"],
        "reports_directory": str(reports_dir.resolve()),
        "selected_model_directory": str(model_dir.resolve()),
        "window_months": window,
        "lstm_epochs": epochs,
    }
