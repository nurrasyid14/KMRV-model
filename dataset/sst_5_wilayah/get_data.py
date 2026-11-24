import argparse
import time
import pandas as pd
import requests
import xarray as xr
from urllib.parse import quote
from pathlib import Path

BASE_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.nc"

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR.mkdir(exist_ok=True)

# (latitude_min, latitude_max, longitude_min, longitude_max)
WILAYAH = {
    "Pasifik_Nino34": (-5.0, 5.0, -170.0, -120.0),
    "Selat_Makassar": (-5.0, 2.0, 116.0, 120.0),
    "Selat_Karimata": (-3.0, 2.0, 105.0, 110.0),
    "Selatan_Jawa": (-12.0, -8.0, 105.0, 115.0),
    "Maluku_Utara_Papua": (-3.0, 3.0, 125.0, 140.0),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Unduh data OISST SST 5 wilayah")
    parser.add_argument("--start-year", type=int, default=2015, help="Tahun awal (default: 2015)")
    parser.add_argument("--end-year", type=int, default=2026, help="Tahun akhir (default: 2026)")
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Unduh ulang file tahunan meskipun sudah ada",
    )
    return parser.parse_args()


def get_erddap_max_date(session: requests.Session) -> pd.Timestamp:
    info_url = "https://coastwatch.pfeg.noaa.gov/erddap/info/ncdcOisst21Agg_LonPM180/index.json"
    try:
        resp = session.get(info_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for row in data.get("table", {}).get("rows", []):
            if row[1] == "time" and row[2] == "actual_range":
                parts = [float(x.strip()) for x in row[4].split(",")]
                return pd.to_datetime(parts[1], unit="s", utc=True)
    except Exception as e:
        print(f"Catatan: gagal membaca batas waktu ERDDAP ({e}), menggunakan perkiraan.", flush=True)
    return pd.Timestamp.now(tz="UTC")


def main():
    args = parse_args()
    start_year = args.start_year
    end_year = args.end_year
    force_download = args.force_download

    output_file = OUTPUT_DIR / f"sst_5_wilayah_{start_year}_{end_year}.nc"
    legacy_file = OUTPUT_DIR / "sst_5_wilayah_2015_2025.nc"

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    max_erddap_dt = get_erddap_max_date(session)
    print(f"Batas observasi data SST di NOAA ERDDAP: {max_erddap_dt.strftime('%Y-%m-%d %H:%M UTC')}", flush=True)

    region_datasets = {}

    for nama, bounds in WILAYAH.items():
        lat_min, lat_max, lon_min, lon_max = bounds

        print(f"\nMemproses {nama}", flush=True)
        yearly_datasets = []

        for year in range(start_year, end_year + 1):
            file_path = OUTPUT_DIR / f"{nama}_{year}.nc"

            if not force_download and file_path.exists():
                try:
                    with xr.open_dataset(file_path) as opened:
                        ds_year = opened[["sst"]].load()
                    if "zlev" in ds_year.dims:
                        ds_year = ds_year.squeeze("zlev", drop=True)
                    if ds_year.sizes.get("time", 0) > 0:
                        yearly_datasets.append(ds_year)
                        print(f"  {year}: Menggunakan file lokal ({ds_year.sizes.get('time', 0)} timestamp)", flush=True)
                        continue
                except Exception as e:
                    print(f"  {year}: File lokal rusak ({e}), mengunduh ulang...", flush=True)

            start_dt = pd.Timestamp(f"{year}-01-01T12:00:00Z")
            end_dt = pd.Timestamp(f"{year}-12-31T12:00:00Z")

            if start_dt > max_erddap_dt:
                print(f"  {year}: Data belum tersedia di NOAA (data terakhir {max_erddap_dt.strftime('%Y-%m-%d')}). Dilewati.", flush=True)
                continue

            if end_dt > max_erddap_dt:
                end_dt = max_erddap_dt
                print(f"  {year}: Menyesuaikan batas akhir query ke {end_dt.strftime('%Y-%m-%d')} (data terbaru NOAA)", flush=True)

            start_date = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_date = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

            query = (
                f"sst[({start_date}):1:({end_date})]"
                f"[(0.0)]"
                f"[({lat_min}):1:({lat_max})]"
                f"[({lon_min}):1:({lon_max})]"
            )

            url = BASE_URL + "?" + quote(query, safe="[],():TZ.-")
            success = False

            for attempt in range(3):
                try:
                    if file_path.exists():
                        file_path.unlink()

                    response = session.get(url, timeout=180)
                    response.raise_for_status()

                    file_path.write_bytes(response.content)

                    # Buka dan muat data sebelum file ditutup
                    with xr.open_dataset(file_path) as opened:
                        ds_year = opened[["sst"]].load()

                    if "zlev" in ds_year.dims:
                        ds_year = ds_year.squeeze("zlev", drop=True)

                    yearly_datasets.append(ds_year)

                    print(f"  {year}: Berhasil diunduh ({ds_year.sizes.get('time', 0)} timestamp)", flush=True)

                    success = True
                    break

                except Exception as e:
                    print(f"  Gagal {year}, percobaan {attempt + 1}/3: {e}", flush=True)
                    time.sleep(3 * (attempt + 1))

            if not success:
                print(f"  Tahun {year} dilewati.", flush=True)

        if yearly_datasets:
            ds_region = xr.concat(yearly_datasets, dim="time", join="outer").sortby("time")

            # Hilangkan timestamp duplikat
            _, indices = __import__("numpy").unique(
                ds_region.time.values, return_index=True
            )
            ds_region = ds_region.isel(time=sorted(indices))

            # Buat nama dimensi unik untuk setiap wilayah
            ds_region = ds_region.rename(
                {
                    "latitude": f"latitude_{nama}",
                    "longitude": f"longitude_{nama}",
                    "sst": f"sst_{nama}",
                }
            )

            region_datasets[nama] = ds_region
            print(f"Total timestamp {nama}: {ds_region.sizes.get('time', 0)}", flush=True)

    if region_datasets:
        # Gabungkan tanpa menyatukan semua grid spasial
        ds_final = xr.merge(
            list(region_datasets.values()), join="outer", compat="no_conflicts"
        )

        ds_final.to_netcdf(output_file)

        print("\n=== DATA SELESAI ===", flush=True)
        print(ds_final, flush=True)
        print("\nFile tersimpan:", output_file.resolve(), flush=True)

        # Buat salinan atau link ke nama lama jika berbeda
        if output_file != legacy_file:
            try:
                ds_final.to_netcdf(legacy_file)
                print("Salinan kompatibilitas tersimpan:", legacy_file.resolve(), flush=True)
            except Exception as e:
                print(f"Catatan: tidak dapat memperbarui {legacy_file.name}: {e}", flush=True)

        for nama in region_datasets:
            var = f"sst_{nama}"
            print(
                f"{nama}: "
                f"dimensi {ds_final[var].dims}, "
                f"jumlah data valid "
                f"{int(ds_final[var].count().values):,}",
                flush=True,
            )

    else:
        print("Tidak ada data berhasil diunduh.", flush=True)

    session.close()


if __name__ == "__main__":
    main()
