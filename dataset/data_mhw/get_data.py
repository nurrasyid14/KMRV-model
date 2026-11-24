import argparse
from pathlib import Path

import pandas as pd
import xarray as xr

# Tentukan path relatif terhadap lokasi script ini berada
CURRENT_DIR = Path(__file__).resolve().parent          # folder dataset/data_mhw
DATASET_DIR = CURRENT_DIR.parent                      # folder dataset

OUTPUT_DIR = CURRENT_DIR
CSV_PATH = OUTPUT_DIR / "mhw_labels.csv"

PERCENTILE = 0.9
MIN_DURATION = 5


def find_nc_file() -> Path:
    sst_dir = DATASET_DIR / "sst_5_wilayah"
    candidates = sorted(sst_dir.glob("sst_5_wilayah_*.nc"), reverse=True)
    if candidates:
        return candidates[0]
    return sst_dir / "sst_5_wilayah_2015_2026.nc"


def spatial_mean(da: xr.DataArray) -> pd.Series:
    dims = [d for d in da.dims if d != "time"]
    return da.mean(dim=dims).to_series()


def seasonal_threshold(series: pd.Series, q: float) -> pd.Series:
    return series.groupby(series.index.dayofyear).transform(lambda x: x.quantile(q))


def flag_mhw(series: pd.Series, threshold: pd.Series, min_duration: int) -> pd.Series:
    exceed = (series > threshold).astype(int)
    run_id = (exceed != exceed.shift()).cumsum()
    run_length = exceed.groupby(run_id).transform("size")
    return ((exceed == 1) & (run_length >= min_duration)).astype(int)


def compute_mhw(ds: xr.Dataset) -> pd.DataFrame:
    results = {}
    for var in ds.data_vars:
        region = var.removeprefix("sst_")
        sst = spatial_mean(ds[var])
        p90 = seasonal_threshold(sst, PERCENTILE)

        results[f"{region}_sst"] = sst
        results[f"{region}_p90"] = p90
        results[f"{region}_is_mhw"] = flag_mhw(sst, p90, MIN_DURATION)

    return pd.DataFrame(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Hitung label MHW dari NetCDF SST")
    parser.add_argument(
        "--nc-file",
        type=Path,
        default=find_nc_file(),
        help="Path file NetCDF SST 5 wilayah gabungan",
    )
    args = parser.parse_args()
    nc_file = args.nc_file.expanduser().resolve()

    if not nc_file.exists():
        raise FileNotFoundError(f"File {nc_file} tidak ditemukan.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Membuka dataset: {nc_file}")
    with xr.open_dataset(nc_file) as ds:
        df_mhw = compute_mhw(ds)

    df_mhw.to_csv(CSV_PATH)

    print(f"Perhitungan selesai! Label MHW tersimpan di: {CSV_PATH}")
    print("Ringkasan jumlah hari MHW:")
    for col in df_mhw.filter(like="_is_mhw"):
        print(f" - {col.removesuffix('_is_mhw')}: {df_mhw[col].sum()} hari MHW")


if __name__ == "__main__":
    main()
