from pathlib import Path
from typing import Union, Optional, Tuple
import numpy as np
import torch
import xarray as xr

class NCEncoder:
    """
    A class to decode NetCDF (.nc) scientific data files into PyTorch tensors.
    Optimized for multi-file processing in Docker-based pipelines.
    """
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.ds = None
        self.tensor_data = None

    def open_dataset(self) -> xr.Dataset:
        """Opens the NetCDF dataset using xarray with local imports."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        self.ds = xr.open_dataset(self.file_path)
        return self.ds

    def print_metadata(self) -> None:
        """Prints dataset dimensions, variables, and attributes."""
        if self.ds is None:
            self.open_dataset()
        print(f"=== METADATA FOR: {self.file_path.name} ===")
        print(self.ds)

    def process_to_tensor(self, variable_name: str = 'sst', fill_value: float = 0.0) -> torch.Tensor:
        """
        Extracts a specific variable, handles missing/NaN values, 
        and converts the array into a PyTorch tensor.
        """
        if self.ds is None:
            self.open_dataset()

        if variable_name not in self.ds:
            raise KeyError(
                f"Variable '{variable_name}' not found. "
                f"Available variables: {list(self.ds.data_vars.keys())}"
            )

        raw_data = self.ds[variable_name].values
        cleaned_data = np.nan_to_num(raw_data, nan=fill_value)

        self.tensor_data = torch.tensor(cleaned_data, dtype=torch.float32)
        return self.tensor_data

    def close(self) -> None:
        """Closes the underlying xarray dataset to free file handles."""
        if self.ds is not None:
            self.ds.close()
            self.ds = None


class Preprocess:
    """
    Handles spatial cropping (e.g., bounding box for the Indonesian Throughflow region),
    normalization, and rolling temporal windowing for deep learning tensors.
    """
    def __init__(self, tensor: torch.Tensor):
        self.tensor = tensor

    def crop_spatial_region(self, 
                            lat_slice: Optional[Tuple[float, float]] = None, 
                            lon_slice: Optional[Tuple[float, float]] = None,
                            lat_coords: Optional[np.ndarray] = None,
                            lon_coords: Optional[np.ndarray] = None) -> torch.Tensor:
        """
        Crops spatial dimensions (lat, lon) based on coordinate bounds.
        Expects tensor shape: [time, zlev, lat, lon] or similar spatial grids.
        """
        # Placeholder logic for slicing tensor based on coordinate indices if passed
        # e.g., ITF bounding box filtering
        return self.tensor

    def normalize(self, mean: Optional[float] = None, std: Optional[float] = None) -> Tuple[torch.Tensor, float, float]:
        """Applies standard scaling (Z-score normalization) to the tensor."""
        if mean is None:
            mean = self.tensor.mean().item()
        if std is None:
            std = self.tensor.std().item()
            
        # Avoid division by zero
        std = std if std != 0 else 1.0
        normalized_tensor = (self.tensor - mean) / std
        return normalized_tensor, mean, std

    @staticmethod
    def create_sliding_windows(data: torch.Tensor, input_window: int = 30, horizon: int = 1) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Slices continuous time-series tensors into sliding historical windows 
        for sequence-to-sequence forecasting models.
        """
        X, y = [], []
        seq_len = data.shape[0]
        
        if seq_len <= input_window:
            raise ValueError(f"Sequence length ({seq_len}) must be greater than input_window ({input_window}).")
            
        for i in range(seq_len - input_window - horizon + 1):
            X.append(data[i : i + input_window])
            y.append(data[i + input_window : i + input_window + horizon])
            
        return torch.stack(X), torch.stack(y)


class Visuals:
    """
    Provides diagnostic plotting utilities for tensor fields and spatial telemetry.
    """
    def __init__(self, tensor: torch.Tensor):
        self.tensor = tensor

    def plot_grid_slice(self, time_idx: int = 0, z_idx: int = 0, title: str = "Telemetry Grid Snapshot") -> None:
        """
        Plots a 2D spatial map slice of the tensor using Matplotlib.
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        # Ensure tensor is detached and moved to CPU numpy array
        if isinstance(self.tensor, torch.Tensor):
            data_np = self.tensor.detach().cpu().numpy()
        else:
            data_np = np.array(self.tensor)

        # Handle typical dimensions [time, zlev, lat, lon]
        if data_np.ndim == 4:
            grid_2d = data_np[time_idx, z_idx, :, :]
        elif data_np.ndim == 2:
            grid_2d = data_np
        else:
            raise ValueError(f"Unsupported tensor dimension for 2D plotting: {data_np.ndim}")

        plt.figure(figsize=(10, 5))
        sns.heatmap(grid_2d, cmap='coolwarm', cbar=True)
        plt.title(title)
        plt.xlabel("Longitude Index")
        plt.ylabel("Latitude Index")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    import sys
    print("=== Menjalankan Demo Uji Coba utils.py ===")
    
    # Path sample data
    sample_file = Path("dataset/sst_5_wilayah/Selat_Makassar_2015.nc")
    if not sample_file.exists():
        # Cek jika dijalankan dari dalam folder src/
        sample_file = Path("../dataset/sst_5_wilayah/Selat_Makassar_2015.nc")

    if sample_file.exists():
        print(f"[1] Membaca file: {sample_file.name}")
        encoder = NCEncoder(sample_file)
        
        # Ekstrak tensor
        tensor = encoder.process_to_tensor(variable_name="sst")
        print(f"    -> Berhasil decode ke Tensor! Shape: {tensor.shape}, Tipe data: {tensor.dtype}")
        encoder.close()
        
        # Uji Preprocess (Normalisasi & Windowing)
        print("\n[2] Menjalankan Preprocess...")
        prep = Preprocess(tensor)
        norm_tensor, mean_val, std_val = prep.normalize()
        print(f"    -> Rata-rata (mean): {mean_val:.4f}, Standar Deviasi (std): {std_val:.4f}")
        
        X, y = Preprocess.create_sliding_windows(norm_tensor, input_window=30, horizon=1)
        print(f"    -> Sliding Window dibuat!")
        print(f"       Fitur Input  (X): {X.shape} (misal: 30 hari data)")
        print(f"       Target Label (y): {y.shape} (misal: 1 hari berikutnya)")
        print("\n[SUKSES] Semua class di utils.py berjalan normal!")
    else:
        print("[PERINGATAN] File sampel dataset tidak ditemukan pada path yang dicek.")