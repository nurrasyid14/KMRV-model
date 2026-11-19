# KMRV Climate Intelligence Dashboard (Frontend)

Dashboard pemantauan dan inferensi iklim maritim berbasis deep learning untuk proyek **KMRV-model**:
- Pemantauan anomali dan fase ENSO (El Niño / La Niña)
- Telemetri Suhu Permukaan Laut (SST) perairan Indonesia
- Deteksi kejadian Marine Heatwave (MHW)
- Matriks respons curah hujan regional Indonesia per musim

## Menjalankan Dashboard

Untuk menjalankan frontend, API, dan model bersama-sama dari root proyek:

```bash
docker compose up --build model-service fastapi-backend frontend
```

Compose tetap membutuhkan variabel PostgreSQL di root `.env` untuk validasi
konfigurasi; siapkan file tersebut dari `.env.example` bila belum ada.
Dashboard tersedia di `http://localhost/`. Endpoint prediksi adalah
`GET /api/v1/forecast/latest?horizon=1` (horizon yang tersedia: `1`, `3`, `6`).
API memuat artefak model saat startup dan melakukan inferensi dari baris fitur
terakhir di `dataset/features_master_unscaled.csv`. Perbarui data fitur untuk
memakai input baru; endpoint ini tidak mengambil observasi iklim real-time.

Untuk pengembangan lokal, jalankan tiap bagian di terminal terpisah dari root
proyek:

```powershell
python -m pip install --index-url https://download.pytorch.org/whl/cpu --no-deps "torch==2.5.1+cpu"
python -m pip install -r model/requirements.txt
$env:MODEL_ARTIFACTS_DIR = (Resolve-Path .\model).Path
$env:FEATURES_FILE = (Resolve-Path .\dataset\features_master_unscaled.csv).Path
python -m uvicorn model.service:app --host 0.0.0.0 --port 8001
```

```powershell
$env:MODEL_SERVICE_URL = "http://localhost:8001"
python -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000
```

```powershell
Set-Location .\frontend
npm ci
npm run dev
```

Akses aplikasi di `http://localhost:5174/`.

Untuk production build frontend:
```bash
cd frontend
npm run build
```

---

## Kontrak Integrasi Prediksi

Komponen [`LatestForecast`](./src/components/LatestForecast.jsx) meminta
`/api/v1/forecast/latest` dari backend; backend meneruskan permintaan ke model
service. Riwayat dan metrik evaluasi tetap berasal dari snapshot yang dibuat
oleh `scripts/export_dashboard_data.py` di `src/data/realData.js`.

## Endpoint Backend Lainnya

### 1. Endpoint RESTful Backend yang Dibutuhkan
Endpoint di bawah ini masih berupa rancangan dan belum diimplementasikan:

| Method | Endpoint | Fungsi | Format Output |
|---|---|---|---|
| `GET` | `/api/v1/enso/latest` | Nilai RONI, ONI, SOI, DMI, dan status fase saat ini | JSON Object |
| `GET` | `/api/v1/forecast/plume?lead=3m` | Trajektori ensemble multi-member KMRV & 80% CI | Array of Numbers / Date |
| `GET` | `/api/v1/ocean/sst-regions` | Anomali SST harian & klimatologi 5 domain laut | GeoJSON / JSON Array |
| `GET` | `/api/v1/ocean/mhw-events` | Deteksi MHW aktif (SST > P90, $\ge$ 5 hari) | JSON Array of Events |
| `GET` | `/api/v1/rainfall/matrix?season=jja` | Matriks persentase anomali curah hujan regional | JSON Matrix |

### 2. Integrasi Zarr Array (Peta SST Grid Tinggi)
Untuk visualisasi layer raster OISST beresolusi penuh dari backend Zarr store:
1. Pasang layer Leaflet TMS/WMS atau GeoTIFF canvas layer di `frontend/src/components/SSTMap.jsx`.
2. Arahkan tile URL ke endpoint dynamic tiler FastAPI:
   `https://backend.kmrv.ac.id/api/v1/tiles/sst/{z}/{x}/{y}.png?date=2026-11-04`

---

## Daftar Komponen yang Menggunakan Data Contoh (Simulasi)

Fitur iklim yang masih dalam tahap pengembangan diberi label jelas **"Data contoh"** atau **"Simulasi"**. Kartu prediksi ONI menggunakan inferensi model, tetapi tetap menunjukkan tanggal input karena dataset saat ini bukan feed real-time:

| Komponen | File | Status Data | Keterangan |
|---|---|---|---|
| **Prediksi ONI dan fase (1/3/6 bulan)** | `src/components/LatestForecast.jsx` | ✅ Inferensi model | Diproses oleh Causal LSTM + XGBoost dari fitur terakhir yang tersedia. |
| **Status MHW Selat Makassar** | `src/pages/Ringkasan.jsx` | ⚠️ Data Contoh | Deteksi MHW Selat Makassar menggunakan mock event untuk demonstrasi UI. |
| **Pita Ketidakpastian (80% CI)** | `src/pages/Ringkasan.jsx` | ⚠️ Simulasi Model | Nilai confidence band dihitung dari standar deviasi mock. |
| **Plume Ensemble Trajectory** | `src/pages/PrakiraanENSO.jsx` | ⚠️ Data Contoh | Kurva 20 lintasan ensemble disimulasikan dari distribusi Gaussian. |
| **Tabel Riwayat MHW** | `src/pages/Laut.jsx` | ⚠️ Data Contoh | Daftar event MHW merupakan dataset contoh berdasarkan skema Hobday et al. (2016). |
| **Matriks Hujan Regional** | `src/pages/DampakIndonesia.jsx` | ⚠️ Simulasi ERA5 | Angka deviasi hujan dihitung dari statistik komposit historis, belum divalidasi stasiun real-time BMKG. |
| **Nilai Aktual OISST & Indeks Global** | `src/data/climateData.js` | ✅ Data Rujukan Riil | Nilai RONI (+0,62 °C), SOI (-7,8), dan DMI (+0,12 °C) merujuk data iklim riil NOAA CPC & BOM Australia. |
