#!/usr/bin/env python
"""
Aggregate raw Malaysia and Hawaii rainfall observations into one monthly CSV.

Run this script before ``python src/preprocessing.py`` so the monthly rainfall
comparison is included in the hierarchical Zarr store.

Defaults are relative to this script, so the command works from any directory:
    python src/rainfall_prepro.py

The output is dataset/data_rainfall_monthly/rainfall_comparison.csv.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"
START = pd.Timestamp("2015-01-01")
END = pd.Timestamp("2025-12-31")
MONTHS = pd.date_range(START, END, freq="MS")

MY_VALUE_COLS = [
    "n_pixels", "rfh", "rfh_avg", "r1h", "r1h_avg",
    "r3h", "r3h_avg", "rfq", "r1q", "r3q",
]
DATE_COL_RE = re.compile(r"^X?(\d{4})[.\-_](\d{2})[.\-_](\d{2})$")
META_COLS = ["SKN", "Station.Name", "LAT", "LON", "ELEV.m."]
MISSING_VALUES = ["NA", "NaN", "", "-999", "-9999"]


def warn_missing_months(frame: pd.DataFrame, label: str) -> None:
    values = frame.drop(columns=["time", "n_obs", "n_stations"], errors="ignore")
    missing = pd.DatetimeIndex(
        frame.loc[~values.notna().any(axis=1), "time"]
    )
    if len(missing):
        labels = ", ".join(m.strftime("%Y-%m") for m in missing)
        print(
            f"[WARNING] {label}: no rainfall values for "
            f"{len(missing)} month(s): {labels}"
        )


def aggregate_malaysia(csv_path: Path) -> pd.DataFrame:
    """Average the dekadal regional observations into one row per month."""
    df = pd.read_csv(csv_path)
    df.columns = [str(column).strip() for column in df.columns]
    if "date" not in df.columns:
        raise ValueError(f"Kolom 'date' tidak ditemukan pada CSV Malaysia: {csv_path}")

    df = df.loc[~df["date"].astype(str).str.startswith("#")].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.loc[df["date"].between(START, END)].copy()
    if df.empty:
        raise ValueError(f"Tidak ada data Malaysia pada rentang {START:%Y-%m}–{END:%Y-%m}")

    missing_columns = [column for column in MY_VALUE_COLS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Kolom rainfall Malaysia tidak lengkap pada {csv_path}: "
            f"{', '.join(missing_columns)}"
        )

    for column in MY_VALUE_COLS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["time"] = df["date"].dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby("time")[MY_VALUE_COLS].mean()
    monthly["n_obs"] = df.groupby("time").size()
    monthly = monthly.reindex(MONTHS)
    monthly.index.name = "time"
    monthly = monthly.reset_index()
    monthly["n_obs"] = monthly["n_obs"].astype("Int64")
    return monthly[["time", *MY_VALUE_COLS, "n_obs"]]


def read_csv_safe(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, na_values=MISSING_VALUES)
    except UnicodeDecodeError:
        return pd.read_csv(path, na_values=MISSING_VALUES, encoding="latin-1")


def station_monthly_from_file(path: Path) -> pd.DataFrame:
    """Convert daily wide columns into station-level monthly means."""
    df = read_csv_safe(path)
    df.columns = [str(column).strip() for column in df.columns]

    date_map: dict[str, pd.Timestamp] = {}
    for column in df.columns:
        match = DATE_COL_RE.match(column)
        if match:
            date = pd.Timestamp(*(int(part) for part in match.groups()))
            if START <= date <= END:
                date_map[column] = date
    if not date_map:
        raise ValueError("tidak ada kolom tanggal harian 2015–2025 (mis. X2015.01.01)")

    id_col = "SKN" if "SKN" in df.columns else "Station.Name"
    if id_col not in df.columns:
        raise ValueError("Kolom identitas stasiun 'SKN' atau 'Station.Name' tidak ditemukan")
    meta = [column for column in META_COLS if column in df.columns and column != id_col]
    long = df.melt(
        id_vars=[id_col, *meta],
        value_vars=list(date_map),
        var_name="date_column",
        value_name="rain_mm",
    )
    long["rain_mm"] = pd.to_numeric(long["rain_mm"], errors="coerce")
    long.loc[long["rain_mm"] < 0, "rain_mm"] = np.nan
    long["date"] = long["date_column"].map(date_map)
    long["time"] = long["date"].dt.to_period("M").dt.to_timestamp()
    long = long.dropna(subset=[id_col])
    return long.rename(columns={id_col: "station_id"})[
        ["station_id", "time", "rain_mm"]
    ]


def aggregate_hawaii(root: Path) -> pd.DataFrame:
    files = sorted(root.rglob("*.csv"))
    if not files:
        raise ValueError(f"Tidak ada CSV Hawaii di {root}")

    daily_parts: list[pd.DataFrame] = []
    failures: list[tuple[Path, Exception]] = []
    for path in files:
        try:
            daily_parts.append(station_monthly_from_file(path))
            print(f"[OK] {path.relative_to(root)}")
        except Exception as exc:
            failures.append((path, exc))
            print(f"[FAILED] {path}: {exc}", file=sys.stderr)
    if not daily_parts:
        raise RuntimeError(f"Semua {len(files)} CSV Hawaii gagal diproses")

    daily = pd.concat(daily_parts, ignore_index=True)
    station_monthly = (
        daily.groupby(["station_id", "time"])["rain_mm"]
        .mean()
        .rename("rain_mean_daily_mm")
        .reset_index()
    )
    regional = station_monthly.groupby("time")["rain_mean_daily_mm"].mean().to_frame()
    regional["n_stations"] = (
        station_monthly.dropna(subset=["rain_mean_daily_mm"])
        .groupby("time")["station_id"]
        .nunique()
    )
    regional = regional.reindex(MONTHS)
    regional["rain_total_mm"] = (
        regional["rain_mean_daily_mm"] * regional.index.days_in_month
    )
    regional.index.name = "time"
    regional = regional.reset_index()
    regional = regional[["time", "rain_mean_daily_mm", "n_stations", "rain_total_mm"]]
    regional.attrs["failed_files"] = failures
    return regional


def combine_rainfall(malaysia: pd.DataFrame, hawaii: pd.DataFrame) -> pd.DataFrame:
    """Align the monthly Malaysia and Hawaii rainfall features on one timeline."""
    malaysia_features = malaysia[["time", "rfh", "r1h"]].rename(
        columns={"rfh": "malaysia_rfh_mm", "r1h": "malaysia_r1h_mm"}
    )
    hawaii_features = hawaii[["time", "rain_total_mm"]].rename(
        columns={"rain_total_mm": "hawaii_rain_mm"}
    )
    comparison = pd.DataFrame({"time": MONTHS})
    comparison = comparison.merge(
        malaysia_features, on="time", how="left", validate="one_to_one"
    )
    comparison = comparison.merge(
        hawaii_features, on="time", how="left", validate="one_to_one"
    )
    return comparison


def find_malaysia_csv() -> Path:
    source_dir = DATASET_DIR / "data_rainfall"
    preferred = source_dir / "Malaysia.csv"
    if preferred.is_file():
        return preferred

    candidates = sorted(source_dir.glob("*.csv"))
    if len(candidates) != 1:
        names = ", ".join(str(path) for path in candidates) or "(tidak ada)"
        raise ValueError(
            f"Dibutuhkan tepat satu CSV Malaysia langsung di {source_dir}; "
            f"ditemukan {len(candidates)} kandidat: {names}. "
            "Pilih input secara eksplisit dengan --malaysia-csv."
        )
    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--malaysia-csv",
        type=Path,
        help=(
            "CSV mentah Malaysia (default: Malaysia.csv di dataset/data_rainfall; "
            "jika tidak ada, gunakan satu-satunya CSV yang ditemukan)"
        ),
    )
    parser.add_argument(
        "--hawaii-dir",
        type=Path,
        default=DATASET_DIR / "data_rainfall" / "Hawaii",
        help="Folder CSV harian Hawaii",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DATASET_DIR / "data_rainfall_monthly",
        help="Folder keluaran CSV perbandingan bulanan",
    )
    args = parser.parse_args()

    try:
        malaysia_csv = args.malaysia_csv or find_malaysia_csv()
        hawaii_dir = args.hawaii_dir.expanduser().resolve()
        output_dir = args.output_dir.expanduser().resolve()
        malaysia_csv = malaysia_csv.expanduser().resolve()
        if not malaysia_csv.is_file():
            raise FileNotFoundError(f"CSV Malaysia tidak ditemukan: {malaysia_csv}")
        if not hawaii_dir.is_dir():
            raise FileNotFoundError(f"Folder CSV Hawaii tidak ditemukan: {hawaii_dir}")

        malaysia = aggregate_malaysia(malaysia_csv)
        hawaii = aggregate_hawaii(hawaii_dir)
        failures = hawaii.attrs.pop("failed_files", [])
        comparison = combine_rainfall(malaysia, hawaii)
        output_dir.mkdir(parents=True, exist_ok=True)

        comparison_path = output_dir / "rainfall_comparison.csv"
        comparison.to_csv(comparison_path, index=False)
        warn_missing_months(malaysia, "Malaysia")
        warn_missing_months(hawaii, "Hawaii")
        print(f"Perbandingan Malaysia–Hawaii: {len(comparison)} bulan -> {comparison_path}")
        return 1 if failures else 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
