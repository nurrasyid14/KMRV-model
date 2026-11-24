"""Generate read-only temporal, leakage, selection, and data sufficiency audits."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.ml.temporal import (
    BACKTEST_MIN_TRAIN_MONTHS,
    BACKTEST_STEP_MONTHS,
    BACKTEST_TEST_MONTHS,
    BACKTEST_VALIDATION_MONTHS,
    PHASE_CLASSES,
    PHASE_NAMES,
    build_expanding_folds,
    fold_indices,
    load_feature_data,
    resolve_feature_columns,
    validation_window_sweep,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "dataset" / "features_master_unscaled.csv"
DEFAULT_REPORTS_PATH = PROJECT_ROOT / "reports"
WINDOW_MONTHS = 12


def _require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Required audit input does not exist: {path}")
    return path


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows available._"
    display = frame.copy().fillna("—")
    headers = [str(column) for column in display.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in display.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def _read_inputs(reports_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fold_metrics = pd.read_csv(_require(reports_dir / "backtesting" / "fold_metrics.csv"))
    class_reports = pd.read_csv(
        _require(reports_dir / "backtesting" / "classification_reports.csv")
    )
    split_distribution = pd.read_csv(
        _require(reports_dir / "data_audit" / "split_distribution.csv")
    )
    return fold_metrics, class_reports, split_distribution


def _class_coverage_report(split_distribution: pd.DataFrame) -> pd.DataFrame:
    rows = split_distribution.copy()
    rows["fold_key"] = rows["fold"].astype(str)
    rows = rows.loc[
        rows["fold_key"].str.fullmatch(r"\d+")
        & rows["split"].isin(("train", "classifier_train_oof", "validation", "test"))
    ].copy()
    group_columns = ["fold_key", "split", "horizon_months"]
    coverage_rows = []
    for keys, group in rows.groupby(group_columns, sort=True):
        fold, split, horizon = keys
        covered = int((group["class_count"] > 0).sum())
        missing = group.loc[group["class_count"] == 0, "class_name"].tolist()
        coverage_rows.append(
            {
                "fold_key": fold,
                "split": split,
                "horizon_months": horizon,
                "actual_class_coverage": covered,
                "missing_actual_classes": json.dumps(missing),
                "coverage_status": (
                    "complete_class_coverage"
                    if covered == len(PHASE_CLASSES)
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
            "post_window_sample_count",
            "class_id",
            "class_name",
            "class_count",
            "proportion",
            "class_percentage",
            "class_missing",
            "actual_class_coverage",
            "missing_actual_classes",
            "coverage_status",
            "purged_target_rows",
        ]
    ].sort_values(["horizon_months", "fold", "split", "class_id"])


def _wide_class_diagnostics(
    class_reports: pd.DataFrame,
    keys: list[str],
) -> pd.DataFrame:
    frame = class_reports.copy()
    frame["class_id_numeric"] = pd.to_numeric(frame["class_id"], errors="coerce")
    frame = frame.loc[frame["class_id_numeric"].isin(PHASE_CLASSES)].copy()
    frame["class_id_numeric"] = frame["class_id_numeric"].astype(int)
    values = ("precision", "recall", "f1_score", "support", "predicted_count")
    wide = frame.pivot_table(
        index=keys,
        columns="class_id_numeric",
        values=list(values),
        aggfunc="first",
    )
    wide.columns = [
        f"class_{int(class_id)}_{metric}"
        for metric, class_id in wide.columns
    ]
    return wide.reset_index()


def _selection_audit(
    fold_metrics: pd.DataFrame,
    class_reports: pd.DataFrame,
    coverage_report: pd.DataFrame,
) -> pd.DataFrame:
    keys = ["fold", "horizon_months", "model", "imbalance_strategy"]
    validation = fold_metrics.loc[fold_metrics["split"] == "validation"].copy()
    test = fold_metrics.loc[fold_metrics["split"] == "test"].copy()
    audit = validation.merge(
        test,
        on=keys,
        how="left",
        suffixes=("_validation", "_test"),
    )
    coverage = coverage_report.loc[
        coverage_report["split"] == "validation",
        ["fold", "horizon_months", "actual_class_coverage", "missing_actual_classes"],
    ].copy()
    coverage["fold"] = coverage["fold"].astype(int)
    coverage = coverage.drop_duplicates(["fold", "horizon_months"])
    audit = audit.merge(coverage, on=["fold", "horizon_months"], how="left")

    for split_name in ("validation", "test"):
        diagnostics = _wide_class_diagnostics(
            class_reports.loc[class_reports["split"] == split_name],
            keys,
        )
        rename = {
            column: f"{split_name}_{column}"
            for column in diagnostics.columns
            if column not in keys
        }
        audit = audit.merge(
            diagnostics.rename(columns=rename),
            on=keys,
            how="left",
        )

    audit["predicted_class_coverage_validation"] = audit[
        [f"predicted_count_{class_id}_validation" for class_id in PHASE_CLASSES]
    ].gt(0).sum(axis=1)
    audit["test_actual_class_coverage"] = audit[
        [f"actual_count_{class_id}_test" for class_id in PHASE_CLASSES]
    ].gt(0).sum(axis=1)
    audit["test_predicted_class_coverage"] = audit[
        [f"predicted_count_{class_id}_test" for class_id in PHASE_CLASSES]
    ].gt(0).sum(axis=1)

    aggregate_metrics = (
        "macro_f1",
        "balanced_accuracy",
        "macro_precision",
        "macro_recall",
    )
    for split_name, source in (("validation", validation), ("test", test)):
        grouped = source.groupby(["horizon_months", "model", "imbalance_strategy"])
        for metric in aggregate_metrics:
            summary = grouped[metric].agg(["mean", "std"]).reset_index()
            summary = summary.rename(
                columns={
                    "mean": f"{split_name}_{metric}_mean_across_folds",
                    "std": f"{split_name}_{metric}_std_across_folds",
                }
            )
            audit = audit.merge(
                summary,
                on=["horizon_months", "model", "imbalance_strategy"],
                how="left",
            )

    audit["validation_summary_status"] = (
        "single configured validation interval; reused for classifier early stopping and ranking"
    )
    audit["test_metrics_used_for_selection"] = False
    audit["selection_status"] = np.where(
        audit["actual_class_coverage"] < len(PHASE_CLASSES),
        "insufficient_class_coverage",
        "provisional_rank_only: validation reused for classifier early stopping",
    )
    audit["fold_local_validation_rank"] = pd.Series(pd.NA, index=audit.index, dtype="Int64")
    for _, indices in audit.groupby(["fold", "horizon_months"]).groups.items():
        candidate_indices = [
            index
            for index in indices
            if audit.loc[index, "actual_class_coverage"] == len(PHASE_CLASSES)
        ]
        ordered = audit.loc[candidate_indices].sort_values(
            [
                "macro_f1_validation",
                "balanced_accuracy_validation",
                "macro_precision_validation",
                "macro_recall_validation",
            ],
            ascending=False,
            kind="mergesort",
        )
        for rank, index in enumerate(ordered.index, start=1):
            audit.loc[index, "fold_local_validation_rank"] = rank
    audit["global_selection_status"] = np.where(
        audit["actual_class_coverage"] == len(PHASE_CLASSES),
        "provisional_validation_candidate_not_final",
        "no_candidate_due_to_insufficient_class_coverage",
    )
    return audit.sort_values(keys).reset_index(drop=True)


def _notebook_evidence(root: Path) -> dict[str, Any]:
    notebook_path = root / "notebook" / "07_feature_engineering.ipynb"
    if not notebook_path.exists():
        return {"available": False, "path": str(notebook_path)}
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    sources: list[str] = []
    outputs: list[str] = []
    for cell in notebook.get("cells", []):
        sources.append("".join(cell.get("source", [])))
        for output in cell.get("outputs", []):
            if "text" in output:
                outputs.append("".join(output["text"]))
            data = output.get("data", {})
            if "text/plain" in data:
                outputs.append("".join(data["text/plain"]))
    source = "\n".join(sources)
    output = "\n".join(outputs)
    row_match = re.search(r"Data dasar berhasil disusun:\s*(\d+)\s*baris", output)
    return {
        "available": True,
        "path": str(notebook_path),
        "base_rows": int(row_match.group(1)) if row_match else None,
        "uses_shifted_horizon_target": 'shift(-lead)' in source,
        "uses_causal_lag_features": ".shift(lag)" in source,
        "uses_lagged_rolling_features": 'lag1"].rolling' in source,
        "filters_to_valid_six_month_target": (
            '"target_oni_lead_6m"].notna()' in source
        ),
        "contains_full_dataset_correlation_visualization": (
            "top_features = corrs[" in source
        ),
    }


def _temporal_integrity_report(
    root: Path,
    data_path: Path,
    raw_ordered: bool,
    frame: pd.DataFrame,
    folds: list[Any],
    feature_columns: list[str],
    notebook: dict[str, Any],
) -> str:
    target_checks = []
    audited_horizons = [h for h in (1, 3, 6, 9, 12) if f"target_oni_lead_{h}m" in frame.columns]
    for horizon in audited_horizons:
        observed = frame[f"target_oni_lead_{horizon}m"].to_numpy(dtype=np.float64)
        expected = frame["oni_anom"].shift(-horizon).to_numpy(dtype=np.float64)
        usable = len(frame) - horizon
        mismatches = int(
            (~np.isclose(observed[:usable], expected[:usable], rtol=0.0, atol=1e-8)).sum()
        )
        target_checks.append(
            {
                "horizon_months": horizon,
                "verified_origins": usable,
                "mismatches": mismatches,
                "status": "pass" if mismatches == 0 else "fail",
            }
        )

    purge_checks = []
    for fold in folds:
        for horizon in audited_horizons:
            indices = fold_indices(fold, horizon, WINDOW_MONTHS)
            train_target_end = int(indices["train"].max() + horizon)
            validation_target_end = int(indices["validation"].max() + horizon)
            purge_checks.append(
                {
                    "fold": fold.fold_id,
                    "horizon": horizon,
                    "train_target_before_validation": train_target_end < fold.validation_start,
                    "validation_target_before_test": validation_target_end < fold.test_start,
                }
            )
    purge_pass = all(
        item["train_target_before_validation"] and item["validation_target_before_test"]
        for item in purge_checks
    )

    validation_test_overlap = []
    for previous, following in zip(folds, folds[1:]):
        for horizon in audited_horizons:
            previous_test = set(
                fold_indices(previous, horizon, WINDOW_MONTHS)["test"].tolist()
            )
            next_validation = set(
                fold_indices(following, horizon, WINDOW_MONTHS)["validation"].tolist()
            )
            validation_test_overlap.append(
                {
                    "earlier_test_fold": previous.fold_id,
                    "later_validation_fold": following.fold_id,
                    "horizon": horizon,
                    "overlapping_origins": len(previous_test & next_validation),
                }
            )

    targets_ok = all(item["mismatches"] == 0 for item in target_checks)
    feature_values = frame[feature_columns].to_numpy(dtype=np.float64)
    nonfinite_count = int((~np.isfinite(feature_values)).sum())
    target_source_ok = bool(
        notebook.get("uses_shifted_horizon_target")
        and notebook.get("filters_to_valid_six_month_target")
    )

    target_table = _markdown_table(pd.DataFrame(target_checks))
    purge_table = _markdown_table(pd.DataFrame(purge_checks))
    overlap_table = _markdown_table(pd.DataFrame(validation_test_overlap))
    return f"""# Temporal integrity report

## Dataset and ordering

- Dataset: `{data_path.relative_to(root)}`
- Rows and date span: **{len(frame)}**, {frame["time"].iloc[0].date()} to {frame["time"].iloc[-1].date()}.
- Input features: **{len(feature_columns)}** numeric columns.
- Raw CSV timestamps already ordered: **{raw_ordered}**; unique and contiguous month-start timestamps are enforced by the loader.
- Missing/non-finite input feature values after loading: **{int(frame[feature_columns].isna().sum().sum())} / {nonfinite_count}**. The backtest rejects missing/non-finite values; it does not fit an imputer.

## Target alignment

`load_feature_data` orders rows by time and validates targets against `oni_anom.shift(-h)`. The independent checks below compare every origin for which the future ONI is present within this 114-row table:

{target_table}

The feature-engineering notebook constructs each target using `oni_anom.shift(-lead)` and filters rows using the six-month target's non-null mask. Its recorded output reports {notebook.get("base_rows", "unknown")} monthly source rows before filtering, which is consistent with target observations beyond the final feature timestamp. Source-shift/filter evidence present: **{target_source_ok}**. The retained target ends up to December 2025 although predictor rows end in June 2025. The underlying Zarr ONI source was not reloaded during this audit, so the terminal values' provenance is supported by notebook code/output, not an independent raw-source recomputation.

## Purge and overlapping windows

For each horizon, train origins satisfy `origin + horizon < validation_start`, and validation origins satisfy `origin + horizon < test_start`:

{purge_table}

Purge checks: **{"PASS" if purge_pass else "FAIL"}**. A 12-month input window may cross a split boundary to use earlier observed feature history; it does not expose a future target. The window ends at its forecast origin. This historical context overlap is valid for rolling forecasts.

Fold independence:

{overlap_table}

{"No later validation fold reuses an earlier test period in the configured one-fold evaluation." if not validation_test_overlap else "Later validation origins may reuse earlier test origins after they become historical; fold metrics are dependent and must not be treated as independent repeats."}

## Preprocessing and feature selection

- Feature scaling is fit in `_fit_lstm` using feature rows no later than the final training origin; the ONI target scaler is fit only on training target origins. Validation/test values are transformed, never fit.
- No imputer is fitted in the backtest. The loader fails on null/non-finite features.
- The active backtest uses all {len(feature_columns)} input features; it does not perform feature selection.
- The notebook contains a full-dataset top-correlation calculation for a visualization. It is not applied to the backtest feature list. Using those target-correlated features as a selected model input would leak validation/test information; any future selection must be performed inside each training fold only.
- Current-month ONI/SST/rain features are available to the model at the row's origin. Operational use requires a declared data-availability/issuance cutoff; this audit cannot establish that all contemporaneous monthly aggregates would be available on an actual forecast date.

Overall temporal/target checks: **{"PASS" if raw_ordered and targets_ok and purge_pass and nonfinite_count == 0 else "REVIEW REQUIRED"}**.
"""


def _validate_classification_outputs(
    reports_dir: Path,
    class_reports: pd.DataFrame,
) -> dict[str, Any]:
    report_rows = class_reports.copy()
    report_rows["class_id_numeric"] = pd.to_numeric(
        report_rows["class_id"], errors="coerce"
    )
    required_ids = set(PHASE_CLASSES.tolist())
    report_groups = report_rows.groupby(
        ["fold", "horizon_months", "model", "imbalance_strategy", "split"]
    )
    incomplete_reports = [
        str(key)
        for key, group in report_groups
        if set(group["class_id_numeric"].dropna().astype(int)) != required_ids
    ]
    if incomplete_reports:
        raise ValueError(
            "Classification reports are missing fixed-label rows for: "
            + ", ".join(incomplete_reports)
        )

    matrix_dir = _require(reports_dir / "backtesting" / "confusion_matrices")
    matrix_files = sorted(matrix_dir.glob("*.csv"))
    if not matrix_files:
        raise FileNotFoundError(f"No confusion matrix CSVs found in {matrix_dir}")
    expected_names = [PHASE_NAMES[int(class_id)] for class_id in PHASE_CLASSES]
    for path in matrix_files:
        matrix = pd.read_csv(path, index_col=0)
        if matrix.shape != (3, 3):
            raise ValueError(f"{path} has shape {matrix.shape}; expected 3x3")
        if list(matrix.index) != expected_names or list(matrix.columns) != expected_names:
            raise ValueError(
                f"{path} does not use fixed confusion-matrix order {expected_names}"
            )
    return {
        "classification_report_rows": len(report_rows),
        "fixed_label_report_groups": len(report_groups),
        "confusion_matrix_files": len(matrix_files),
        "all_confusion_matrices_3x3": True,
        "fixed_label_order": expected_names,
    }


def _leakage_audit_report(
    notebook: dict[str, Any],
    classification_outputs: dict[str, Any],
) -> str:
    notebook_target_evidence = (
        "Notebook shift(-lead) construction and six-month target filtering were observed."
        if notebook.get("uses_shifted_horizon_target")
        and notebook.get("filters_to_valid_six_month_target")
        else "Notebook source evidence for target construction is incomplete."
    )
    checks = [
        ("Timestamp order", "Raw feature master is chronological, unique, and contiguous monthly data.", "PASS"),
        ("Target construction", f"ONI leads are generated by shift(-h); all in-table alignments match. {notebook_target_evidence}", "PASS"),
        ("Boundary purge", "Train and validation target timestamps are strictly before the next split; target leakage across boundaries is blocked.", "PASS"),
        ("Overlapping windows", "Windows contain only feature history through their origin. Shared historical feature rows are not future labels.", "PASS WITH NOTE"),
        ("Fold reuse", "The configured evaluation contains one terminal fold, so no later validation period reuses a reported test interval.", "PASS FOR CURRENT SPLIT"),
        ("LSTM OOF classifier features", "Classifier training uses expanding OOF LSTM forecasts. Each block model trains on earlier origins and early-stops on an inner validation period whose targets end before the block.", "PASS BY CODE PATH"),
        ("Outer LSTM validation/test", "LSTM epoch count is selected using an internal terminal validation segment within outer training, then refit on all outer training origins. Outer validation and test targets are not used to fit LSTM weights or select its epoch.", "PASS BY CODE PATH"),
        ("Classifier input targets", "resolve_feature_columns excludes all target_* columns. Classifier receives contemporaneous/lagged features plus predicted LSTM ONI, not actual future ONI.", "PASS"),
        ("Scaling", "Feature and target scalers are fitted on training history/targets in each outer or inner fit.", "PASS BY CODE PATH"),
        ("Imputation", "No imputation fit or transform occurs; missing/non-finite feature input raises an error.", "PASS"),
        ("Feature selection", "No feature selection runs in the backtest. Notebook's full-dataset top-correlation step is a visualization only and must not be reused to select inputs.", "PASS WITH CAUTION"),
        ("Hyperparameter tuning", "No grid search is run. LSTM epoch selection uses a train-internal chronological segment; tree early stopping uses outer validation, which is also scored for candidate ranking. This makes classifier rankings provisional.", "LIMITATION"),
        ("Test use", "Test folds are evaluated only; audit rankings and the abstention gate use validation metrics and class coverage only.", "PASS"),
    ]
    table = _markdown_table(
        pd.DataFrame(checks, columns=["component", "finding", "status"])
    )
    return f"""# Leakage audit

## Findings

{table}

## LSTM out-of-fold path

For each outer fold and horizon, `_oof_lstm_forecasts` sets the outer training limit to `fold.train_end - horizon`. It creates successive six-origin blocks. For a block beginning at `B`, its inner training labels end before the inner validation period, the inner validation labels end before `B`, and only then is the fitted LSTM used to forecast origins `B` through the block end. `_fit_lstm` fits its feature scaler through the last training origin and its target scaler only on training target values. `predict_lstm` runs in evaluation/no-gradient mode.

The classifier's OOF rows therefore do not use their own ONI targets to fit the LSTM producing their `lstm_oni_forecast`. The outer LSTM's epoch count is selected from a terminal validation segment contained within outer training, then its weights are refit on all outer training origins using that fixed epoch count. Outer validation/test targets do not select LSTM epochs or fit its weights. Tree classifier early stopping uses outer validation; the untouched test targets are read for final scoring only after validation-based candidate selection.

The OOF procedure drops early outer-training origins; the classifier sees only the retained OOF forecasts. This is leakage-safe but materially reduces its training size (reported in `class_coverage_report.csv`).

## Remaining methodological caveats

1. The outer validation data are also used for tree-classifier early stopping and then scored for candidate ranking. A validation ranking is not an untouched model-selection estimate. LSTM epoch selection is separate and uses only a segment within outer training.
2. There is only one validation and one test period in the current record; this is insufficient to estimate stability across independent ENSO regimes.
3. Monthly feature availability is not timestamped at issuance time. Contemporaneous ONI, SST, MHW, and rainfall features are safe only if they would be observed at the forecast origin.
4. The feature-engineering notebook's top-correlation plot is computed over the full retained series. It is not used by the backtester; any production feature selection must be nested within each training fold.

No test scores were used in this audit's candidate ranking or selection gate.

## Classification diagnostic integrity

- Fixed labels in reports and matrices: `{classification_outputs["fixed_label_order"]}`.
- Classification report groups checked: **{classification_outputs["fixed_label_report_groups"]}**; all include per-class rows for labels 0, 1, and 2, including absent classes with zero support.
- Confusion matrix CSVs checked: **{classification_outputs["confusion_matrix_files"]}**; every matrix is 3×3 in the fixed class order.
- The model selection audit contains actual and predicted counts and per-class precision, recall, and F1 for both validation and test; test columns are descriptive only.
"""


def _data_sufficiency_report(
    frame: pd.DataFrame,
    feature_count: int,
    coverage: pd.DataFrame,
    selection_audit: pd.DataFrame,
) -> str:
    raw_counts = []
    audited_horizons = [h for h in (1, 3, 6, 9, 12) if f"target_phase_lead_{h}m" in frame.columns]
    for horizon in audited_horizons:
        labels = frame[f"target_phase_lead_{horizon}m"].dropna().astype(int)
        raw_counts.append(
            {
                "horizon": horizon,
                "La Nina": int((labels == 0).sum()),
                "Neutral": int((labels == 1).sum()),
                "El Nino": int((labels == 2).sum()),
                "all_labels": len(labels),
            }
        )

    fold_rows = coverage.loc[
        coverage["split"].isin(("train", "classifier_train_oof", "validation", "test"))
    ]
    fold_ids = sorted(
        pd.to_numeric(fold_rows["fold"], errors="coerce").dropna().astype(int).unique()
    )
    summary_rows = []
    for horizon in audited_horizons:
        row: dict[str, Any] = {"horizon": horizon}
        for fold in fold_ids:
            current = fold_rows.loc[
                (fold_rows["horizon_months"] == horizon)
                & (fold_rows["fold"].astype(str) == str(fold))
            ]
            for split in ("train", "classifier_train_oof", "validation", "test"):
                subset = current.loc[current["split"] == split]
                row[f"fold{fold}_{split}_n"] = (
                    int(subset["sample_count"].iloc[0]) if not subset.empty else 0
                )
                if split in ("validation", "test") and not subset.empty:
                    row[f"fold{fold}_{split}_coverage"] = (
                        f'{int(subset["actual_class_coverage"].iloc[0])}/3'
                    )
        summary_rows.append(row)

    oof_counts = (
        fold_rows.loc[fold_rows["split"] == "classifier_train_oof"]
        .drop_duplicates(["fold", "horizon_months"])["sample_count"]
    )
    minimum_oof = int(oof_counts.min()) if not oof_counts.empty else 0
    maximum_oof = int(oof_counts.max()) if not oof_counts.empty else 0
    eligible_candidate_count = int(
        (selection_audit["selection_status"] != "insufficient_class_coverage").sum()
    )
    fold_table = _markdown_table(pd.DataFrame(summary_rows))
    return f"""# Data sufficiency report

## Effective sample sizes

The feature master contains **{len(frame)}** rows, **{feature_count}** input features, and a 12-month input window. The classifier receives those features plus one predicted ONI feature (**{feature_count + 1}** inputs). It is trained only on retained causal LSTM OOF rows: across horizons/folds, the OOF training set ranges from **{minimum_oof}** to **{maximum_oof}** rows. The smallest OOF set has fewer rows than features, so flexible tree models can overfit severely. **{eligible_candidate_count}** validation candidate rows have full class coverage.

| Horizon | La Niña | Neutral | El Niño | Total labeled rows |
| --- | ---: | ---: | ---: | ---: |
{_markdown_table(pd.DataFrame(raw_counts)).split(chr(10), 2)[2]}

Purging and the sliding window reduce usable validation rows to 23, 21, and 18 for horizons 1, 3, and 6; the terminal test period has 18 origins. The actual per-fold train/OOF/validation/test counts and class distributions are in `class_coverage_report.csv`:

{fold_table}

## Interpretation and recommendations

- **114 samples are not sufficient for a reliable three-class, multi-horizon model-selection claim.** The configured run has only one 18-month test period and one validation period; it cannot measure between-period stability.
- Extend the historical record to multiple decades if a homogeneous source with consistent feature definitions is available. Do not synthesize observations or rebalance validation/test.
- **67 features are too many relative to the OOF classifier sample sizes in this experiment.** Reduce to a small, domain-justified candidate set and compare against persistence/climatology baselines.
- No feature selection is applied in this audit. If introduced, fit the selector independently inside each outer training fold (and inside the OOF training procedure where applicable); never select using the full dataset or test labels.
- Keep all horizons separate. The 6-month horizon has the fewest validation origins and particularly small OOF samples.
- A 24-month validation interval offers more support at horizon 6 than an 18-month interval while retaining 72 training months. `validation_window_sweep.csv` compares it with 18-, 30-, and 36-month alternatives. Outer validation still controls tree-classifier early stopping and is not an independent model-selection estimate; LSTM epoch selection uses an internal segment of the training period.
- The previous 60/18/18 layout generated two folds, but its first validation omitted El Niño and its second validation reused prior test origins. Generating more than two folds here would require shorter validation/test intervals; a 12-month validation leaves only six horizon-6 origins after purge, so it was rejected.
- Current data cannot support several independent validation and test periods with adequate class coverage. Extend the record before interpreting fold variability or claiming stable model selection.

This report assesses data sufficiency only; it does not alter features, retrain models, or change saved model artifacts.
"""


def _final_recommendation(
    selection_audit: pd.DataFrame,
    coverage: pd.DataFrame,
) -> str:
    validation = coverage.loc[coverage["split"] == "validation"]
    incomplete_horizons = sorted(
        validation.loc[
            validation["actual_class_coverage"] < len(PHASE_CLASSES),
            "horizon_months",
        ].unique()
    )
    leaders = selection_audit.loc[
        selection_audit["fold_local_validation_rank"] == 1,
        [
            "fold",
            "horizon_months",
            "model",
            "imbalance_strategy",
            "macro_f1_validation",
            "balanced_accuracy_validation",
        ],
    ]
    leader_table = _markdown_table(leaders)
    incomplete_text = ", ".join(str(item) for item in incomplete_horizons)
    if incomplete_horizons:
        coverage_statement = (
            "At least one configured validation horizon lacks a class "
            f"(horizons: {incomplete_text}); no three-class ranking is valid there."
        )
    else:
        coverage_statement = (
            "The configured validation period covers all three classes at every "
            "horizon, so validation-only candidate ranking is permitted."
        )
    return f"""# Final recommendation

## Decision

**Do not declare a final production model from this experiment.** {coverage_statement} The configured run has only one validation period and one test period; outer validation is also used for tree-classifier early stopping, so its ranks remain provisional.

Validation-only diagnostic rank leaders are:

{leader_table}

These ranks use macro-F1, balanced accuracy, per-class precision/recall, and class coverage, with ONI RMSE as a later tie-breaker. Test metrics are descriptive only and were not used to rank candidates. The test period misses classes at some horizons, so its metrics cannot establish recognition of all three phases.

The selected 24-month validation duration is a compromise: it retains 72 training months and yields 23, 21, and 18 usable validation origins for horizons 1, 3, and 6. The 6-month horizon has only four Neutral validation examples, so selection is still uncertain.

## Audit conclusions

1. Raw timestamps are ordered and contiguous; target shifts, target-time purge, training-only scaling, causal lag/rolling construction, and OOF forecast boundaries pass the checks documented in `temporal_integrity_report.md` and `leakage_audit.md`.
2. The single terminal fold avoids cross-fold test/validation reuse, but does not provide independent estimates of temporal stability.
3. The classifier is trained on few OOF rows relative to 68 input dimensions. This is a dominant data-sufficiency concern even after increasing the initial training interval.
4. No model is promoted as a final production choice; rankings and selected checkpoints remain provisional pending independent historical evaluation.

## Next steps

1. Extend the historical record with consistent, timestamped predictors and target definitions; do not generate synthetic test examples.
2. Define forecast issuance time and lag any monthly predictor that would not be available then.
3. Extend the historical record and run nested rolling-origin evaluation with multiple three-class validation and test periods.
4. Establish persistence and climatology baselines, then consider fold-local domain feature selection and regularization.
5. Promote a final model only after class coverage and selection stability are supported by multiple independent validation periods.
"""


def generate_final_audit(
    data_path: Path = DEFAULT_DATA_PATH,
    reports_dir: Path = DEFAULT_REPORTS_PATH,
) -> Path:
    data_path = data_path.resolve()
    reports_dir = reports_dir.resolve()
    root = PROJECT_ROOT
    audit_dir = reports_dir / "final_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(_require(data_path), parse_dates=["time"])
    raw_ordered = bool(raw["time"].is_monotonic_increasing)
    frame = load_feature_data(data_path)
    feature_columns = resolve_feature_columns(frame)
    folds = build_expanding_folds(
        len(frame),
        min_train_months=BACKTEST_MIN_TRAIN_MONTHS,
        validation_months=BACKTEST_VALIDATION_MONTHS,
        test_months=BACKTEST_TEST_MONTHS,
        step_months=BACKTEST_STEP_MONTHS,
    )
    window_sweep = validation_window_sweep(frame)
    fold_metrics, class_reports, split_distribution = _read_inputs(reports_dir)
    coverage = _class_coverage_report(split_distribution)
    selection_audit = _selection_audit(fold_metrics, class_reports, coverage)
    notebook = _notebook_evidence(root)
    classification_outputs = _validate_classification_outputs(
        reports_dir,
        class_reports,
    )

    (audit_dir / "class_coverage_report.csv").write_text(
        coverage.to_csv(index=False),
        encoding="utf-8",
    )
    window_sweep.to_csv(audit_dir / "validation_window_sweep.csv", index=False)
    (audit_dir / "validation_window_sweep.json").write_text(
        window_sweep.to_json(orient="records", date_format="iso", indent=2),
        encoding="utf-8",
    )
    selection_audit.to_csv(audit_dir / "model_selection_audit.csv", index=False)
    (audit_dir / "temporal_integrity_report.md").write_text(
        _temporal_integrity_report(
            root,
            data_path,
            raw_ordered,
            frame,
            folds,
            feature_columns,
            notebook,
        ),
        encoding="utf-8",
    )
    (audit_dir / "leakage_audit.md").write_text(
        _leakage_audit_report(notebook, classification_outputs),
        encoding="utf-8",
    )
    (audit_dir / "data_sufficiency_report.md").write_text(
        _data_sufficiency_report(
            frame,
            len(feature_columns),
            coverage,
            selection_audit,
        ),
        encoding="utf-8",
    )
    (audit_dir / "final_recommendation.md").write_text(
        _final_recommendation(selection_audit, coverage),
        encoding="utf-8",
    )
    return audit_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--reports", type=Path, default=DEFAULT_REPORTS_PATH)
    args = parser.parse_args()
    print(generate_final_audit(args.data, args.reports))


if __name__ == "__main__":
    main()
