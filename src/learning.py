"""BluePrint alur pembelajaran dan peramalan.

Tujuan
------
Membangun eksperimen peramalan klimatologi bulanan yang dapat direproduksi,
dimulai dari baseline sederhana, lalu dibandingkan secara adil dengan model
machine-learning. Modul ini melatih, mengevaluasi, memvisualisasikan, dan
menyimpan metrik performa model ke database PostgreSQL.

Produk peramalan
----------------
1. Prediksi ONI/SST-anomali Niño 3.4 untuk horizon bulanan yang tetap,
   misalnya 1, 3, 6, dan 12 bulan.
2. Probabilitas fase ENSO El Niño/netral/La Niña pada horizon yang sama,
   dihitung dari target kontinu ONI atau RONI yang telah dipilih, bukan dari
   label tahunan.
3. Prediksi SST absolut/anomali pada grid atau rerata wilayah Pasifik dan tiga
   wilayah Indonesia yang tersedia.
4. Prediksi status MHW, intensitas, dan durasi pada wilayah yang memiliki
   label MHW yang konsisten.
5. Prediksi dampak hujan Malaysia dan Hawaii sebagai target terpisah; Indonesia
   tidak boleh disimpulkan dari satu seri rainfall Malaysia.

Sumber data dan pembentukan fitur
---------------------------------
* Baca group Zarr ``sst_5_wilayah/pasifik_nino34``, Selat Karimata, Selat
  Makassar, ``data_oni/oni``, ``data_soi/soi``, ``data_dmi/dmi``, rainfall
  Malaysia/Hawaii, dan MHW sesuai target.
* Gunakan time alignment bulanan dan tetapkan timestamp sebagai awal bulan.
  Resampling ONI musiman 3-bulanan harus didokumentasikan; jangan menganggap
  setiap label musiman sebagai dua belas pengamatan baru.
* Fitur SST dapat berupa nilai absolut, anomali terhadap klimatologi training,
  rerata wilayah, centroid/peta grid, atau embedding spasio-temporal.
* Tambahkan lag 1 sampai n bulan, rolling mean, seasonal encoding, dan nilai
  ONI/SOI/DMI pada waktu prediksi yang diketahui saat issuance.
* Hindari fitur masa depan seperti `ANOM` pada horizon target, kecuali target
  model eksplisit adalah supervised nowcasting dan availability date tercatat.
* Normalisasi, imputasi, climatology, dan encoding kategori harus dipelajari
  pada training split saja.

Kontrak anomali dan baseline
----------------------------
* ``sst`` pada store adalah SST absolut; anomali bulanan proyek dihitung terpisah
  dengan climatology tetap, misalnya 1991--2020, bila data referensi memadai.
* ONI ``ANOM`` adalah data resmi, sedangkan ONI ``TOTAL`` bukan hasil anomali
  proyek.
* Benchmark minimum:
  1. climatologi bulanan training;
  2. persistence nilai target terakhir;
  3. seasonal-naive target bulan yang sama tahun sebelumnya;
  4. persistence ONI/SOI/DMI untuk indeks ENSO;
  5. climatologi dan persistence MHW/rainfall untuk eksperimen dampak.
* Anomali benchmark dan model dievaluasi pada split serta horizon yang sama.
  Model baru dinyatakan memiliki nilai hanya jika mengungguli baseline yang lebih
  sederhana dengan ukuran ketidakpastian dan metrik yang disepakati.

Pemilahan data
--------------
Gunakan split kronologis forward-chaining/rolling-origin, bukan random split.
Simpan cut-off dan availability date setiap hindcast. Data sebelum cut-off hanya
boleh dipakai untuk training dan climatology; validation dipakai untuk
hyperparameter; test dipakai sekali untuk laporan akhir. Dengan arsip hanya
2015--2025, awalnya gunakan evaluasi leave-enough-data-forward dan laporkan
jumlah sampel per lead serta ketidakpastian musim.

Arsitektur dan model kandidat
-----------------------------
Tahap awal:
* persistence, climatologi musiman, ridge/elastic-net, dan autoregressive linear
  untuk baseline yang mudah ditafsirkan;
* LightGBM/XGBoost untuk lag dan indeks tabular terstruktur;
* LSTM atau Temporal Convolutional Network untuk deret SST dan rainfall.

Tahap lanjutan:
* CNN/ConvLSTM pada grid regional untuk memanfaatkan pola spasial;
* model probabilistik atau quantile regression untuk interval prediksi;
* LightGBM memakai embedding temporal dan fitur hasil eksperimen LSTM;
* ensemble sederhana hanya setelah model individual dievaluasi pada fold yang
  sama dan tidak digabungkan dengan leakage.

Target dan loss
---------------
1. ONI/SST: MSE/MAE dan skill RMSE terhadap climatology/persistence.
2. Fase ENSO: cross-entropy, calibration, balanced accuracy, dan confusion
   matrix.
3. MHW biner: Brier score, ROC-AUC, PR-AUC, recall, precision, dan F1.
4. Intensitas/durasi MHW: interval censor-aware atau regresi nonnegatif bila
   distribusi mendukung.
5. Rainfall: MAE/RMSE, bias, anomaly correlation, dan skor probabilitas pada
   target bernilai positif.

Evaluasi dan keluaran
---------------------
Laporkan metrik per region, season, lead time, dan tahun. Berikan confidence
interval bootstrap per episode yang tidak merandomkan titik berurutan secara
independen. Bandingkan model dengan climatology/persistence menggunakan skill
score; untuk probabilitas, laporkan reliability diagram dan calibration error.
Simpan artifacts (model, scaler/climatology, feature schema, cut-off, metrics,
dan run version) serta prediksi yang dapat dibaca ulang oleh inference dan
database persistence.

Urutan implementasi
-------------------
1. Buat loader dan kontrak schema Zarr.
2. Buat normalizer, anomaly builder, seasonal features, lag features, dan split
   chronologis dalam fungsi yang dapat diuji.
3. Jalankan baseline ONI, SST, rainfall, dan MHW.
4. Tambahkan model tabular per lead/horizon.
5. Tambahkan LSTM dan evaluasi dengan parameter efisiensi serta seed tetap.
6. Baru tambahkan ConvLSTM/CNN setelah arti regional cukup panjang.
7. Kalibrasi probabilitas, simpan artifact, dan uji inference tanpa data masa
   depan.

Keterbatasan implementasi
-------------------------
Rentang 2015--2025 dan jumlah sampel 132 bulan dapat kurang memadai untuk
hindcast ENSO dan evaluasi episode. Hindari klaim fase multi-tahun deterministik
atau reliabilitas probabilitas tinggi dari data pendek. Semua perubahan
baseline, cutoff, formula anomaly, variabel target, dan data availability harus
diberi versi agar hasil antarpercobaan dapat dibandingkan.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Project Module Imports
try:
    from src.ml import classif, deepl, forecast, stats
    from src.ml.ensemble import ForecastOrchestrator, ForecastRunConfig, ForecastRunResult
    from src.database import Database
    from src.utils import Visuals
except ImportError:
    from ml import classif, deepl, forecast, stats
    from ml.ensemble import ForecastOrchestrator, ForecastRunConfig, ForecastRunResult
    from database import Database
    from utils import Visuals

import knowledge

logger = logging.getLogger(__name__)


# ==============================================================================
# SECTION 1: CONFIGURATION AND DATA SCHEMAS
# ==============================================================================

@dataclass(frozen=True)
class LearningConfig:
    """Experiment configuration for climate and ENSO forecasting models."""

    zarr_store_path: Path = Path("dataset/climate_dataset.zarr")
    target_variable: str = "ANOM"  # Oceanic Niño Index anomaly
    region_name: str = "Pasifik_Nino34"
    horizons: Tuple[int, ...] = (1, 3, 6, 12)
    lags: Tuple[int, ...] = (1, 2, 3, 6, 12)
    window_size: int = 12
    train_ratio: float = 0.70
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    seed: int = 42
    enabled_models: Tuple[str, ...] = (
        "persistence",
        "climatology",
        "seasonal_naive",
        "ridge",
        "lightgbm",
        "lstm",
        "enso_classifier",
    )


@dataclass
class DatasetSplits:
    """Chronologically aligned train, validation, and test datasets."""

    train_df: pd.DataFrame
    val_df: pd.DataFrame
    test_df: pd.DataFrame
    feature_columns: List[str]
    target_column: str
    feature_mean: pd.Series
    feature_std: pd.Series
    train_climatology: pd.Series


# ==============================================================================
# SECTION 2: DATA LOADING & EXTRACTION FROM ZARR / STORE
# ==============================================================================

def load_climate_dataframe(
    zarr_store_path: Union[str, Path] = "dataset/climate_dataset.zarr",
) -> pd.DataFrame:
    """Extract and align all monthly climate variables into a unified DataFrame.

    Variables extracted:
        - ONI (ANOM, TOTAL)
        - SOI (Tahiti - Darwin index)
        - DMI (Indian Ocean Dipole index)
        - Regional SST spatial means (Pasifik Niño 3.4, Selat Makassar, Selat Karimata)
        - Regional rainfall (Malaysia, Hawaii)
        - MHW occurrence indicators
    """
    store_path = Path(zarr_store_path)
    dates = pd.date_range("2015-01-01", "2025-12-01", freq="MS")

    if not store_path.exists():
        logger.warning(
            f"Zarr store {store_path} not found. Generating standardized fallback series for demonstration."
        )
        return generate_synthetic_climate_dataframe(dates)

    try:
        import xarray as xr

        series_dict: Dict[str, pd.Series] = {}

        # 1. Load ONI
        try:
            with xr.open_zarr(str(store_path), group="data_oni/oni", consolidated=False) as ds:
                time_idx = pd.to_datetime(ds["time"].values)
                series_dict["ANOM"] = pd.Series(ds["ANOM"].values, index=time_idx)
                series_dict["TOTAL"] = pd.Series(ds["TOTAL"].values, index=time_idx)
        except Exception as e:
            logger.warning(f"Could not read data_oni/oni: {e}")

        # 2. Load SOI
        try:
            with xr.open_zarr(str(store_path), group="data_soi/soi", consolidated=False) as ds:
                time_idx = pd.to_datetime(ds["time"].values)
                series_dict["SOI"] = pd.Series(ds["SOI"].values, index=time_idx)
        except Exception as e:
            logger.warning(f"Could not read data_soi/soi: {e}")

        # 3. Load DMI
        try:
            with xr.open_zarr(str(store_path), group="data_dmi/dmi", consolidated=False) as ds:
                time_idx = pd.to_datetime(ds["time"].values)
                series_dict["DMI"] = pd.Series(ds["DMI"].values, index=time_idx)
        except Exception as e:
            logger.warning(f"Could not read data_dmi/dmi: {e}")

        # 4. Load Regional SST (Spatial Means)
        for region_key in ("pasifik_nino34", "selat_makassar", "selat_karimata"):
            group_name = f"sst_5_wilayah/{region_key}"
            try:
                with xr.open_zarr(str(store_path), group=group_name, consolidated=False) as ds:
                    time_idx = pd.to_datetime(ds["time"].values)
                    # Compute area-weighted spatial mean across lat and lon
                    da = ds["sst"]
                    if "zlev" in da.dims:
                        da = da.squeeze("zlev", drop=True)
                    lats = ds["lat"].values
                    weights = np.cos(np.deg2rad(lats))
                    weights_da = xr.DataArray(weights, dims=["lat"], coords={"lat": lats})
                    weighted_mean = (da * weights_da).sum(dim=["lat", "lon"]) / (weights_da * (~da.isnull())).sum(dim=["lat", "lon"])
                    series_dict[f"sst_{region_key}"] = pd.Series(weighted_mean.values, index=time_idx)
            except Exception as e:
                logger.warning(f"Could not read {group_name}: {e}")

        # 5. Load Rainfall
        try:
            with xr.open_zarr(str(store_path), group="data_rainfall_monthly/malaysia", consolidated=False) as ds:
                time_idx = pd.to_datetime(ds["time"].values)
                if "rfh" in ds.data_vars:
                    series_dict["rainfall_mys"] = pd.Series(ds["rfh"].values, index=time_idx)
        except Exception as e:
            logger.warning(f"Could not read rainfall-mys: {e}")

        try:
            with xr.open_zarr(str(store_path), group="data_rainfall_monthly/hawaii", consolidated=False) as ds:
                time_idx = pd.to_datetime(ds["time"].values)
                if "rain_total_mm" in ds.data_vars:
                    series_dict["rainfall_hawaii"] = pd.Series(ds["rain_total_mm"].values, index=time_idx)
        except Exception as e:
            logger.warning(f"Could not read rainfall-hawaii: {e}")

        # 6. Load MHW Labels
        try:
            with xr.open_zarr(str(store_path), group="data_mhw/mhw_labels", consolidated=False) as ds:
                time_idx = pd.to_datetime(ds["time"].values)
                if "Pasifik_Nino34_is_mhw" in ds.data_vars:
                    series_dict["mhw_nino34"] = pd.Series(ds["Pasifik_Nino34_is_mhw"].values, index=time_idx)
                if "Selat_Makassar_is_mhw" in ds.data_vars:
                    series_dict["mhw_makassar"] = pd.Series(ds["Selat_Makassar_is_mhw"].values, index=time_idx)
        except Exception as e:
            logger.warning(f"Could not read mhw_labels: {e}")

        if not series_dict:
            return generate_synthetic_climate_dataframe(dates)

        df = pd.DataFrame(series_dict, index=dates).sort_index()
        # Interpolate small gaps or forward-fill
        df = df.ffill().bfill()
        return df

    except Exception as e:
        logger.error(f"Error loading Zarr store: {e}. Falling back to standardized dataset.")
        return generate_synthetic_climate_dataframe(dates)


def generate_synthetic_climate_dataframe(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Generate physically-realistic synthetic ENSO, SST, and climate index series for testing."""
    np.random.seed(42)
    n = len(dates)
    months = dates.month.to_numpy()

    # Synthetic ENSO cycle: 4-year quasi-periodicity + seasonal phase locking peaking in DJF
    time_steps = np.arange(n)
    enso_wave = 1.3 * np.sin(2 * np.pi * time_steps / 48 - 0.5)
    seasonality = 0.4 * np.cos(2 * np.pi * (months - 1) / 12)
    noise = np.random.normal(0, 0.2, size=n)
    oni_anom = np.round(enso_wave + seasonality + noise, 3)

    # Absolute SST centered around 27.2 °C
    sst_total = np.round(27.2 + 0.9 * np.sin(2 * np.pi * (months - 4) / 12) + oni_anom, 2)

    # Atmospheric SOI: negatively coupled with ONI
    soi = np.round(-10.5 * oni_anom + np.random.normal(0, 3.0, size=n), 1)

    # Indian Ocean Dipole (DMI): partially coupled with ENSO
    dmi = np.round(0.35 * oni_anom + 0.4 * np.sin(2 * np.pi * time_steps / 36) + np.random.normal(0, 0.15, size=n), 2)

    # Regional SSTs
    sst_makassar = np.round(29.0 + 0.5 * np.cos(2 * np.pi * (months - 5) / 12) - 0.3 * oni_anom + np.random.normal(0, 0.1, size=n), 2)
    sst_karimata = np.round(28.8 + 0.6 * np.cos(2 * np.pi * (months - 4) / 12) - 0.25 * oni_anom + np.random.normal(0, 0.1, size=n), 2)

    # Rainfall
    rain_mys = np.maximum(50.0, np.round(220.0 - 45.0 * oni_anom + np.random.normal(0, 30.0, size=n), 1))
    rain_hawaii = np.maximum(10.0, np.round(150.0 + 20.0 * oni_anom + np.random.normal(0, 25.0, size=n), 1))

    # MHW flag
    mhw_flag = (oni_anom >= 1.0).astype(int)

    return pd.DataFrame(
        {
            "ANOM": oni_anom,
            "TOTAL": sst_total,
            "SOI": soi,
            "DMI": dmi,
            "sst_pasifik_nino34": sst_total,
            "sst_selat_makassar": sst_makassar,
            "sst_selat_karimata": sst_karimata,
            "rainfall_mys": rain_mys,
            "rainfall_hawaii": rain_hawaii,
            "mhw_nino34": mhw_flag,
        },
        index=dates,
    )


# ==============================================================================
# SECTION 3: FEATURE ENGINEERING & DATA SPLITTING
# ==============================================================================

def build_feature_matrix(
    df: pd.DataFrame,
    target_col: str = "ANOM",
    feature_cols: Optional[List[str]] = None,
    lags: Tuple[int, ...] = (1, 2, 3, 6, 12),
    lead_horizon: int = 1,
) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """Build historical lag features, seasonal cycles, and rolling metrics.

    Ensures no future data leakage: feature matrix at row t uses only
    observations available at or before issuance timestamp t.

    Args:
        df: Aligned monthly climate DataFrame.
        target_col: Target variable to forecast.
        feature_cols: Base feature columns to lag. Defaults to available columns.
        lags: Lags in months to generate.
        lead_horizon: Target forecast horizon in months (target = y_{t+h}).

    Returns:
        X (features DataFrame), y (target Series), and list of feature names.
    """
    df_clean = df.copy()
    base_features = feature_cols or [col for col in df.columns if col in ("ANOM", "SOI", "DMI", "sst_pasifik_nino34", "rainfall_mys")]

    feature_dict: Dict[str, pd.Series] = {}

    # 1. Historical Lag Features
    for col in base_features:
        for lag in lags:
            feature_dict[f"{col}_lag_{lag}"] = df_clean[col].shift(lag)

    # 2. Rolling Statistics (Mean & Std) of target
    for r_window in (3, 6):
        feature_dict[f"{target_col}_rollmean_{r_window}"] = df_clean[target_col].shift(1).rolling(window=r_window).mean()
        feature_dict[f"{target_col}_rollstd_{r_window}"] = df_clean[target_col].shift(1).rolling(window=r_window).std()

    # 3. Cyclical Month Encoding (Annual Solar Cycle)
    months = df_clean.index.month
    feature_dict["month_sin"] = pd.Series(np.sin(2 * np.pi * months / 12.0), index=df_clean.index)
    feature_dict["month_cos"] = pd.Series(np.cos(2 * np.pi * months / 12.0), index=df_clean.index)

    # 4. Target variable shifted forward by lead_horizon
    target_series = df_clean[target_col].shift(-lead_horizon)
    target_series.name = f"{target_col}_h{lead_horizon}"

    X = pd.DataFrame(feature_dict, index=df_clean.index)
    y = target_series

    # Drop NaNs resulting from lags and forward shift
    valid_mask = ~(X.isna().any(axis=1) | y.isna())
    X_valid = X[valid_mask]
    y_valid = y[valid_mask]

    return X_valid, y_valid, list(X.columns)


def chronological_split(
    X: pd.DataFrame,
    y: pd.Series,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
) -> DatasetSplits:
    """Split features and target chronologically without shuffle.

    Calculates normalization scalers and climatology solely from the training split.
    """
    n = len(X)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    train_X = X.iloc[:n_train]
    train_y = y.iloc[:n_train]

    val_X = X.iloc[n_train : n_train + n_val]
    val_y = y.iloc[n_train : n_train + n_val]

    test_X = X.iloc[n_train + n_val :]
    test_y = y.iloc[n_train + n_val :]

    # Fit feature scaling solely on train_X
    f_mean = train_X.mean()
    f_std = train_X.std().replace(0, 1.0)

    # Fit target monthly climatology solely on train_y
    train_climatology = train_y.groupby(train_y.index.month).mean()

    train_df = train_X.copy()
    train_df["target"] = train_y

    val_df = val_X.copy()
    val_df["target"] = val_y

    test_df = test_X.copy()
    test_df["target"] = test_y

    return DatasetSplits(
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        feature_columns=list(X.columns),
        target_column=y.name,
        feature_mean=f_mean,
        feature_std=f_std,
        train_climatology=train_climatology,
    )


# ==============================================================================
# SECTION 4: METRIC EVALUATION FUNCTIONS
# ==============================================================================

def compute_regression_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
    baseline_rmse: Optional[float] = None,
) -> Dict[str, float]:
    """Compute standard regression metrics and skill scores."""
    act = np.asarray(actual, dtype=float)
    pred = np.asarray(predicted, dtype=float)
    valid = ~np.isnan(act) & ~np.isnan(pred)

    if not np.any(valid):
        return {"mae": float("nan"), "rmse": float("nan"), "r2_score": float("nan"), "sample_size": 0}

    act_v, pred_v = act[valid], pred[valid]
    mae = float(mean_absolute_error(act_v, pred_v))
    rmse = float(np.sqrt(mean_squared_error(act_v, pred_v)))
    r2 = float(r2_score(act_v, pred_v)) if len(act_v) > 1 else float("nan")

    metrics = {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2_score": round(r2, 4),
        "sample_size": int(len(act_v)),
    }

    if baseline_rmse and baseline_rmse > 0:
        skill = 1.0 - (rmse / baseline_rmse)
        metrics["skill_score"] = round(skill, 4)

    return metrics


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """Compute categorical and probabilistic classification metrics."""
    acc = float(accuracy_score(y_true, y_pred))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred))
    f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    metrics = {
        "accuracy": round(acc, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "f1_score": round(f1, 4),
        "sample_size": int(len(y_true)),
    }

    if y_prob is not None:
        try:
            # Multi-class or binary Brier score
            if y_prob.ndim == 2 and y_prob.shape[1] > 1:
                classes = np.unique(y_true)
                y_true_binary = pd.get_dummies(y_true).reindex(columns=classes, fill_value=0).to_numpy()
                brier = float(np.mean(np.sum((y_prob - y_true_binary) ** 2, axis=1)))
                metrics["brier_score"] = round(brier, 4)
                # Multiclass ROC-AUC
                try:
                    roc_auc = float(roc_auc_score(y_true, y_prob, multi_class="ovr", average="macro"))
                    metrics["roc_auc"] = round(roc_auc, 4)
                except Exception:
                    pass
            elif y_prob.ndim == 1:
                brier = float(brier_score_loss(y_true, y_prob))
                metrics["brier_score"] = round(brier, 4)
                roc_auc = float(roc_auc_score(y_true, y_prob))
                metrics["roc_auc"] = round(roc_auc, 4)
        except Exception as e:
            logger.debug(f"Probabilistic metric computation note: {e}")

    return metrics


# ==============================================================================
# SECTION 5: PIPELINE EXECUTION & EXPERIMENT RUNNER
# ==============================================================================

class ClimateLearningPipeline:
    """End-to-end learning pipeline training statistical, tabular, and sequence models."""

    def __init__(self, config: Optional[LearningConfig] = None):
        self.config = config or LearningConfig()
        self.orchestrator = ForecastOrchestrator(
            ForecastRunConfig(
                horizons=self.config.horizons,
                window_size=self.config.window_size,
                seed=self.config.seed,
                enabled_models=self.config.enabled_models,
            )
        )
        self.evaluation_records: List[Dict[str, Any]] = []

    def run_horizon_experiment(
        self,
        df: pd.DataFrame,
        horizon: int,
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, Dict[str, float]], pd.DatetimeIndex, np.ndarray]:
        """Run training and evaluation for a specific forecast horizon.

        Args:
            df: Climate data frame.
            horizon: Lead horizon in months (1, 3, 6, 12).

        Returns:
            Tuple of (predictions_dict, metrics_dict, test_dates, test_actual).
        """
        target_col = self.config.target_variable

        # 1. Feature Engineering
        X, y, feature_names = build_feature_matrix(
            df,
            target_col=target_col,
            lags=self.config.lags,
            lead_horizon=horizon,
        )

        # 2. Chronological Split
        splits = chronological_split(
            X, y,
            train_ratio=self.config.train_ratio,
            val_ratio=self.config.val_ratio,
        )

        # Normalize features with training scaler
        X_train_norm = ((splits.train_df[feature_names] - splits.feature_mean) / splits.feature_std).to_numpy(dtype=np.float32)
        X_test_norm = ((splits.test_df[feature_names] - splits.feature_mean) / splits.feature_std).to_numpy(dtype=np.float32)

        y_train = splits.train_df["target"].to_numpy(dtype=np.float32)
        y_test = splits.test_df["target"].to_numpy(dtype=np.float32)
        test_dates = splits.test_df.index

        predictions: Dict[str, np.ndarray] = {}
        horizon_metrics: Dict[str, Dict[str, float]] = {}

        # ----------------------------------------------------------------------
        # A. Statistical Baselines (stats.py)
        # ----------------------------------------------------------------------
        train_series = df.loc[splits.train_df.index, target_col]

        # 1. Persistence
        if "persistence" in self.config.enabled_models:
            last_known = float(train_series.iloc[-1])
            pred_persistence = np.full(len(test_dates), last_known)
            predictions["persistence"] = pred_persistence
            horizon_metrics["persistence"] = compute_regression_metrics(y_test, pred_persistence)

        # 2. Climatology
        if "climatology" in self.config.enabled_models:
            pred_climatology = splits.train_climatology.loc[test_dates.month].to_numpy(dtype=float)
            predictions["climatology"] = pred_climatology
            horizon_metrics["climatology"] = compute_regression_metrics(y_test, pred_climatology)

        # 3. Seasonal Naive
        if "seasonal_naive" in self.config.enabled_models:
            try:
                naive_res = stats.seasonal_naive(
                    train_series,
                    horizon=len(test_dates),
                    forecast_dates=test_dates,
                )
                pred_naive = naive_res.prediction
                predictions["seasonal_naive"] = pred_naive
                horizon_metrics["seasonal_naive"] = compute_regression_metrics(y_test, pred_naive)
            except Exception as e:
                logger.debug(f"Seasonal naive skipped: {e}")

        # Baseline RMSE for skill score comparison
        base_rmse = horizon_metrics.get("persistence", {}).get("rmse") or horizon_metrics.get("climatology", {}).get("rmse")

        # ----------------------------------------------------------------------
        # B. Tabular Machine Learning Models (forecast.py)
        # ----------------------------------------------------------------------
        # 4. Ridge Regression
        if "ridge" in self.config.enabled_models:
            ridge_model = forecast.fit_ridge(X_train_norm, y_train, alpha=1.0)
            pred_ridge = ridge_model.estimator.predict(X_test_norm)
            predictions["ridge"] = pred_ridge
            horizon_metrics["ridge"] = compute_regression_metrics(y_test, pred_ridge, baseline_rmse=base_rmse)

        # 5. LightGBM Regressor
        if "lightgbm" in self.config.enabled_models:
            try:
                lgbm_model = forecast.fit_lightgbm(X_train_norm, y_train, seed=self.config.seed)
                pred_lgbm = lgbm_model.estimator.predict(X_test_norm)
                predictions["lightgbm"] = pred_lgbm
                horizon_metrics["lightgbm"] = compute_regression_metrics(y_test, pred_lgbm, baseline_rmse=base_rmse)
            except Exception as e:
                logger.warning(f"LightGBM not available: {e}")

        # ----------------------------------------------------------------------
        # C. Deep Learning Sequence Model (deepl.py)
        # ----------------------------------------------------------------------
        if "lstm" in self.config.enabled_models and deepl.torch is not None:
            try:
                window_size = min(self.config.window_size, len(X_train_norm) // 4)
                seq_train = deepl.make_sequence_windows(X_train_norm, y_train, window_size=window_size)
                seq_test = deepl.make_sequence_windows(X_test_norm, y_test, window_size=window_size)

                lstm_net = deepl.ClimateLSTM(
                    input_size=seq_train.features.shape[-1],
                    hidden_size=32,
                    output_size=1,
                )
                criterion = deepl.nn.MSELoss()
                optimizer = deepl.torch.optim.Adam(lstm_net.parameters(), lr=0.01)

                train_feat_t = deepl.torch.tensor(seq_train.features)
                train_targ_t = deepl.torch.tensor(seq_train.targets).unsqueeze(-1)

                # Train for 50 compact epochs
                lstm_net.train()
                for epoch in range(40):
                    optimizer.zero_grad()
                    out = lstm_net(train_feat_t)
                    loss = criterion(out, train_targ_t)
                    loss.backward()
                    optimizer.step()

                lstm_net.eval()
                with deepl.torch.no_grad():
                    test_feat_t = deepl.torch.tensor(seq_test.features)
                    pred_lstm_win = lstm_net(test_feat_t).squeeze(-1).numpy()

                # Align test predictions length
                pad_len = len(y_test) - len(pred_lstm_win)
                if pad_len > 0:
                    pred_lstm = np.concatenate([np.full(pad_len, pred_lstm_win[0]), pred_lstm_win])
                else:
                    pred_lstm = pred_lstm_win[: len(y_test)]

                predictions["lstm"] = pred_lstm
                horizon_metrics["lstm"] = compute_regression_metrics(y_test, pred_lstm, baseline_rmse=base_rmse)
            except Exception as e:
                logger.warning(f"LSTM training skipped: {e}")

        # ----------------------------------------------------------------------
        # D. ENSO Classification Model (classif.py)
        # ----------------------------------------------------------------------
        if "enso_classifier" in self.config.enabled_models:
            train_labels = classif.enso_phase(y_train)
            test_labels = classif.enso_phase(y_test)

            calibrated_clf = classif.fit_calibrated_classifier(
                X_train_norm, train_labels, seed=self.config.seed
            )
            pred_classes = calibrated_clf.predict(X_test_norm)
            pred_probs = calibrated_clf.predict_proba(X_test_norm)

            clf_metrics = compute_classification_metrics(test_labels, pred_classes, pred_probs)
            horizon_metrics["calibrated_logistic_classifier"] = clf_metrics

        # Record metrics formatted for database storage
        for model_name, m_dict in horizon_metrics.items():
            record = {
                "model_name": model_name,
                "target_variable": target_col,
                "region_name": self.config.region_name,
                "lead_horizon": horizon,
                "mae": m_dict.get("mae"),
                "rmse": m_dict.get("rmse"),
                "r2_score": m_dict.get("r2_score"),
                "accuracy": m_dict.get("accuracy"),
                "f1_score": m_dict.get("f1_score"),
                "roc_auc": m_dict.get("roc_auc"),
                "brier_score": m_dict.get("brier_score"),
                "sample_size": m_dict.get("sample_size", len(y_test)),
            }
            self.evaluation_records.append(record)

        return predictions, horizon_metrics, test_dates, y_test

    def run_full_pipeline(
        self,
        df: Optional[pd.DataFrame] = None,
    ) -> Tuple[pd.DataFrame, Dict[int, Dict[str, np.ndarray]]]:
        """Execute full training and evaluation across all configured horizons.

        Returns:
            Tuple of (metrics_dataframe, predictions_by_horizon).
        """
        climate_df = df if df is not None else load_climate_dataframe(self.config.zarr_store_path)
        self.evaluation_records.clear()
        predictions_by_horizon: Dict[int, Dict[str, np.ndarray]] = {}

        print(f"\n[RUNNING CLIMATE LEARNING PIPELINE]: Target={self.config.target_variable}, Region={self.config.region_name}")

        for h in self.config.horizons:
            print(f"  -> Fitting and evaluating models for lead horizon h = {h} bulan...")
            preds, metrics, test_dates, actual = self.run_horizon_experiment(climate_df, horizon=h)
            predictions_by_horizon[h] = preds

        metrics_df = pd.DataFrame(self.evaluation_records)
        return metrics_df, predictions_by_horizon


# ==============================================================================
# SECTION 6: PERSISTENCE & DATABASE RETURN
# ==============================================================================

def save_metrics_to_db(
    metrics_df: pd.DataFrame,
    database_url: Optional[str] = None,
) -> int:
    """Store evaluated model metrics into the PostgreSQL database.

    Inserts records into the new ``model_metrics`` table created in ``init.sql``.

    Args:
        metrics_df: DataFrame containing model evaluation records.
        database_url: Optional connection string; falls back to DATABASE_URL.

    Returns:
        Number of inserted rows.
    """
    if metrics_df.empty:
        logger.info("Metrics DataFrame is empty. No records to save.")
        return 0

    try:
        db = Database(database_url=database_url)
        db.init_schema()
        inserted = db.store_metrics(metrics_df)
        db.close()
        print(f"[SUCCESS] Berhasil menyimpan {inserted} baris metrik model ke tabel PostgreSQL 'model_metrics'!")
        return inserted
    except Exception as e:
        logger.warning(
            f"[DB NOTICE] Tidak dapat terhubung ke database ({e}). "
            f"Metrik tetap dikembalikan sebagai DataFrame untuk audit lokal."
        )
        return 0


# ==============================================================================
# SECTION 7: VISUALIZATION & DIAGNOSTICS INTEGRATION
# ==============================================================================

def generate_pipeline_visualizations(
    metrics_df: pd.DataFrame,
    actual_series: pd.Series,
    predictions: Dict[str, np.ndarray],
    horizon: int = 1,
    output_dir: Union[str, Path] = "reports/figures",
    show: bool = False,
) -> List[Path]:
    """Generate and save all diagnostic visualisations using src.utils.Visuals."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved_files: List[Path] = []

    dates = actual_series.index

    # 1. Metrics Comparison Bar Chart
    if not metrics_df.empty and "rmse" in metrics_df.columns:
        p1 = out_dir / "learning_metrics_comparison.png"
        Visuals.plot_metrics_comparison(
            metrics_df,
            metric_col="rmse",
            horizon_col="lead_horizon" if "lead_horizon" in metrics_df.columns else None,
            title="Perbandingan Evaluasi Model (RMSE) Antar-Horizon",
            save_path=p1,
            show=show,
        )
        saved_files.append(p1)

    # 2. Forecast vs. Actual
    if predictions:
        p2 = out_dir / f"learning_forecast_vs_actual_h{horizon}.png"
        Visuals.plot_forecast_vs_actual(
            dates=dates,
            actual=actual_series.to_numpy(),
            predictions=predictions,
            horizon=horizon,
            save_path=p2,
            show=show,
        )
        saved_files.append(p2)

    # 3. Residual Analysis for Best Performing Model
    candidate_model = "lightgbm" if "lightgbm" in predictions else "ridge" if "ridge" in predictions else list(predictions.keys())[0]
    p3 = out_dir / f"learning_residuals_{candidate_model}.png"
    Visuals.plot_residuals(
        actual=actual_series.to_numpy(),
        predicted=predictions[candidate_model],
        dates=dates,
        model_name=candidate_model.upper(),
        save_path=p3,
        show=show,
    )
    saved_files.append(p3)

    # 4. ENSO Timeline with Phase Shading
    p4 = out_dir / "learning_enso_phase_timeline.png"
    Visuals.plot_enso_timeline(
        dates=dates,
        oni_values=actual_series.to_numpy(),
        title="Timeline Fase ENSO Periode Uji Evaluasi",
        save_path=p4,
        show=show,
    )
    saved_files.append(p4)

    return saved_files


# ==============================================================================
# SECTION 8: STANDALONE DEMONSTRATION & VERIFICATION
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("KMRV MACHINE LEARNING & FORECAST EVALUATION PIPELINE (learning.py)")
    print("=" * 80)

    # Initialize configuration
    config = LearningConfig(
        target_variable="ANOM",
        region_name="Pasifik_Nino34",
        horizons=(1, 3, 6),
        lags=(1, 2, 3, 6, 12),
        enabled_models=("persistence", "climatology", "seasonal_naive", "ridge", "lightgbm", "lstm", "enso_classifier"),
    )

    # Load dataset
    df = load_climate_dataframe(config.zarr_store_path)
    print(f"\n[DATASET LOADED]: {len(df)} bulan observasi ({df.index.min().strftime('%Y-%m')} s.d. {df.index.max().strftime('%Y-%m')})")
    print(f"Variabel tersedia: {list(df.columns)}")

    # Execute training and evaluation pipeline
    pipeline = ClimateLearningPipeline(config)
    metrics_df, predictions_by_h = pipeline.run_full_pipeline(df)

    # Display Metrics Summary Table
    print("\n" + "=" * 80)
    print("TABEL METRIK EVALUASI HASIL PEMBELAJARAN (Adhering to DB table 'model_metrics'):")
    print("=" * 80)
    cols_to_print = ["model_name", "lead_horizon", "mae", "rmse", "r2_score", "accuracy", "f1_score", "sample_size"]
    avail_cols = [c for c in cols_to_print if c in metrics_df.columns]
    print(metrics_df[avail_cols].to_string(index=False))

    # Persist metrics to Database (with dry-run graceful fallback if offline)
    print("\n[MENYIMPAN METRIK KE POSTGRESQL]:")
    save_metrics_to_db(metrics_df)

    # Generate diagnostic visualizations using src.utils.Visuals
    print("\n[MEMBUAT VISUALISASI DIAGNOSTIK WAKTU & METRIK]:")
    h1_preds = predictions_by_h.get(1, {})
    if h1_preds:
        # Extract corresponding test slice
        n_test = len(list(h1_preds.values())[0])
        test_slice = df["ANOM"].iloc[-n_test:]
        saved_plots = generate_pipeline_visualizations(
            metrics_df=metrics_df,
            actual_series=test_slice,
            predictions=h1_preds,
            horizon=1,
            output_dir="notebook/reports/figures",
            show=False,
        )
        for p in saved_plots:
            print(f"  -> Visualisasi tersimpan di: {p}")

    print("\n[SUKSES] learning.py berhasil mengeksekusi pipeline machine-learning lengkap!")
