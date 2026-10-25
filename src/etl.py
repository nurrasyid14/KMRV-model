from pathlib import Path
from typing import Union, List
import pandas as pd
import xarray as xr
from src.utils import NCEncoder

class ExploratoryDataAnalysis:
    """
    Performs automated exploratory data analysis (EDA) across a directory 
    containing one or more NetCDF (.nc) files recursively, and mirrors 
    them as Zarr stores into data/processed/zarr/<relative_path>.
    """
    def __init__(self, data_dir: Union[str, Path], output_base_dir: Union[str, Path] = "data/processed/zarr"):
        self.data_dir = Path(data_dir)
        self.output_base_dir = Path(output_base_dir)
        
        if not self.data_dir.exists() or not self.data_dir.is_dir():
            raise NotADirectoryError(f"Provided path is not a valid directory: {self.data_dir}")

    def discover_files(self) -> List[Path]:
        """Recursively finds all .nc files within the directory and its subfolders."""
        return sorted(list(self.data_dir.rglob("*.nc")))

    def process_and_report(self) -> pd.DataFrame:
        """
        Converts discovered NetCDF files to Zarr and reports their stored variables.
        """
        nc_files = self.discover_files()
        
        if not nc_files:
            print(f"No .nc files found in directory: {self.data_dir}")
            return pd.DataFrame()

        print(f"Found {len(nc_files)} NetCDF file(s). Converting to Zarr & running EDA summary...\n")
        report_records = []

        for file_path in nc_files:
            relative_path = file_path.relative_to(self.data_dir)
            output_zarr_path = self.output_base_dir / relative_path.with_suffix(".zarr")

            encoder = NCEncoder(file_path)
            try:
                encoder.encode_to_zarr(output_zarr_path)
                encoder.close()

                with xr.open_zarr(output_zarr_path) as ds:
                    variables = list(ds.data_vars)
                    for var_name in variables:
                        var_array = ds[var_name]
                        report_records.append({
                            "file_name": file_path.name,
                            "relative_path": str(relative_path),
                            "saved_zarr_path": str(output_zarr_path),
                            "variable": var_name,
                            "shape": str(var_array.shape),
                            "dtype": str(var_array.dtype),
                            "has_nans": bool(var_array.isnull().any().compute().item())
                        })

                print(f"[SUCCESS] Processed & Saved: {output_zarr_path}")

            except Exception as e:
                print(f"[ERROR] Failed processing {file_path.name}: {e}")
            finally:
                encoder.close()

        return pd.DataFrame(report_records)


if __name__ == "__main__":
    print("=== Menjalankan Proses EDA & Konversi Zarr ===")
    data_dir = "dataset/sst_5_wilayah"
    output_zarr_dir = "data/processed/zarr"
    report_csv_path = Path("data/processed/eda_report.csv")
    report_csv_path.parent.mkdir(parents=True, exist_ok=True)

    eda = ExploratoryDataAnalysis(data_dir=data_dir, output_base_dir=output_zarr_dir)
    df_report = eda.process_and_report()

    if not df_report.empty:
        df_report.to_csv(report_csv_path, index=False)
        print(f"\n[SELESAI] Laporan metadata disimpan ke: {report_csv_path}")
        print(f"Total file & variabel yang tercatat: {len(df_report)}")
        print("\nContoh ringkasan laporan:")
        print(df_report[["file_name", "variable", "shape", "has_nans"]].head(10).to_string())
    else:
        print("[PERINGATAN] Tidak ada data yang berhasil diproses.")
