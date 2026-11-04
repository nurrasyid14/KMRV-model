-- Mengaktifkan ekstensi PostGIS untuk pengolahan data spasial wilayah perairan Indonesia
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Tabel Master Wilayah Perairan / Grid Metadata
CREATE TABLE IF NOT EXISTS mhw_regions (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,       -- Contoh: "Perairan Laut Banda", "Selat Makassar"
    lat_min FLOAT NOT NULL,
    lat_max FLOAT NOT NULL,
    lon_min FLOAT NOT NULL,
    lon_max FLOAT NOT NULL,
    geom GEOMETRY(Polygon, 4326)             -- Batas polygon spasial wilayah
);

-- 2. Tabel Data Observasi Harian NetCDF (NOAA OISST) per Grid/Titik
CREATE TABLE IF NOT EXISTS oisst_daily_observations (
    obs_id BIGSERIAL PRIMARY KEY,
    time_stamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    sst FLOAT,                               -- Sea Surface Temperature (°C)
    anom FLOAT,                              -- Sea Surface Temperature Anomaly (°C)
    err FLOAT,                               -- Error estimate
    ice FLOAT,                               -- Sea ice concentration (0-1)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indeks untuk mempercepat kueri spasial-temporal
    CONSTRAINT unique_obs_grid_time UNIQUE (time_stamp, latitude, longitude)
);

CREATE INDEX idx_oisst_time_lat_lon ON oisst_daily_observations (time_stamp, latitude, longitude);

-- 3. Tabel Indeks Iklim (ENSO & IOD)
CREATE TABLE IF NOT EXISTS climate_indices (
    index_id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    enso_index FLOAT NOT NULL,               -- Nilai indeks ENSO (Nino 3.4, dll)
    iod_index FLOAT NOT NULL,                -- Nilai Indeks Dipole Mode (IOD)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabel Hasil Prediksi Model Hibrid (PyTorch LSTM + LightGBM)
CREATE TABLE IF NOT EXISTS mhw_predictions (
    prediction_id BIGSERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    target_date DATE NOT NULL,               -- Tanggal yang diprediksi
    sst_anomaly FLOAT NOT NULL,              -- Prediksi Anomali Suhu Laut
    enso_index FLOAT NOT NULL,               -- Indeks ENSO saat inferensi
    iod_index FLOAT NOT NULL,                -- Indeks IOD saat inferensi
    mhw_category VARCHAR(50) NOT NULL,       -- Kategori: Moderate, Strong, Severe, Extreme
    duration_days INT,                       -- Estimasi durasi kejadian MHW
    model_version VARCHAR(50) DEFAULT 'PyTorch-LSTM-v1.0',
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mhw_pred_date_region ON mhw_predictions (target_date, region_name);

-- 5. Tabel Metrik Evaluasi Model (Model Performance & Forecast Metrics)
CREATE TABLE IF NOT EXISTS model_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,        -- Contoh: "persistence", "climatology", "ridge", "lightgbm", "lstm"
    target_variable VARCHAR(100) NOT NULL,   -- Contoh: "ONI", "sst_anomaly", "enso_phase", "rainfall"
    region_name VARCHAR(100),                -- Contoh: "Pasifik_Nino34", "Selat_Makassar", "Global"
    lead_horizon INT,                        -- Horizon peramalan (bulan, misal 1, 3, 6, 12)
    mae FLOAT,                               -- Mean Absolute Error
    rmse FLOAT,                              -- Root Mean Squared Error
    r2_score FLOAT,                          -- Coefficient of Determination (R²)
    accuracy FLOAT,                          -- Accuracy / Balanced Accuracy
    f1_score FLOAT,                          -- Macro / Binary F1 Score
    roc_auc FLOAT,                           -- ROC-AUC Score
    brier_score FLOAT,                       -- Brier Score (Probabilistic Calibration)
    sample_size INT,                         -- Jumlah sampel evaluasi / hindcast
    evaluated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_model_metrics_name_target ON model_metrics (model_name, target_variable, lead_horizon);

-- Create a limited application/member login without sharing the bootstrap superuser.
\getenv app_user DB_MEMBER_USER
\getenv app_password DB_MEMBER_PASSWORD
\getenv admin_user POSTGRES_USER
\getenv database_name POSTGRES_DB
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'app_user', :'app_password') \gexec
GRANT CONNECT ON DATABASE :"database_name" TO :"app_user";
GRANT USAGE ON SCHEMA public TO :"app_user";
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO :"app_user";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO :"app_user";
ALTER DEFAULT PRIVILEGES FOR ROLE :"admin_user" IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE ON TABLES TO :"app_user";
ALTER DEFAULT PRIVILEGES FOR ROLE :"admin_user" IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO :"app_user";