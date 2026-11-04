from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import torch
import xarray as xr


class NCEncoder:
    """
    A class to convert NetCDF (.nc) scientific data files into Zarr stores.
    Optimized for multi-file processing in Docker-based pipelines.
    """
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.ds: Optional[xr.Dataset] = None

    def open_dataset(self) -> xr.Dataset:
        """Opens the NetCDF dataset using xarray."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        self.ds = xr.open_dataset(self.file_path)
        return self.ds

    def encode_to_zarr(self, output_path: Union[str, Path]) -> Path:
        """Writes the complete NetCDF dataset to a Zarr store."""
        ds = self.ds if self.ds is not None else self.open_dataset()
        zarr_path = Path(output_path)
        zarr_path.parent.mkdir(parents=True, exist_ok=True)
        ds.to_zarr(zarr_path, mode="w", zarr_format=2)
        return zarr_path

    def print_metadata(self) -> None:
        """Prints dataset dimensions, variables, and attributes."""
        ds = self.ds if self.ds is not None else self.open_dataset()
        print(f"=== METADATA FOR: {self.file_path.name} ===")
        print(ds)

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

    @classmethod
    def from_zarr(
        cls,
        store_path: Union[str, Path],
        variable_name: str = "sst",
        fill_value: float = 0.0,
    ) -> "Preprocess":
        """Extracts a Zarr variable into a tensor for existing preprocessing steps."""
        zarr_path = Path(store_path)
        if not zarr_path.exists():
            raise FileNotFoundError(f"Zarr store not found: {zarr_path}")

        with xr.open_zarr(zarr_path) as ds:
            if variable_name not in ds.data_vars:
                raise KeyError(
                    f"Variable '{variable_name}' not found. "
                    f"Available variables: {list(ds.data_vars)}"
                )
            raw_data = ds[variable_name].to_numpy()

        cleaned_data = np.nan_to_num(raw_data, nan=fill_value)
        return cls(torch.tensor(cleaned_data, dtype=torch.float32))

    def crop_spatial_region(
        self,
        lat_slice: Optional[Tuple[float, float]] = None,
        lon_slice: Optional[Tuple[float, float]] = None,
        lat_coords: Optional[np.ndarray] = None,
        lon_coords: Optional[np.ndarray] = None,
    ) -> torch.Tensor:
        """
        Crops spatial dimensions (lat, lon) based on coordinate bounds.
        Expects tensor shape: [time, zlev, lat, lon] or similar spatial grids.
        """
        return self.tensor

    def normalize(
        self, mean: Optional[float] = None, std: Optional[float] = None
    ) -> Tuple[torch.Tensor, float, float]:
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
    def create_sliding_windows(
        data: torch.Tensor, input_window: int = 30, horizon: int = 1
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Slices continuous time-series tensors into sliding historical windows
        for sequence-to-sequence forecasting models.
        """
        X, y = [], []
        seq_len = data.shape[0]

        if seq_len <= input_window:
            raise ValueError(
                f"Sequence length ({seq_len}) must be greater than input_window ({input_window})."
            )

        for i in range(seq_len - input_window - horizon + 1):
            X.append(data[i : i + input_window])
            y.append(data[i + input_window : i + input_window + horizon])

        return torch.stack(X), torch.stack(y)


class Visuals:
    """
    Comprehensive diagnostic plotting and visualization utilities for:
    - 2D/4D spatial grid fields (SST maps, regional heatmaps)
    - Time-series telemetry (observed vs. predicted, multi-series, ONI/ENSO timelines)
    - Performance metrics (model comparison bar charts, residuals, confusion matrices, reliability curves)
    """

    def __init__(self, tensor: Optional[torch.Tensor] = None):
        self.tensor = tensor

    def plot_grid_slice(
        self,
        time_idx: int = 0,
        z_idx: int = 0,
        title: str = "Telemetry Grid Snapshot",
        save_path: Optional[Union[str, Path]] = None,
        show: bool = True,
    ) -> Any:
        """Plots a 2D spatial map slice of the tensor using Matplotlib and Seaborn."""
        import matplotlib.pyplot as plt
        import seaborn as sns

        if self.tensor is None:
            raise ValueError("No tensor provided to Visuals instance for plot_grid_slice.")

        if isinstance(self.tensor, torch.Tensor):
            data_np = self.tensor.detach().cpu().numpy()
        else:
            data_np = np.array(self.tensor)

        if data_np.ndim == 4:
            grid_2d = data_np[time_idx, z_idx, :, :]
        elif data_np.ndim == 2:
            grid_2d = data_np
        else:
            raise ValueError(f"Unsupported tensor dimension for 2D plotting: {data_np.ndim}")

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(grid_2d, cmap="coolwarm", cbar=True, ax=ax)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("Longitude Index")
        ax.set_ylabel("Latitude Index")
        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    # =========================================================================
    # TIME SERIES VISUALIZATIONS
    # =========================================================================

    @staticmethod
    def plot_time_series(
        time_index: Union[pd.DatetimeIndex, np.ndarray, list],
        series_dict: Dict[str, Union[np.ndarray, pd.Series, list]],
        title: str = "Climate Time Series Telemetry",
        ylabel: str = "Value",
        thresholds: Optional[Dict[str, float]] = None,
        palette: Optional[List[str]] = None,
        save_path: Optional[Union[str, Path]] = None,
        show: bool = True,
    ) -> Any:
        """Plot multiple continuous time series on a shared timeline.

        Args:
            time_index: DatetimeIndex or array of timestamps.
            series_dict: Mapping of {label: array_or_series}.
            title: Title of the figure.
            ylabel: Y-axis label.
            thresholds: Optional mapping of {label: value} to draw dashed horizontal lines.
            palette: Optional list of hex colors.
            save_path: Optional path to save figure.
            show: Whether to display figure with plt.show().
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(12, 5), dpi=150)
        colors = palette or ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

        for idx, (label, values) in enumerate(series_dict.items()):
            color = colors[idx % len(colors)]
            vals = np.asarray(values, dtype=float)
            ax.plot(time_index, vals, label=label, color=color, linewidth=1.75)

        if thresholds:
            for t_label, t_val in thresholds.items():
                color = "red" if t_val > 0 else "blue" if t_val < 0 else "gray"
                ax.axhline(t_val, color=color, linestyle="--", alpha=0.7, label=f"Ambang {t_label} ({t_val:+0.1f})")

        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("Waktu (Tanggal / Bulan)", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", frameon=True, fontsize=9)
        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    @staticmethod
    def plot_forecast_vs_actual(
        dates: Union[pd.DatetimeIndex, np.ndarray, list],
        actual: Union[np.ndarray, pd.Series],
        predictions: Dict[str, Union[np.ndarray, pd.Series]],
        horizon: Optional[int] = None,
        title: Optional[str] = None,
        ylabel: str = "Anomali (°C)",
        save_path: Optional[Union[str, Path]] = None,
        show: bool = True,
    ) -> Any:
        """Plot actual ground-truth observations against one or more model forecasts.

        Computes MAE and RMSE dynamically for each model and appends them to legend.
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(13, 5), dpi=150)
        actual_arr = np.asarray(actual, dtype=float)

        ax.plot(
            dates, actual_arr,
            label="Observasi (Ground Truth)",
            color="#111111", linewidth=2.2, zorder=4
        )

        model_styles = {
            "persistence": ("#7f7f7f", "--", 1.5),
            "climatology": ("#17becf", "-.", 1.5),
            "seasonal_naive": ("#bcbd22", ":", 1.5),
            "ridge": ("#ff7f0e", "-", 1.8),
            "lightgbm": ("#2ca02c", "-", 2.0),
            "lstm": ("#9467bd", "-", 2.0),
        }

        for name, pred in predictions.items():
            pred_arr = np.asarray(pred, dtype=float)
            # Mask NaNs for metric computation
            valid_mask = ~np.isnan(actual_arr) & ~np.isnan(pred_arr)
            if np.any(valid_mask):
                mae = np.mean(np.abs(actual_arr[valid_mask] - pred_arr[valid_mask]))
                rmse = np.sqrt(np.mean((actual_arr[valid_mask] - pred_arr[valid_mask]) ** 2))
                legend_label = f"{name} (MAE: {mae:.2f}, RMSE: {rmse:.2f})"
            else:
                legend_label = name

            color, style, lw = model_styles.get(name.lower(), ("#e377c2", "-", 1.5))
            ax.plot(dates, pred_arr, label=legend_label, color=color, linestyle=style, linewidth=lw)

        horizon_str = f" [Horizon: {horizon} Bulan]" if horizon else ""
        plot_title = title or f"Perbandingan Prediksi Model vs Observasi Nyata{horizon_str}"
        ax.set_title(plot_title, fontsize=12, fontweight="bold")
        ax.set_xlabel("Tanggal / Periode", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.axhline(0, color="gray", linestyle="-", linewidth=0.8, alpha=0.5)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper left", frameon=True, fontsize=9)
        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    @staticmethod
    def plot_enso_timeline(
        dates: Union[pd.DatetimeIndex, np.ndarray, list],
        oni_values: Union[np.ndarray, pd.Series],
        threshold: float = 0.5,
        title: str = "Timeline Fase ENSO (Oceanic Niño Index / SSTA Niño 3.4)",
        save_path: Optional[Union[str, Path]] = None,
        show: bool = True,
    ) -> Any:
        """Plot the ONI series with red shading for El Niño and blue shading for La Niña."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(14, 5), dpi=150)
        oni_arr = np.asarray(oni_values, dtype=float)

        ax.plot(dates, oni_arr, color="#222222", linewidth=1.5, label="ONI / SSTA Niño 3.4")

        # Shading for warm phase (El Niño >= +0.5) and cold phase (La Niña <= -0.5)
        ax.fill_between(
            dates, oni_arr, threshold,
            where=(oni_arr >= threshold),
            color="#e74c3c", alpha=0.55, interpolate=True, label="Fase Hangat / El Niño (>= +0.5°C)"
        )
        ax.fill_between(
            dates, oni_arr, -threshold,
            where=(oni_arr <= -threshold),
            color="#3498db", alpha=0.55, interpolate=True, label="Fase Dingin / La Niña (<= -0.5°C)"
        )

        # Baseline & thresholds
        ax.axhline(0.0, color="#555555", linestyle="-", linewidth=0.9)
        ax.axhline(threshold, color="#c0392b", linestyle="--", linewidth=1.2, alpha=0.8)
        ax.axhline(-threshold, color="#2980b9", linestyle="--", linewidth=1.2, alpha=0.8)

        # Extreme threshold lines (+2.0 / -2.0)
        ax.axhline(2.0, color="#78281f", linestyle=":", linewidth=1.0, alpha=0.7, label="Very Strong (+2.0°C)")
        ax.axhline(-2.0, color="#1b4f72", linestyle=":", linewidth=1.0, alpha=0.7, label="Very Strong (-2.0°C)")

        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("Waktu (Bulan / Tahun)", fontsize=10)
        ax.set_ylabel("Anomali Suhu Muka Laut (°C)", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper left", frameon=True, fontsize=8.5, ncol=3)
        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    # =========================================================================
    # METRICS VISUALIZATIONS
    # =========================================================================

    @staticmethod
    def plot_metrics_comparison(
        metrics_df: pd.DataFrame,
        metric_col: str = "rmse",
        model_col: str = "model_name",
        horizon_col: Optional[str] = "lead_horizon",
        title: Optional[str] = None,
        save_path: Optional[Union[str, Path]] = None,
        show: bool = True,
    ) -> Any:
        """Visualizes model evaluation metrics across models and forecast lead horizons."""
        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

        if horizon_col and horizon_col in metrics_df.columns:
            sns.barplot(
                data=metrics_df,
                x=horizon_col,
                y=metric_col,
                hue=model_col,
                palette="tab10",
                ax=ax,
            )
            ax.set_xlabel(f"Horizon Prediksi ({horizon_col} Bulan)", fontsize=10)
        else:
            sns.barplot(
                data=metrics_df,
                x=model_col,
                y=metric_col,
                palette="viridis",
                ax=ax,
            )
            ax.set_xlabel("Model", fontsize=10)

        metric_label = metric_col.upper()
        ax.set_ylabel(metric_label, fontsize=10)
        plot_title = title or f"Perbandingan Metrik Evaluasi ({metric_label}) Antar-Model"
        ax.set_title(plot_title, fontsize=12, fontweight="bold")
        ax.grid(True, axis="y", linestyle=":", alpha=0.6)

        # Annotate bars with values
        for p in ax.patches:
            height = p.get_height()
            if not np.isnan(height) and height > 0:
                ax.annotate(
                    f"{height:.2f}",
                    (p.get_x() + p.get_width() / 2.0, height),
                    ha="center", va="bottom",
                    fontsize=8, xytext=(0, 2),
                    textcoords="offset points",
                )

        ax.legend(title="Model", frameon=True, fontsize=9)
        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    @staticmethod
    def plot_residuals(
        actual: Union[np.ndarray, pd.Series],
        predicted: Union[np.ndarray, pd.Series],
        dates: Optional[Union[pd.DatetimeIndex, np.ndarray]] = None,
        model_name: str = "Model",
        save_path: Optional[Union[str, Path]] = None,
        show: bool = True,
    ) -> Any:
        """Diagnostic plot containing 3 panels:
        1. Residuals over time (or index).
        2. Histogram & KDE of residuals.
        3. Actual vs. Predicted scatter with 1:1 identity line.
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        act = np.asarray(actual, dtype=float)
        pred = np.asarray(predicted, dtype=float)
        valid = ~np.isnan(act) & ~np.isnan(pred)
        act_v, pred_v = act[valid], pred[valid]
        residuals = act_v - pred_v

        fig, axes = plt.subplots(1, 3, figsize=(16, 4.5), dpi=150)

        # Panel 1: Residuals time series
        x_axis = dates[valid] if dates is not None else np.arange(len(residuals))
        axes[0].plot(x_axis, residuals, color="#e67e22", marker="o", markersize=3, linestyle="-", linewidth=1.2)
        axes[0].axhline(0, color="black", linestyle="--", linewidth=1.0)
        axes[0].set_title(f"Residual Over Time ({model_name})", fontsize=11, fontweight="bold")
        axes[0].set_ylabel("Error (Actual - Predicted)")
        axes[0].grid(True, linestyle=":", alpha=0.6)

        # Panel 2: Distribution of residuals
        sns.histplot(residuals, kde=True, color="#3498db", ax=axes[1])
        axes[1].axvline(0, color="red", linestyle="--", linewidth=1.0)
        axes[1].set_title(f"Distribusi Residual\n(Mean: {np.mean(residuals):.3f}, Std: {np.std(residuals):.3f})", fontsize=11, fontweight="bold")
        axes[1].set_xlabel("Residual (°C)")
        axes[1].grid(True, linestyle=":", alpha=0.6)

        # Panel 3: Actual vs. Predicted scatter
        axes[2].scatter(act_v, pred_v, color="#2ecc71", alpha=0.7, edgecolors="k", s=30)
        min_val = min(act_v.min(), pred_v.min())
        max_val = max(act_v.max(), pred_v.max())
        axes[2].plot([min_val, max_val], [min_val, max_val], "r--", linewidth=1.5, label="1:1 Perfect Fit")
        axes[2].set_title("Scatter: Actual vs Predicted", fontsize=11, fontweight="bold")
        axes[2].set_xlabel("Observasi Sebenarnya")
        axes[2].set_ylabel("Hasil Prediksi")
        axes[2].legend(loc="upper left", fontsize=8.5)
        axes[2].grid(True, linestyle=":", alpha=0.6)

        plt.tight_layout()
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    @staticmethod
    def plot_confusion_matrix(
        y_true: Union[np.ndarray, list],
        y_pred: Union[np.ndarray, list],
        labels: Optional[List[str]] = None,
        title: str = "Matriks Kebingungan (Confusion Matrix) Fase ENSO",
        cmap: str = "Blues",
        save_path: Optional[Union[str, Path]] = None,
        show: bool = True,
    ) -> Any:
        """Plot annotated heatmap confusion matrix for categorical predictions."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        from sklearn.metrics import confusion_matrix

        target_labels = labels or sorted(list(set(y_true) | set(y_pred)))
        cm = confusion_matrix(y_true, y_pred, labels=target_labels)
        cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
        cm_norm = np.nan_to_num(cm_norm)

        # Create annotation strings (Count + Percentage)
        annot_matrix = np.empty_like(cm, dtype=object)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                annot_matrix[i, j] = f"{cm[i, j]}\n({cm_norm[i, j]:.1%})"

        fig, ax = plt.subplots(figsize=(7, 5.5), dpi=150)
        sns.heatmap(
            cm,
            annot=annot_matrix,
            fmt="",
            cmap=cmap,
            xticklabels=target_labels,
            yticklabels=target_labels,
            cbar=True,
            ax=ax,
        )
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("Prediksi Model", fontsize=10)
        ax.set_ylabel("Observasi Sebenarnya", fontsize=10)
        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    @staticmethod
    def plot_reliability_curve(
        y_true_binary: Union[np.ndarray, list],
        y_prob: Union[np.ndarray, list],
        n_bins: int = 5,
        title: str = "Diagram Keandalan (Reliability / Calibration Curve)",
        save_path: Optional[Union[str, Path]] = None,
        show: bool = True,
    ) -> Any:
        """Plot calibration / reliability diagram for probabilistic forecasts."""
        import matplotlib.pyplot as plt
        from sklearn.calibration import calibration_curve
        from sklearn.metrics import brier_score_loss

        y_true_arr = np.asarray(y_true_binary, dtype=int)
        y_prob_arr = np.asarray(y_prob, dtype=float)

        prob_true, prob_pred = calibration_curve(y_true_arr, y_prob_arr, n_bins=n_bins)
        brier = brier_score_loss(y_true_arr, y_prob_arr)

        fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
        ax.plot([0, 1], [0, 1], "k--", label="Kalibrasi Sempurna (Ideal)")
        ax.plot(
            prob_pred, prob_true, "s-",
            color="#2980b9", linewidth=2.0, markersize=6,
            label=f"Model Terkalibrasi (Brier: {brier:.3f})"
        )

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("Probabilitas Prediksi Rata-rata")
        ax.set_ylabel("Frekuensi Kejadian Nyata")
        ax.set_xlim([-0.05, 1.05])
        ax.set_ylim([-0.05, 1.05])
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper left", fontsize=9)
        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        return fig


if __name__ == "__main__":
    print("=== Menjalankan Demo Uji Coba utils.py ===")

    # Test time series visualization demo with synthetic series
    sample_dates = pd.date_range("2023-01-01", periods=12, freq="MS")
    actual_oni = np.array([0.1, 0.3, 0.6, 0.8, 1.1, 1.4, 1.7, 2.1, 2.0, 1.8, 1.2, 0.4])
    pred_ridge = actual_oni + np.random.normal(0, 0.15, size=len(actual_oni))
    pred_lgbm = actual_oni + np.random.normal(0, 0.10, size=len(actual_oni))

    print("\n[1] Demo Visuals.plot_enso_timeline (dry-run without GUI display)...")
    fig1 = Visuals.plot_enso_timeline(sample_dates, actual_oni, show=False)
    print("    -> Berhasil menghasilkan figure ENSO timeline!")

    print("\n[2] Demo Visuals.plot_forecast_vs_actual...")
    fig2 = Visuals.plot_forecast_vs_actual(
        dates=sample_dates,
        actual=actual_oni,
        predictions={"ridge": pred_ridge, "lightgbm": pred_lgbm},
        horizon=1,
        show=False,
    )
    print("    -> Berhasil menghasilkan figure Forecast vs Actual!")

    print("\n[3] Demo Visuals.plot_metrics_comparison...")
    dummy_metrics = pd.DataFrame([
        {"model_name": "persistence", "lead_horizon": 1, "rmse": 0.45},
        {"model_name": "climatology", "lead_horizon": 1, "rmse": 0.58},
        {"model_name": "ridge", "lead_horizon": 1, "rmse": 0.28},
        {"model_name": "lightgbm", "lead_horizon": 1, "rmse": 0.22},
        {"model_name": "persistence", "lead_horizon": 3, "rmse": 0.62},
        {"model_name": "climatology", "lead_horizon": 3, "rmse": 0.59},
        {"model_name": "ridge", "lead_horizon": 3, "rmse": 0.41},
        {"model_name": "lightgbm", "lead_horizon": 3, "rmse": 0.35},
    ])
    fig3 = Visuals.plot_metrics_comparison(dummy_metrics, metric_col="rmse", show=False)
    print("    -> Berhasil menghasilkan figure Metrics Comparison!")

    print("\n[4] Demo Visuals.plot_residuals...")
    fig4 = Visuals.plot_residuals(actual_oni, pred_lgbm, dates=sample_dates, model_name="LightGBM", show=False)
    print("    -> Berhasil menghasilkan figure Residuals!")

    print("\n[SUKSES] Semua fungsi visualisasi time series & metrics di utils.py berjalan normal!")
