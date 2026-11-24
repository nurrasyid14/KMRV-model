"""Climate data scrapers and downloaders for NOAA, CPC, and PSL sources.

Provides automated fetching of ONI, SOI, DMI, and OISST remote datasets.
When autoscrap is enabled in the pipeline, these functions are called
before QC and training.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"

URL_ONI = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
URL_SOI = "https://psl.noaa.gov/data/correlation/soi.data"
URL_DMI = "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data"
BASE_URL_ERDDAP = (
    "https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.nc"
)

WILAYAH = {
    "Pasifik_Nino34": (-5.0, 5.0, -170.0, -120.0),
    "Selat_Makassar": (-5.0, 2.0, 116.0, 120.0),
    "Selat_Karimata": (-3.0, 2.0, 105.0, 110.0),
    "Selatan_Jawa": (-12.0, -8.0, 105.0, 115.0),
    "Maluku_Utara_Papua": (-3.0, 3.0, 125.0, 140.0),
}


def download_oni(
    dest_dir: Path | None = None,
    timeout: int = 30,
) -> Path:
    """Download NOAA CPC ONI index and parse to CSV and raw txt."""
    output_dir = dest_dir or (DATASET_DIR / "data_oni")
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "oni.ascii.txt"
    csv_path = output_dir / "oni.csv"

    response = requests.get(
        URL_ONI,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=timeout,
    )
    response.raise_for_status()
    raw_path.write_bytes(response.content)

    df_oni = pd.read_csv(raw_path, sep=r"\s+")
    df_oni.to_csv(csv_path, index=False)
    logger.info("Successfully downloaded ONI to %s (%d rows)", csv_path, len(df_oni))
    return csv_path


def download_soi(
    dest_dir: Path | None = None,
    timeout: int = 30,
) -> Path:
    """Download NOAA PSL SOI index and parse to CSV."""
    output_dir = dest_dir or (DATASET_DIR / "data_soi")
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "soi.data"
    csv_path = output_dir / "soi.csv"

    response = requests.get(
        URL_SOI,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=timeout,
    )
    response.raise_for_status()
    raw_path.write_bytes(response.content)

    df = pd.read_csv(raw_path, skiprows=1, sep=r"\s+", header=None, dtype=str)
    df = df[df[0].str.match(r"^\d{4}$", na=False)].copy()
    df.columns = ["Year", *range(1, 13)]
    df = df.apply(pd.to_numeric, errors="coerce")

    df_soi = (
        df.melt(id_vars="Year", var_name="Month", value_name="SOI")
        .replace({"SOI": {-99.99: np.nan}})
        .dropna(subset=["SOI"])
        .astype({"Year": int, "Month": int})
        .sort_values(["Year", "Month"])
        .reset_index(drop=True)
    )
    df_soi.to_csv(csv_path, index=False)
    logger.info("Successfully downloaded SOI to %s (%d rows)", csv_path, len(df_soi))
    return csv_path


def download_dmi(
    dest_dir: Path | None = None,
    timeout: int = 30,
) -> Path:
    """Download NOAA PSL DMI index and parse to CSV."""
    output_dir = dest_dir or (DATASET_DIR / "data_dmi")
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "dmi.had.long.data"
    csv_path = output_dir / "dmi.csv"

    response = requests.get(
        URL_DMI,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=timeout,
    )
    response.raise_for_status()
    raw_path.write_bytes(response.content)

    df = pd.read_csv(raw_path, skiprows=1, sep=r"\s+", header=None, dtype=str)
    df = df[df[0].str.match(r"^\d{4}$", na=False)].copy()
    df.columns = ["Year", *range(1, 13)]
    df = df.apply(pd.to_numeric, errors="coerce")

    df_dmi = (
        df.melt(id_vars="Year", var_name="Month", value_name="DMI")
        .replace({"DMI": {-9999.0: np.nan}})
        .dropna(subset=["DMI"])
        .astype({"Year": int, "Month": int})
        .sort_values(["Year", "Month"])
        .reset_index(drop=True)
    )
    df_dmi.to_csv(csv_path, index=False)
    logger.info("Successfully downloaded DMI to %s (%d rows)", csv_path, len(df_dmi))
    return csv_path


def download_sst(
    dest_dir: Path | None = None,
    regions: list[str] | None = None,
    start_year: int = 2024,
    end_year: int = 2025,
    timeout: int = 60,
) -> list[Path]:
    """Download regional OISST NetCDF files from ERDDAP."""
    output_dir = dest_dir or (DATASET_DIR / "sst_5_wilayah")
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded_files: list[Path] = []
    target_regions = regions or list(WILAYAH.keys())

    session = requests.Session()
    try:
        for name in target_regions:
            if name not in WILAYAH:
                continue
            lat_min, lat_max, lon_min, lon_max = WILAYAH[name]
            for year in range(start_year, end_year + 1):
                start_date = f"{year}-01-01T12:00:00Z"
                end_date = f"{year}-12-31T12:00:00Z"
                query = (
                    f"sst[({start_date}):1:({end_date})]"
                    f"[(0.0)]"
                    f"[({lat_min}):1:({lat_max})]"
                    f"[({lon_min}):1:({lon_max})]"
                )
                url = BASE_URL_ERDDAP + "?" + quote(query, safe="[],():TZ.-")
                file_path = output_dir / f"{name}_{year}.nc"
                try:
                    res = session.get(url, timeout=timeout)
                    res.raise_for_status()
                    file_path.write_bytes(res.content)
                    downloaded_files.append(file_path)
                    logger.info("Downloaded SST: %s", file_path.name)
                except Exception as exc:
                    logger.warning("Failed downloading SST for %s %d: %s", name, year, exc)
    finally:
        session.close()

    return downloaded_files


def download_all_sources(
    dataset_dir: Path | None = None,
    include_sst: bool = False,
    timeout: int = 30,
) -> dict[str, Any]:
    """Execute all data download scrapers before QC and training."""
    base_dir = dataset_dir or DATASET_DIR
    results: dict[str, Any] = {}

    try:
        results["oni"] = str(download_oni(base_dir / "data_oni", timeout=timeout))
    except Exception as exc:
        logger.warning("Auto-scrap ONI failed: %s", exc)
        results["oni"] = None

    try:
        results["soi"] = str(download_soi(base_dir / "data_soi", timeout=timeout))
    except Exception as exc:
        logger.warning("Auto-scrap SOI failed: %s", exc)
        results["soi"] = None

    try:
        results["dmi"] = str(download_dmi(base_dir / "data_dmi", timeout=timeout))
    except Exception as exc:
        logger.warning("Auto-scrap DMI failed: %s", exc)
        results["dmi"] = None

    if include_sst:
        try:
            downloaded_sst = download_sst(base_dir / "sst_5_wilayah", timeout=timeout)
            results["sst"] = [str(p) for p in downloaded_sst]
        except Exception as exc:
            logger.warning("Auto-scrap SST failed: %s", exc)
            results["sst"] = []
    else:
        results["sst"] = "skipped (sst archives present locally)"

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Running download_all_sources...")
    summary = download_all_sources()
    print("Download summary:", summary)
