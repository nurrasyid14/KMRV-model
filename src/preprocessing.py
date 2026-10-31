#!/usr/bin/env python
"""
Convert monthly CSV and NetCDF climate sources into one hierarchical Zarr store.

Run ``python src/rainfall_prepro.py`` first to create monthly rainfall CSVs,
then run ``python src/preprocessing.py``. Both commands work from any directory.

All time-series groups cover January 2015 through December 2025 at monthly
frequency. Daily MHW label time series are averaged by month; if an MHW source
instead contains event start/end dates, each event is counted in every month it
is active and its intensity mean and maximum are calculated for those months.
"""

from __future__ import annotations

import argparse
import inspect
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"
START = pd.Timestamp("2015-01-01")
END = pd.Timestamp("2025-12-31")
MONTHS = pd.date_range(START, END, freq="MS")

NETCDF_EXTENSIONS = {".nc", ".nc4", ".cdf", ".netcdf"}
CSV_EXTENSION = ".csv"
EXCLUDE_TOP_DIRS = {"data_rainfall"}
SST_SKIP_NAME_KEYWORDS = (("selatan", "jawa"), ("maluku", "utara"))
COORD_ALIASES = {
    "time": ("time", "valid_time", "date", "datetime", "times"),
    "lat": ("lat", "latitude", "nav_lat", "y"),
    "lon": ("lon", "longitude", "nav_lon", "x"),
}
SEASON_CENTER_MONTH = {
    "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
    "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
}
ZARR_FORMAT_SUPPORTED = "zarr_format" in inspect.signature(xr.Dataset.to_zarr).parameters


def safe_name(value: str) -> str:
    """Convert a path component into a Zarr-safe group component."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "_", value)
    return value.strip("_") or "unnamed"


def group_for_file(path: Path, input_dir: Path) -> str:
    """Build a group from the relative path, combining annual SST files by region."""
    relative = path.relative_to(input_dir)
    parts = list(relative.with_suffix("").parts)
    if parts and safe_name(parts[0]) == "sst_5_wilayah":
        parts[-1] = re.sub(r"_\d{4}$", "", parts[-1])
    return "/".join(safe_name(part) for part in parts)


def is_excluded_sst(path: Path, input_dir: Path) -> bool:
    relative = path.relative_to(input_dir)
    if not relative.parts or safe_name(relative.parts[0]) != "sst_5_wilayah":
        return False
    normalized = re.sub(r"[^a-z0-9]+", "_", path.stem.lower()).strip("_")
    words = set(normalized.split("_"))
    return any(set(keywords).issubset(words) for keywords in SST_SKIP_NAME_KEYWORDS)


def normalize_netcdf(ds: xr.Dataset) -> xr.Dataset:
    """Normalize common time/latitude/longitude coordinate names."""
    existing = set(ds.variables) | set(ds.dims)
    rename = {}
    for standard, aliases in COORD_ALIASES.items():
        if standard not in existing:
            match = next((name for name in aliases if name in existing), None)
            if match is not None and match != standard:
                rename[match] = standard
    if rename:
        ds = ds.rename(rename)
    if "time" not in ds.coords:
        raise ValueError("NetCDF tidak memiliki koordinat waktu yang dikenali")

    time_index = ds.indexes.get("time")
    if isinstance(time_index, xr.CFTimeIndex):
        try:
            ds = ds.convert_calendar("proleptic_gregorian", use_cftime=False)
        except (TypeError, ValueError):
            ds = ds.assign_coords(time=time_index.to_datetimeindex())
    return ds


def to_month_start(values: pd.DatetimeIndex | pd.Series) -> pd.DatetimeIndex | pd.Series:
    """Normalize dates to the first day of their month."""
    if isinstance(values, pd.Series):
        return values.dt.to_period("M").dt.to_timestamp()
    return pd.DatetimeIndex(values).to_period("M").to_timestamp()


def complete_monthly_dataset(ds: xr.Dataset) -> xr.Dataset:
    """Sort, combine duplicate months, and reindex to the full required calendar."""
    if "time" not in ds.coords:
        raise ValueError("Dataset tidak memiliki koordinat time")
    normalized = pd.DatetimeIndex(ds["time"].values).to_period("M").to_timestamp()
    ds = ds.assign_coords(time=normalized)
    ds = ds.groupby("time").mean(keep_attrs=True)
    ds = ds.sortby("time").reindex(time=MONTHS)
    return ds


def monthly_netcdf(path: Path) -> xr.Dataset:
    """Slice before monthly aggregation and load only the reduced result."""
    try:
        opened = xr.open_dataset(path, chunks={})
    except (ImportError, ValueError):
        opened = xr.open_dataset(path)
    with opened:
        ds = normalize_netcdf(opened)
        ds = ds.sel(time=slice(START, END))
        if ds.sizes.get("time", 0) == 0:
            raise ValueError(f"Tidak ada data waktu dalam rentang {START:%Y-%m}–{END:%Y-%m}")

        time_index = pd.DatetimeIndex(ds["time"].values)
        median_step = time_index.to_series().diff().dropna().dt.total_seconds().median()
        if pd.isna(median_step) or median_step / 86400 < 28:
            ds = ds.resample(time="MS").mean(keep_attrs=True)
        else:
            ds = ds.assign_coords(time=to_month_start(time_index))
        ds = ds.load()

    if "time" not in ds.coords:
        raise ValueError(f"Tidak ada koordinat time yang dapat diagregasi: {path}")
    months = pd.DatetimeIndex(ds["time"].values).to_period("M").to_timestamp()
    ds = ds.assign_coords(time=months).groupby("time").mean(keep_attrs=True)
    ds = ds.sortby("time")
    for variable in ds.variables:
        ds[variable].encoding.clear()
    return ds


def _column_map(df: pd.DataFrame) -> dict[str, object]:
    return {str(column).strip().lower(): column for column in df.columns}


def _event_monthly(df: pd.DataFrame, columns: dict[str, object]) -> pd.DataFrame | None:
    start_col = next(
        (columns[name] for name in ("start_date", "event_start", "start", "begin")
         if name in columns),
        None,
    )
    end_col = next(
        (columns[name] for name in ("end_date", "event_end", "end", "finish")
         if name in columns),
        None,
    )
    if start_col is None or end_col is None:
        return None

    intensity_col = next(
        (columns[name] for name in ("intensity", "intensity_mean", "mean_intensity")
         if name in columns),
        None,
    )
    starts = pd.to_datetime(df[start_col], errors="coerce")
    ends = pd.to_datetime(df[end_col], errors="coerce")
    valid = starts.notna() & ends.notna() & (ends >= starts)
    if not valid.any():
        raise ValueError("Kolom tanggal mulai/akhir event MHW tidak berisi rentang yang valid")
    intensities = (
        pd.to_numeric(df[intensity_col], errors="coerce")
        if intensity_col is not None
        else pd.Series(np.nan, index=df.index)
    )
    monthly_events: dict[pd.Timestamp, list[float]] = {}
    for start, end, intensity in zip(starts[valid], ends[valid], intensities[valid]):
        first = max(start.to_period("M").to_timestamp(), MONTHS[0])
        last = min(end.to_period("M").to_timestamp(), MONTHS[-1])
        if first > last:
            continue
        for month in pd.date_range(first, last, freq="MS"):
            monthly_events.setdefault(month, []).append(float(intensity))

    result = pd.DataFrame(index=MONTHS)
    result["event_count"] = pd.Series(
        {month: len(values) for month, values in monthly_events.items()}, dtype="float64"
    )
    result["event_count"] = result["event_count"].fillna(0)
    result["intensity_mean"] = pd.Series(
        {month: pd.Series(values, dtype="float64").mean()
         for month, values in monthly_events.items()},
        dtype="float64",
    )
    result["intensity_max"] = pd.Series(
        {month: pd.Series(values, dtype="float64").max()
         for month, values in monthly_events.items()},
        dtype="float64",
    )
    result.index.name = "time"
    return result


def csv_to_dataset(path: Path) -> xr.Dataset:
    """Parse date, index, or MHW event CSVs into a unique monthly time index."""
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"CSV kosong: {path}")
    df = df.dropna(axis=1, how="all")
    columns = _column_map(df)

    if path.parent.name.lower() == "data_mhw":
        event_frame = _event_monthly(df, columns)
        if event_frame is not None:
            return xr.Dataset.from_dataframe(event_frame)

    season_col = columns.get("seas") or columns.get("season")
    year_col = columns.get("yr") or columns.get("year")
    if season_col is not None and year_col is not None:
        seasons = df[season_col].astype(str).str.upper().str.strip()
        years = pd.to_numeric(df[year_col], errors="coerce")
        dates = [
            pd.Timestamp(year=int(year), month=SEASON_CENTER_MONTH[season], day=1)
            if pd.notna(year) and season in SEASON_CENTER_MONTH
            else pd.NaT
            for season, year in zip(seasons, years)
        ]
        df["time"] = pd.to_datetime(dates)
        df = df.loc[df["time"].notna()].copy()
        drop_cols = [season_col, year_col]
    else:
        year_col = columns.get("year", columns.get("yr"))
        month_col = columns.get("month", columns.get("mo"))
        date_col = next(
            (columns[name] for name in ("time", "date", "datetime", "timestamp")
             if name in columns),
            None,
        )
        if date_col is not None:
            df["time"] = pd.to_datetime(df[date_col], errors="coerce")
            drop_cols = [date_col]
        elif year_col is not None and month_col is not None:
            df["time"] = pd.to_datetime(
                {
                    "year": pd.to_numeric(df[year_col], errors="coerce"),
                    "month": pd.to_numeric(df[month_col], errors="coerce"),
                    "day": 1,
                },
                errors="coerce",
            )
            drop_cols = [year_col, month_col]
        else:
            raise ValueError(f"Kolom tanggal/bulan tidak ditemukan pada {path}")

    df = df.loc[df["time"].notna()].copy()
    df = df.loc[df["time"].between(START, END)].copy()
    if df.empty:
        raise ValueError(f"Tidak ada data waktu dalam rentang {START:%Y-%m}–{END:%Y-%m}: {path}")

    values = df.drop(columns=[*drop_cols, "time"], errors="ignore")
    numeric = values.apply(pd.to_numeric, errors="coerce")
    numeric = numeric.loc[:, numeric.notna().any()]
    if numeric.empty:
        raise ValueError(f"Tidak ada kolom numerik untuk agregasi bulanan: {path}")
    numeric.index = pd.DatetimeIndex(df["time"], name="time")
    numeric.index = to_month_start(numeric.index)
    numeric.index.name = "time"
    numeric = numeric.groupby(level="time").mean(numeric_only=True)
    numeric = numeric.reindex(MONTHS)
    numeric.index.name = "time"
    return xr.Dataset.from_dataframe(numeric)


def clean_attrs(ds: xr.Dataset, sources: list[Path]) -> xr.Dataset:
    ds.attrs["source_files"] = ", ".join(path.name for path in sources)
    ds.attrs["preprocessing_note"] = (
        "Time sliced to 2015-2025 and normalized to monthly starts; "
        "spatial dimensions are preserved."
    )
    return ds


def discover_files(input_dir: Path, output_path: Path) -> list[Path]:
    files = []
    for path in input_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in NETCDF_EXTENSIONS | {CSV_EXTENSION}:
            continue
        try:
            path.resolve().relative_to(output_path)
            continue
        except ValueError:
            pass
        files.append(path)
    return sorted(files)


def write_group(
    ds: xr.Dataset,
    output_path: Path,
    group: str,
    zarr_format: int | None,
) -> None:
    options = {
        "group": group,
        "mode": "a",
        "consolidated": False,
    }
    if ZARR_FORMAT_SUPPORTED:
        options["zarr_format"] = zarr_format
    elif zarr_format is not None:
        raise RuntimeError(
            "Versi xarray terpasang tidak mendukung argumen zarr_format; "
            "jalankan tanpa --zarr-format."
        )
    ds.to_zarr(str(output_path), **options)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DATASET_DIR,
        help="Folder sumber CSV dan NetCDF",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DATASET_DIR / "climate_dataset.zarr",
        help="Path direktori Zarr keluaran",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Ganti direktori Zarr keluaran yang sudah ada",
    )
    parser.add_argument(
        "--zarr-format",
        type=int,
        choices=(2, 3),
        default=2 if ZARR_FORMAT_SUPPORTED else None,
        help="Format Zarr; default 2 bila didukung xarray terpasang",
    )
    args = parser.parse_args()

    input_dir = args.input_dir.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    if not input_dir.is_dir():
        print(f"ERROR: direktori input tidak ditemukan: {input_dir}", file=sys.stderr)
        return 2
    if output_path.exists() and not args.overwrite:
        print(
            f"ERROR: output sudah ada: {output_path}. "
            "Gunakan --overwrite atau pilih --output lain.",
            file=sys.stderr,
        )
        return 2

    files = discover_files(input_dir, output_path)
    if not files:
        print(f"ERROR: tidak ditemukan CSV/NetCDF di {input_dir}", file=sys.stderr)
        return 2

    skipped: set[Path] = set()
    processable: list[Path] = []
    for path in files:
        relative = path.relative_to(input_dir)
        if relative.parts and safe_name(relative.parts[0]) in EXCLUDE_TOP_DIRS:
            skipped.add(path)
            print(f"[SKIP] {relative}: direktori top-level dikecualikan")
        elif is_excluded_sst(path, input_dir):
            skipped.add(path)
            print(f"[SKIP] {relative}: SST wilayah dikecualikan berdasarkan nama")
        else:
            processable.append(path)

    if output_path.exists():
        shutil.rmtree(output_path)

    grouped_files: dict[str, list[Path]] = {}
    failures: dict[Path, str] = {}
    for path in processable:
        grouped_files.setdefault(group_for_file(path, input_dir), []).append(path)

    final_groups: list[str] = []
    for group, group_files in sorted(grouped_files.items()):
        print(f"[PROCESS] {len(group_files)} file -> group='{group}'")
        try:
            if all(path.suffix.lower() in NETCDF_EXTENSIONS for path in group_files):
                datasets = [monthly_netcdf(path) for path in group_files]
                ds = xr.concat(datasets, dim="time") if len(datasets) > 1 else datasets[0]
                ds = complete_monthly_dataset(ds)
            elif len(group_files) == 1 and group_files[0].suffix.lower() == CSV_EXTENSION:
                ds = csv_to_dataset(group_files[0])
            else:
                raise ValueError("Beberapa sumber dengan format berbeda berbagi nama group")

            ds = clean_attrs(ds, group_files)
            for variable in ds.variables:
                ds[variable].encoding.clear()
            write_group(ds, output_path, group, args.zarr_format)
            final_groups.append(group)
            print(
                f"[OK] {group}: dims={dict(ds.sizes)}; "
                f"vars={list(ds.data_vars)}; months={ds.sizes.get('time', 0)}"
            )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            for path in group_files:
                failures[path] = error
                print(f"[FAILED] {path.relative_to(input_dir)}: {error}", file=sys.stderr)

    successful = len(processable) - len(failures)
    print("\n=== SUMMARY ===")
    print(f"Files found: {len(files)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Successfully written: {successful}")
    print(f"Failed: {len(failures)}")
    print(f"Zarr store: {output_path}")
    print("Final groups:")
    for group in sorted(final_groups):
        print(f"- {group}")
    if failures:
        print("\nFailures:")
        for path, error in failures.items():
            print(f"- {path.relative_to(input_dir)}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
