from pathlib import Path
from typing import Union, List, Optional
import pandas as pd
import torch
from src.utils import NCEncoder

class ExploratoryDataAnalysis:
    """
    Performs automated exploratory data analysis (EDA) across a directory 
    containing one or more NetCDF (.nc) files recursively, and mirrors 
    the processed PyTorch tensors into data/processed/pt/<relative_path>.
    """
    def __init__(self, data_dir: Union[str, Path], output_base_dir: Union[str, Path] = "data/processed/pt"):
        self.data_dir = Path(data_dir)
        self.output_base_dir = Path(output_base_dir)
        
        if not self.data_dir.exists() or not self.data_dir.is_dir():
            raise NotADirectoryError(f"Provided path is not a valid directory: {self.data_dir}")

    def discover_files(self) -> List[Path]:
        """Recursively finds all .nc files within the directory and its subfolders."""
        return sorted(list(self.data_dir.rglob("*.nc")))

    def process_and_report(self, variable_name: str = 'sst', fill_value: float = 0.0) -> pd.DataFrame:
        """
        Scans all discovered NetCDF files, extracts structural metadata, 
        converts them to PyTorch tensors, and mirrors the path under data/processed/pt/.
        """
        nc_files = self.discover_files()
        
        if not nc_files:
            print(f"No .nc files found in directory: {self.data_dir}")
            return pd.DataFrame()

        print(f"Found {len(nc_files)} NetCDF file(s). Processing tensors & running EDA summary...\n")
        report_records = []

        for file_path in nc_files:
            # 1. Calculate relative path to mirror directory structure
            relative_path = file_path.relative_to(self.data_dir)
            output_pt_path = self.output_base_dir / relative_path.with_suffix('.pt')
            
            # 2. Ensure destination subdirectories exist
            output_pt_path.parent.mkdir(parents=True, exist_ok=True)

            encoder = NCEncoder(file_path)
            try:
                ds = encoder.open_dataset()
                
                file_name = file_path.name
                dimensions = dict(ds.sizes)
                variables = list(ds.data_vars.keys())
                
                # Check if the requested variable exists, else fall back or report
                target_var = variable_name if variable_name in ds else variables[0]
                
                # Process to tensor using NCEncoder method logic
                tensor_data = encoder.process_to_tensor(variable_name=target_var, fill_value=fill_value)
                
                # Save tensor to mirrored path
                torch.save(tensor_data, output_pt_path)

                # Record metadata for EDA report
                for var_name in variables:
                    var_array = ds[var_name]
                    report_records.append({
                        "file_name": file_name,
                        "relative_path": str(relative_path),
                        "saved_tensor_path": str(output_pt_path),
                        "variable": var_name,
                        "shape": str(var_array.shape),
                        "dtype": str(var_array.dtype),
                        "has_nans": bool(pd.isnull(var_array.values).any())
                    })
                    
                print(f"[SUCCESS] Processed & Saved: {output_pt_path}")

            except Exception as e:
                print(f"[ERROR] Failed processing {file_path.name}: {e}")
            finally:
                encoder.close()

        return pd.DataFrame(report_records)


if __name__ == "__main__":
    print("=== Menjalankan Proses EDA & Ekstraksi Tensor .pt ===")
    data_dir = "dataset/sst_5_wilayah"
    output_pt_dir = "data/processed/pt"
    report_csv_path = Path("data/processed/eda_report.csv")
    report_csv_path.parent.mkdir(parents=True, exist_ok=True)

    eda = ExploratoryDataAnalysis(data_dir=data_dir, output_base_dir=output_pt_dir)
    df_report = eda.process_and_report(variable_name="sst")

    if not df_report.empty:
        df_report.to_csv(report_csv_path, index=False)
        print(f"\n[SELESAI] Laporan metadata disimpan ke: {report_csv_path}")
        print(f"Total file & variabel yang tercatat: {len(df_report)}")
        print("\nContoh ringkasan laporan:")
        print(df_report[["file_name", "variable", "shape", "has_nans"]].head(10).to_string())
    else:
        print("[PERINGATAN] Tidak ada data yang berhasil diproses.")

