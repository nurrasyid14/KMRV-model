"""Chronological ENSO data auditing and leakage-aware fold construction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

PHASE_NAMES = {0: "La Nina", 1: "Neutral", 2: "El Nino"}
PHASE_CLASSES = np.array([0, 1, 2], dtype=np.int64)
SUPPORTED_HORIZONS = (1, 3, 6)
BACKTEST_MIN_TRAIN_MONTHS = 72
BACKTEST_VALIDATION_MONTHS = 24
BACKTEST_TEST_MONTHS = 18
BACKTEST_STEP_MONTHS = 18
VALIDATION_SWEEP_MONTHS = (18, 24, 30, 36)
FOLD_SWEEP_VALIDATION_MONTHS = (12, 18, 24, 30, 36)
FOLD_SWEEP_TEST_MONTHS = (12, 18, 24)
FOLD_SWEEP_MIN_TRAIN_MONTHS = (60, BACKTEST_MIN_TRAIN_MONTHS)
LOW_CLASS_SUPPORT_THRESHOLD = 5


@dataclass(frozen=True)
class BacktestFold:
    fold_id: int
    train_end: int
    validation_end: int
    test_end: int

    @property
    def validation_start(self) -> int:
        return self.train_end

    @property
    def test_start(self) -> int:
        return self.validation_end


def load_feature_data(
    path: Path,
    verify_target_alignment: bool = True,
) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=["time"])
    if "time" not in frame.columns:
        raise ValueError(f"{path} must contain a 'time' column")
    frame = frame.sort_values("time").reset_index(drop=True)
    if frame["time"].isna().any() or frame["time"].duplicated().any():
        raise ValueError(f"{path} must contain unique, non-missing timestamps")
    if len(frame) < 1:
        raise ValueError(f"{path} contains no rows")
    expected_months = pd.date_range(frame["time"].iloc[0], frame["time"].iloc[-1], freq="MS")
    if not frame["time"].reset_index(drop=True).equals(pd.Series(expected_months, name="time")):
        raise ValueError("ENSO features must contain a contiguous monthly time index")

    feature_columns = resolve_feature_columns(frame)
    if not feature_columns:
        raise ValueError("No numeric climate feature columns were found")
    if not frame[feature_columns].apply(pd.to_numeric, errors="coerce").notna().all().all():
        raise ValueError("Climate features contain missing or non-numeric values")
    if not np.isfinite(frame[feature_columns].to_numpy(dtype=np.float64)).all():
        raise ValueError("Climate features contain infinite values")

    for horizon in SUPPORTED_HORIZONS:
        oni_target = f"target_oni_lead_{horizon}m"
        phase_target = f"target_phase_lead_{horizon}m"
        missing = {oni_target, phase_target} - set(frame.columns)
        if missing:
            raise ValueError(f"Dataset is missing target columns: {sorted(missing)}")
        if frame[[oni_target, phase_target]].isna().any().any():
            raise ValueError(f"Dataset has missing labels for the {horizon}-month horizon")
        labels = frame[phase_target].to_numpy()
        if not np.isin(labels, PHASE_CLASSES).all():
            raise ValueError(f"{phase_target} contains labels outside {PHASE_CLASSES.tolist()}")
        if not np.array_equal(labels.astype(np.int64), labels):
            raise ValueError(f"{phase_target} must contain integer class labels")

        if verify_target_alignment:
            future_rows = len(frame) - horizon
            expected_targets = frame["oni_anom"].shift(-horizon).iloc[:future_rows].to_numpy()
            observed_targets = frame[oni_target].iloc[:future_rows].to_numpy()
            if not np.allclose(observed_targets, expected_targets, rtol=0.0, atol=1e-8):
                raise ValueError(
                    f"{oni_target} does not match the observed ONI anomaly shifted "
                    f"{horizon} months into the future"
                )
        expected_phase = np.where(
            frame[oni_target].to_numpy() < -0.5,
            0,
            np.where(frame[oni_target].to_numpy() > 0.5, 2, 1),
        )
        if not np.array_equal(labels.astype(np.int64), expected_phase):
            raise ValueError(f"{phase_target} is inconsistent with {oni_target} thresholds")

    return frame


def resolve_feature_columns(frame: pd.DataFrame) -> list[str]:
    columns = [
        column
        for column in frame.columns
        if column != "time" and not column.startswith("target_")
    ]
    non_numeric = [
        column
        for column in columns
        if not pd.api.types.is_numeric_dtype(frame[column])
    ]
    if non_numeric:
        raise ValueError(f"Climate feature columns must be numeric: {non_numeric}")
    return columns


def build_expanding_folds(
    row_count: int,
    min_train_months: int = 60,
    validation_months: int = 18,
    test_months: int = 18,
    step_months: int = 18,
) -> list[BacktestFold]:
    if min_train_months <= 0 or validation_months <= 0 or test_months <= 0 or step_months <= 0:
        raise ValueError("Fold sizes must be positive")
    folds: list[BacktestFold] = []
    test_start = min_train_months + validation_months
    while test_start + test_months <= row_count:
        folds.append(
            BacktestFold(
                fold_id=len(folds) + 1,
                train_end=test_start - validation_months,
                validation_end=test_start,
                test_end=test_start + test_months,
            )
        )
        test_start += step_months
    if not folds:
        raise ValueError(
            "Not enough monthly observations for one fold with "
            f"{min_train_months} train, {validation_months} validation, "
            f"and {test_months} test months"
        )
    return folds


def fold_indices(
    fold: BacktestFold,
    horizon: int,
    window: int,
) -> dict[str, np.ndarray]:
    if horizon not in SUPPORTED_HORIZONS:
        raise ValueError(f"Unsupported forecast horizon: {horizon}")
    if window < 1:
        raise ValueError("Sliding window must be positive")

    train = np.arange(window - 1, fold.train_end - horizon, dtype=np.int64)
    validation = np.arange(
        fold.validation_start,
        fold.validation_end - horizon,
        dtype=np.int64,
    )
    test = np.arange(fold.test_start, fold.test_end, dtype=np.int64)
    if len(train) == 0 or len(validation) == 0 or len(test) == 0:
        raise ValueError(
            f"Fold {fold.fold_id} is too small after purging the {horizon}-month target gap"
        )
    return {"train": train, "validation": validation, "test": test}


def validation_window_sweep(
    frame: pd.DataFrame,
    horizons: tuple[int, ...] = SUPPORTED_HORIZONS,
    validation_months: tuple[int, ...] = VALIDATION_SWEEP_MONTHS,
    test_months: int = BACKTEST_TEST_MONTHS,
    min_train_months: int = 60,
) -> pd.DataFrame:
    if test_months <= 0 or min_train_months <= 0:
        raise ValueError("Test and minimum training periods must be positive")
    if any(months <= 0 for months in validation_months):
        raise ValueError("Validation periods must be positive")
    if any(horizon not in SUPPORTED_HORIZONS for horizon in horizons):
        raise ValueError(f"Unsupported horizon in {horizons}")

    rows: list[dict[str, object]] = []
    boundary = len(frame) - test_months
    if boundary < 1:
        raise ValueError("Not enough rows to reserve the requested final test period")

    for months in validation_months:
        train_end = boundary - months
        if train_end < min_train_months:
            continue
        for horizon in horizons:
            origins = np.arange(train_end, boundary - horizon, dtype=np.int64)
            if len(origins) == 0:
                continue
            labels = frame.iloc[origins][f"target_phase_lead_{horizon}m"].astype(int)
            counts = labels.value_counts().to_dict()
            missing = [
                PHASE_NAMES[class_id]
                for class_id in PHASE_CLASSES
                if int(class_id) not in counts
            ]
            row: dict[str, object] = {
                "validation_months": months,
                "train_months": train_end,
                "test_months": test_months,
                "horizon_months": horizon,
                "train_start": frame["time"].iloc[0],
                "train_end": frame["time"].iloc[train_end - 1],
                "validation_start": frame["time"].iloc[train_end],
                "validation_boundary_end": frame["time"].iloc[boundary - 1],
                "validation_origin_start": frame["time"].iloc[origins[0]],
                "validation_origin_end": frame["time"].iloc[origins[-1]],
                "test_start": frame["time"].iloc[boundary],
                "test_end": frame["time"].iloc[-1],
                "validation_sample_count": len(origins),
                "actual_class_coverage": len(PHASE_CLASSES) - len(missing),
                "missing_classes": missing,
                "coverage_status": (
                    "complete_class_coverage"
                    if not missing
                    else "insufficient_class_coverage"
                ),
                "is_configured_window": months == BACKTEST_VALIDATION_MONTHS,
            }
            for class_id, class_name in PHASE_NAMES.items():
                count = int(counts.get(class_id, 0))
                row[f"class_{class_id}_name"] = class_name
                row[f"class_{class_id}_count"] = count
                row[f"class_{class_id}_percentage"] = (
                    100.0 * count / len(origins)
                )
            rows.append(row)
    return pd.DataFrame(rows)


def fold_feasibility_sweep(
    frame: pd.DataFrame,
    horizons: tuple[int, ...] = SUPPORTED_HORIZONS,
    min_train_periods: tuple[int, ...] = FOLD_SWEEP_MIN_TRAIN_MONTHS,
    validation_periods: tuple[int, ...] = FOLD_SWEEP_VALIDATION_MONTHS,
    test_periods: tuple[int, ...] = FOLD_SWEEP_TEST_MONTHS,
    window: int = 12,
) -> pd.DataFrame:
    if not horizons or any(horizon not in SUPPORTED_HORIZONS for horizon in horizons):
        raise ValueError(f"Unsupported or empty horizon selection: {horizons}")
    if not min_train_periods or any(
        months < window for months in min_train_periods
    ) or window < 1:
        raise ValueError("Minimum training history must be at least one input window")
    candidate_folds: list[tuple[int, int, int, BacktestFold]] = []
    for min_train_months in min_train_periods:
        for validation_months in validation_periods:
            for test_months in test_periods:
                try:
                    folds = build_expanding_folds(
                        len(frame),
                        min_train_months=min_train_months,
                        validation_months=validation_months,
                        test_months=test_months,
                        step_months=test_months,
                    )
                except ValueError:
                    continue
                candidate_folds.extend(
                    (min_train_months, validation_months, test_months, fold)
                    for fold in folds
                )

    rows: list[dict[str, object]] = []
    for min_train_months, validation_months, test_months, fold in candidate_folds:
        fold_rows: list[dict[str, object]] = []
        rejection_reasons: list[str] = []
        low_support: list[str] = []
        validation_coverages = []
        test_coverages = []
        train_coverages = []
        purge_checks = []
        window_checks = []
        independent_validation_checks = []
        for horizon in horizons:
            indices = fold_indices(fold, horizon, window)
            row: dict[str, object] = {
                "min_train_months": min_train_months,
                "validation_months": validation_months,
                "test_months": test_months,
                "fold": fold.fold_id,
                "horizon_months": horizon,
            }
            for split, origins in indices.items():
                labels = frame.iloc[origins][
                    f"target_phase_lead_{horizon}m"
                ].astype(int)
                counts = labels.value_counts().to_dict()
                missing = [
                    PHASE_NAMES[class_id]
                    for class_id in PHASE_CLASSES
                    if int(class_id) not in counts
                ]
                coverage = len(PHASE_CLASSES) - len(missing)
                row[f"{split}_sample_count"] = len(origins)
                row[f"{split}_class_coverage"] = coverage
                row[f"{split}_missing_classes"] = missing
                row[f"{split}_origin_start"] = frame["time"].iloc[origins[0]]
                row[f"{split}_origin_end"] = frame["time"].iloc[origins[-1]]
                row[f"{split}_target_end"] = (
                    frame["time"].iloc[origins[-1]]
                    + pd.DateOffset(months=horizon)
                )
                if split == "train":
                    train_coverages.append(coverage)
                elif split == "validation":
                    validation_coverages.append(coverage)
                else:
                    test_coverages.append(coverage)
                if coverage < len(PHASE_CLASSES):
                    rejection_reasons.append(
                        f"{split}_h{horizon}_missing_"
                        + "_".join(missing).replace(" ", "_")
                    )
                for class_id, class_name in PHASE_NAMES.items():
                    count = int(counts.get(class_id, 0))
                    row[f"{split}_class_{class_id}_count"] = count
                    row[f"{split}_class_{class_id}_percentage"] = (
                        100.0 * count / len(origins)
                    )
                    if 0 < count < LOW_CLASS_SUPPORT_THRESHOLD:
                        low_support.append(
                            f"{split}_h{horizon}_{class_name}={count}"
                        )
            train_target_before_validation = bool(
                np.all(indices["train"] + horizon < fold.validation_start)
            )
            validation_target_before_test = bool(
                np.all(indices["validation"] + horizon < fold.test_start)
            )
            purge_ok = train_target_before_validation and validation_target_before_test
            window_ok = all(
                np.all(origins >= window - 1)
                for origins in indices.values()
            )
            row["purge_ok"] = purge_ok
            row["input_window_ok"] = window_ok
            prior_test_origins = [
                origin
                for prior_min_train, prior_validation, prior_test, prior_fold
                in candidate_folds
                if (
                    prior_min_train,
                    prior_validation,
                    prior_test,
                )
                == (min_train_months, validation_months, test_months)
                and prior_fold.fold_id < fold.fold_id
                for origin in range(prior_fold.test_start, prior_fold.test_end)
            ]
            validation_reuses_prior_test = bool(
                prior_test_origins
                and np.intersect1d(
                    indices["validation"],
                    np.asarray(prior_test_origins, dtype=np.int64),
                ).size
            )
            row["validation_independent_of_prior_test"] = (
                not validation_reuses_prior_test
            )
            purge_checks.append(purge_ok)
            window_checks.append(window_ok)
            independent_validation_checks.append(
                not validation_reuses_prior_test
            )
            if not purge_ok:
                rejection_reasons.append(f"h{horizon}_target_purge_failed")
            if not window_ok:
                rejection_reasons.append(f"h{horizon}_input_window_failed")
            if validation_reuses_prior_test:
                rejection_reasons.append(
                    f"h{horizon}_validation_reuses_prior_test_period"
                )
            fold_rows.append(row)

        accepted = (
            bool(purge_checks)
            and all(purge_checks)
            and all(window_checks)
            and all(independent_validation_checks)
            and bool(train_coverages)
            and min(train_coverages) == len(PHASE_CLASSES)
            and min(validation_coverages) == len(PHASE_CLASSES)
            and min(test_coverages) == len(PHASE_CLASSES)
        )
        for row in fold_rows:
            row["fold_accepted"] = accepted
            row["decision"] = (
                "accepted"
                if accepted
                else "rejected_incomplete_coverage_or_temporal_check"
            )
            row["rejection_reasons"] = sorted(set(rejection_reasons))
            row["low_class_support_warnings"] = sorted(set(low_support))
            rows.append(row)
    return pd.DataFrame(rows)


def windows_for_origins(
    values: np.ndarray,
    origins: np.ndarray,
    window: int,
) -> np.ndarray:
    if len(origins) == 0:
        raise ValueError("Cannot create sliding windows for an empty origin set")
    if np.any(origins < window - 1) or np.any(origins >= len(values)):
        raise ValueError("Window origins fall outside the available monthly history")
    windows = np.stack(
        [values[origin - window + 1:origin + 1] for origin in origins]
    )
    return windows.astype(np.float32)


def distribution_rows(
    frame: pd.DataFrame,
    horizon: int,
    dataset_name: str,
    period: str,
    sample_count: int | None = None,
) -> list[dict[str, object]]:
    target = f"target_phase_lead_{horizon}m"
    counts = frame[target].astype(int).value_counts().to_dict()
    total = len(frame) if sample_count is None else sample_count
    rows = []
    for class_id, class_name in PHASE_NAMES.items():
        count = int(counts.get(class_id, 0))
        rows.append(
            {
                "dataset": dataset_name,
                "period": period,
                "horizon_months": horizon,
                "class_id": class_id,
                "class_name": class_name,
                "sample_count": total,
                "class_count": count,
                "proportion": count / total if total else 0.0,
                "class_missing": count == 0,
            }
        )
    return rows


def audit_tables(
    frame: pd.DataFrame,
    data_dir: Path,
    folds: list[BacktestFold],
    horizons: tuple[int, ...],
    window: int,
) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    class_rows: list[dict[str, object]] = []
    split_rows: list[dict[str, object]] = []
    split_files = {
        "provided_train": data_dir / "train_features.csv",
        "provided_validation": data_dir / "val_features.csv",
        "provided_test": data_dir / "test_features.csv",
    }

    for horizon in horizons:
        class_rows.extend(distribution_rows(frame, horizon, "master", "all"))
        for year, year_frame in frame.groupby(frame["time"].dt.year, sort=True):
            class_rows.extend(distribution_rows(frame=year_frame, horizon=horizon,
                                                dataset_name="master", period=str(year)))
        for split_name, split_path in split_files.items():
            if not split_path.exists():
                continue
            split_frame = load_feature_data(split_path, verify_target_alignment=False)
            class_rows.extend(
                distribution_rows(split_frame, horizon, split_name, "all")
            )
            input_rows = max(0, len(split_frame) - window + 1)
            target = f"target_phase_lead_{horizon}m"
            counts = split_frame[target].astype(int).value_counts().to_dict()
            for class_id, class_name in PHASE_NAMES.items():
                count = int(counts.get(class_id, 0))
                split_rows.append(
                    {
                        "fold": split_name,
                        "split": split_name.removeprefix("provided_"),
                        "horizon_months": horizon,
                        "start_time": split_frame["time"].iloc[0],
                        "end_time": split_frame["time"].iloc[-1],
                        "sample_count": len(split_frame),
                        "post_window_sample_count": input_rows,
                        "class_id": class_id,
                        "class_name": class_name,
                        "class_count": count,
                        "proportion": count / len(split_frame) if len(split_frame) else 0.0,
                        "class_missing": count == 0,
                        "purged_target_rows": 0,
                    }
                )

        for fold in folds:
            indices = fold_indices(fold, horizon, window)
            for split_name, row_indices in indices.items():
                split_frame = frame.iloc[row_indices]
                split_rows.extend(
                    {
                        "fold": fold.fold_id,
                        "split": split_name,
                        "horizon_months": horizon,
                        "start_time": split_frame["time"].iloc[0],
                        "end_time": split_frame["time"].iloc[-1],
                        "sample_count": len(split_frame),
                        "post_window_sample_count": len(split_frame),
                        "class_id": row["class_id"],
                        "class_name": row["class_name"],
                        "class_count": row["class_count"],
                        "proportion": row["proportion"],
                        "class_missing": row["class_missing"],
                        "purged_target_rows": (
                            horizon if split_name in ("train", "validation") else 0
                        ),
                    }
                    for row in distribution_rows(
                        split_frame,
                        horizon,
                        f"fold_{fold.fold_id}",
                        split_name,
                    )
                )

    missing = [
        {
            "dataset": row["dataset"],
            "period": row["period"],
            "horizon_months": row["horizon_months"],
            "class_name": row["class_name"],
        }
        for row in class_rows
        if row["class_missing"]
    ]
    summary = {
        "total_samples": len(frame),
        "time_start": frame["time"].iloc[0].date().isoformat(),
        "time_end": frame["time"].iloc[-1].date().isoformat(),
        "monthly_contiguous": True,
        "feature_count": len(resolve_feature_columns(frame)),
        "horizons_months": list(horizons),
        "class_mapping": {str(key): value for key, value in PHASE_NAMES.items()},
        "fold_count": len(folds),
        "folds": [
            {
                "fold": fold.fold_id,
                "train_start": frame["time"].iloc[0].date().isoformat(),
                "train_end": frame["time"].iloc[fold.train_end - 1].date().isoformat(),
                "validation_start": frame["time"].iloc[fold.validation_start].date().isoformat(),
                "validation_end": frame["time"].iloc[fold.validation_end - 1].date().isoformat(),
                "test_start": frame["time"].iloc[fold.test_start].date().isoformat(),
                "test_end": frame["time"].iloc[fold.test_end - 1].date().isoformat(),
            }
            for fold in folds
        ],
        "missing_class_periods": missing,
        "target_alignment": "target_oni_lead_h matches oni_anom shifted by h months",
        "purge_rule": "train/validation targets must occur strictly before the next split",
    }
    return summary, pd.DataFrame(class_rows), pd.DataFrame(split_rows)
