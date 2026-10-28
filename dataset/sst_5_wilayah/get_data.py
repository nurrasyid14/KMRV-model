import time
import requests
import xarray as xr
from urllib.parse import quote
from pathlib import Path

BASE_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.nc"

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "sst_5_wilayah_2015_2025.nc"

START_YEAR = 2015
END_YEAR = 2025

# (latitude_min, latitude_max, longitude_min, longitude_max)
WILAYAH = {
    "Pasifik_Nino34": (-5.0, 5.0, -170.0, -120.0),
    "Selat_Makassar": (-5.0, 2.0, 116.0, 120.0),
    "Selat_Karimata": (-3.0, 2.0, 105.0, 110.0),
    "Selatan_Jawa": (-12.0, -8.0, 105.0, 115.0),
    "Maluku_Utara_Papua": (-3.0, 3.0, 125.0, 140.0),
}

session = requests.Session()
region_datasets = {}

for nama, bounds in WILAYAH.items():
    lat_min, lat_max, lon_min, lon_max = bounds

    print(f"\nMemproses {nama}")
    yearly_datasets = []

    for year in range(START_YEAR, END_YEAR + 1):
        start_date = f"{year}-01-01T12:00:00Z"
        end_date = f"{year}-12-31T12:00:00Z"

        query = (
            f"sst[({start_date}):1:({end_date})]"
            f"[(0.0)]"
            f"[({lat_min}):1:({lat_max})]"
            f"[({lon_min}):1:({lon_max})]"
        )

        url = BASE_URL + "?" + quote(query, safe="[],():TZ.-")

        file_path = OUTPUT_DIR / f"{nama}_{year}.nc"
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

                print(f"  {year}: {ds_year.sizes.get('time', 0)} timestamp")

                success = True
                break

            except Exception as e:
                print(f"  Gagal {year}, percobaan {attempt + 1}/3: {e}")
                time.sleep(3 * (attempt + 1))

        if not success:
            print(f"  Tahun {year} dilewati.")

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

        print(f"Total timestamp {nama}: {ds_region.sizes.get('time', 0)}")

if region_datasets:
    # Gabungkan tanpa menyatukan semua grid spasial
    ds_final = xr.merge(
        list(region_datasets.values()), join="outer", compat="no_conflicts"
    )

    ds_final.to_netcdf(OUTPUT_FILE)

    print("\n=== DATA SELESAI ===")
    print(ds_final)
    print("\nFile tersimpan:", OUTPUT_FILE.resolve())

    for nama in region_datasets:
        var = f"sst_{nama}"
        print(
            f"{nama}: "
            f"dimensi {ds_final[var].dims}, "
            f"jumlah data valid "
            f"{int(ds_final[var].count().values):,}"
        )

else:
    print("Tidak ada data berhasil diunduh.")

session.close()
