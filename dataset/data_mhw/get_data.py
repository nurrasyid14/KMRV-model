from pathlib import Path

import pandas as pd
import xarray as xr

# Tentukan path relatif terhadap lokasi script ini berada
    # Tentukan path relatif terhadap lokasi script ini berada
CURRENT_DIR = Path(__file__).resolve().parent          # folder dataset/data_mhw
DATASET_DIR = CURRENT_DIR.parent                      # folder dataset

NC_FILE = DATASET_DIR / "sst_5_wilayah" / "sst_5_wilayah_2015_2025.nc"
OUTPUT_DIR = CURRENT_DIR
CSV_PATH = OUTPUT_DIR / "mhw_labels.csv"

PERCENTILE = 0.9
MIN_DURATION = 5


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
    if not NC_FILE.exists():
        raise FileNotFoundError(f"File {NC_FILE} tidak ditemukan.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Membuka dataset: {NC_FILE}")
    with xr.open_dataset(NC_FILE) as ds:
        df_mhw = compute_mhw(ds)

    df_mhw.to_csv(CSV_PATH)

    print(f"Perhitungan selesai! Label MHW tersimpan di: {CSV_PATH}")
    print("Ringkasan jumlah hari MHW (2015–2025):")
    for col in df_mhw.filter(like="_is_mhw"):
        print(f" - {col.removesuffix('_is_mhw')}: {df_mhw[col].sum()} hari MHW")


if __name__ == "__main__":
    main()
