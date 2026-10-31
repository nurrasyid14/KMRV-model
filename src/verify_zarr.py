#!/usr/bin/env python
"""Verify every dataset group in dataset/climate_dataset.zarr."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import zarr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STORE = PROJECT_ROOT / "dataset" / "climate_dataset.zarr"
START = pd.Timestamp("2015-01-01")
END = pd.Timestamp("2025-12-01")
MONTHS = pd.date_range(START, END, freq="MS")
SST_SKIP_NAME_KEYWORDS = (("selatan", "jawa"), ("maluku", "utara"))


def stored_groups(store: Path) -> list[str]:
    root = zarr.open_group(str(store), mode="r")
    groups: list[str] = []

    def collect(name: str, node: object) -> None:
        if hasattr(node, "array_keys") and list(node.array_keys()):
            groups.append(name)

    root.visititems(collect)
    return sorted(groups)


def verify(store: Path) -> int:
    if not store.is_dir():
        print(f"ERROR: Zarr store tidak ditemukan: {store}", file=sys.stderr)
        return 2
    try:
        groups = stored_groups(store)
    except Exception as exc:
        print(f"ERROR: tidak dapat membaca Zarr store: {exc}", file=sys.stderr)
        return 2
    if not groups:
        print(f"ERROR: tidak ditemukan group dataset di {store}", file=sys.stderr)
        return 1

    rows = []
    errors: list[str] = []
    for group in groups:
        normalized = re.sub(r"[^a-z0-9]+", "_", group.lower()).strip("_")
        words = set(normalized.split("_"))
        if "data_rainfall" in words:
            errors.append(f"{group}: group rainfall mentah tidak boleh ada")
        if any(set(keywords).issubset(words) for keywords in SST_SKIP_NAME_KEYWORDS):
            errors.append(f"{group}: group SST wilayah yang dikecualikan ditemukan")

        try:
            with xr.open_zarr(str(store), group=group, consolidated=False) as ds:
                dims = dict(ds.sizes)
                variables = list(ds.data_vars)
                if "time" not in ds.coords:
                    errors.append(f"{group}: koordinat time tidak ditemukan")
                    rows.append((group, dims, variables, 0, "time tidak tersedia"))
                    continue
                time = pd.DatetimeIndex(ds["time"].values)
                missing = MONTHS.difference(time)
                missing_text = (
                    ", ".join(value.strftime("%Y-%m") for value in missing) or "-"
                )
                rows.append((group, dims, variables, len(time), missing_text))
                if ds["time"].dtype != np.dtype("datetime64[ns]"):
                    errors.append(f"{group}: time bukan datetime64[ns] ({ds['time'].dtype})")
                if len(time) == 0:
                    errors.append(f"{group}: koordinat time kosong")
                    continue
                if time.min() != START:
                    errors.append(f"{group}: time minimum {time.min()} bukan {START}")
                if time.max() > END:
                    errors.append(f"{group}: time maksimum {time.max()} melewati {END}")
                if not (time.day == 1).all():
                    errors.append(f"{group}: ada tanggal time yang bukan awal bulan")
                if time.has_duplicates:
                    errors.append(f"{group}: koordinat time memiliki duplikat")
                if not time.is_monotonic_increasing:
                    errors.append(f"{group}: koordinat time tidak terurut naik")
                if len(time) != len(MONTHS):
                    errors.append(f"{group}: ditemukan {len(time)} bulan, seharusnya 132")
        except Exception as exc:
            errors.append(f"{group}: gagal dibuka/diperiksa: {type(exc).__name__}: {exc}")

    headers = ("group", "dims", "variables", "months", "missing months")
    widths = [
        max(len(headers[index]), *(len(str(row[index])) for row in rows))
        for index in range(len(headers))
    ]
    print(" | ".join(name.ljust(widths[index]) for index, name in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(str(value).ljust(widths[index]) for index, value in enumerate(row)))
    if errors:
        print("\nVerification failures:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"\nOK: {len(groups)} group lolos verifikasi.")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE, help="Path Zarr store")
    args = parser.parse_args()
    return verify(args.store.expanduser().resolve())


if __name__ == "__main__":
    raise SystemExit(main())
