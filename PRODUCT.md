# Product

<!-- impeccable:product-schema 1 -->

## Platform

Web (React + Vite, served sebagai SPA statis dari `frontend/dist`)

---

## Nama Proyek

**Lautan.id** — Dashboard monitoring iklim maritim dan prakiraan ENSO berbasis AI untuk perairan Indonesia.

> Repo ini bernama `KMRV-model` (nama repo saja, bukan nama model).
> Nama model sebenarnya adalah **Causal LSTM + LightGBM Ensemble** (lihat bagian Arsitektur).

---

## Konteks Akademik

- **Mata kuliah:** Proyek Sistem Cerdas, Semester 5, Program Studi Sains Data Terapan.
- **Tujuan akademik:** Membangun pipeline ML end-to-end yang reproducible untuk peramalan ENSO berbasis data publik NOAA, termasuk evaluasi jujur terhadap keterbatasan model.
- **Bukan layanan operasional:** Peringatan iklim resmi tetap menjadi wewenang BMKG.

---

## Pengguna

Dua audiens, diimbangi secara deliberat:

- **Penguji akademik:** Dosen/penguji dan sesama mahasiswa mata kuliah Proyek Sistem Cerdas yang mengevaluasi rigor: kejujuran penanganan data, metodologi, skill model, dan pernyataan keterbatasan.
- **Pengunjung umum / tertarik:** Aplikasi dibagikan secara publik. Pengunjung pertama kali harus bisa memahami kondisi ENSO terkini dan batas kemampuan model tanpa keahlian domain khusus.

**Ukuran keberhasilan:** Komunikasi jujur dan mudah dipahami tentang kondisi ENSO dan bukti model kepada kedua audiens. Tidak ada yang diinvensikan; tidak ada tampilan yang tidak penting.

---

## Tujuan Produk

Lautan.id adalah dashboard monitoring dan evaluasi iklim maritim Indonesia, berpusat pada El Niño–Southern Oscillation (ENSO). Ia menampilkan:

1. **ONI, SOI, dan DMI terbaru** dari dataset repo (bukan realtime feed).
2. **Anomali SST di lima domain maritim** — Nino 3.4 (referensi ENSO), Selat Karimata, Selat Makassar, Selatan Jawa, Maluku–Papua.
3. **Evaluasi jujur pipeline Causal LSTM + LightGBM** di tiga horizon prakiraan (1, 3, 6 bulan), termasuk horizon yang gagal.
4. **Arsip ONI historis** Januari 2016 – Juni 2025 beserta annotasi periode uji.

---

## Arsitektur Model (Detail Teknis)

### Model: Causal LSTM + LightGBM Ensemble

Pipeline dua tahap yang diimplementasikan di `src/ml/ensemble.py`:

#### Tahap 1 — Causal LSTM (Regresi ONI)
- **Framework:** PyTorch
- **File:** `src/ml/2lstm.py`, kelas `CausalLSTM`
- **Arsitektur:** `nn.LSTM` satu lapis, `input_size` = jumlah fitur, `hidden_size = 32`, `num_layers = 1`, `batch_first = True`
- **Regularisasi:** `nn.Dropout(0.1)` pada hidden state sebelum output linear
- **Output:** nilai kontinu ONI (`target_oni_lead_{h}m`) untuk horizon h = 1/3/6 bulan ke depan
- **Loss function:** MSELoss
- **Optimizer:** Adam, `lr = 0.003`
- **Training:** hingga 300 epoch, `batch_size = 16`, early stopping dengan patience 20 pada validation MSE
- **Input window:** 12 bulan berurutan (12-step lookback)
- **Preprocessing:** `StandardScaler` fit pada data training saja, disimpan sebagai `feature_scaler_horizon_{h}m.joblib` dan `target_scaler_horizon_{h}m.joblib`

#### Tahap 2 — LightGBM Phase Classifier
- **Framework:** LightGBM
- **File:** `src/ml/lgbm.py`, fungsi `create_phase_classifier`
- **Task:** Klasifikasi multikelas — La Niña (0), Netral (1), El Niño (2)
- **Hyperparameter:**
  - `objective = "multiclass"`, `num_class = 3`
  - `n_estimators = 300`, `learning_rate = 0.03`
  - `num_leaves = 7`, `max_depth = 3`
  - `min_child_samples = 5`, `subsample = 0.8`, `colsample_bytree = 0.8`
  - `reg_lambda = 1.0`, `random_state = 42`
- **Input fitur ke LightGBM:** prediksi LSTM (`lstm_oni`) + seluruh fitur tabular (iklim, lag, rolling, musiman)
- **Early stopping:** 50 round tanpa peningkatan pada validation set
- **Output tersimpan:** `lightgbm_horizon_{h}m.txt`

#### Orkestrasi & Split Data
- **Semua split kronologis:** tidak ada data masa depan yang bocor ke preprocessing atau pelatihan
- **Split:** training (Jan 2016 – Des 2021, 72 baris), validasi (Jan 2022 – Des 2023, 24 baris), uji (Jan 2024 – Jun 2025, 18 baris)
- **Seed fixed:** `seed_everything(42)` pada random, numpy, torch, dan cuda sebelum setiap training
- **Entry point training:** `python main.py --horizons 1 3 6`

---

## Dataset

### Sumber Data Upstream
| Sumber | Konten | Penggunaan |
|---|---|---|
| NOAA OISST v2.1 | SST harian 0,25° | SST regional (Niño 3.4, Karimata, Makassar, Jawa, Maluku) |
| NOAA CPC | ONI bulanan | Target ENSO |
| NOAA PSL | SOI bulanan | Fitur atmosfer |
| NOAA PSL | DMI (Dipole Mode Index) | Fitur Indian Ocean Dipole |

### Cakupan Dataset
- **Rentang waktu:** Januari 2016 – Juni 2025, bulanan (114 baris total)
- **File:** `dataset/features_master_unscaled.csv` (master, satuan fisik), dibagi ke `train_features.csv` / `val_features.csv` / `test_features.csv`

### Daftar Fitur Lengkap (68 kolom)
| Kelompok | Fitur |
|---|---|
| **Indeks ENSO** | `oni_anom`, `oni_total` |
| **Atmosfer** | `soi`, `dmi` |
| **SST Regional** | `sst_nino34`, `sst_karimata`, `sst_makassar`, `sst_jawa`, `sst_maluku` |
| **Gradien SST** | `sst_nino34_zonal_grad` |
| **MHW (Marine Heatwave)** | `mhw_nino34`, `mhw_karimata`, `mhw_makassar`, `mhw_jawa`, `mhw_maluku` *(mayoritas nol/konstan)* |
| **Curah hujan proxy** | `rain_malaysia`, `rain_hawaii` |
| **Musiman** | `month_sin`, `month_cos` |
| **Coupling index** | `enso_coupling_index` |
| **Lag ONI** | `oni_anom_lag1/2/3/6/12` |
| **Lag SOI** | `soi_lag1/2/3/6/12` |
| **Lag DMI** | `dmi_lag1/2/3/6/12` |
| **Lag SST Niño 3.4** | `sst_nino34_lag1/2/3/6/12` |
| **Lag gradien SST** | `sst_nino34_zonal_grad_lag1/2/3/6/12` |
| **Lag SST Makassar** | `sst_makassar_lag1/2/3/6/12` |
| **Lag curah hujan** | `rain_malaysia_lag1/2/3/6/12` |
| **Rolling ONI** | `oni_anom_roll3_mean`, `oni_anom_roll3_std`, `oni_anom_roll6_mean` |
| **Rolling SOI** | `soi_roll3_mean`, `soi_roll3_std`, `soi_roll6_mean` |
| **Rolling DMI** | `dmi_roll3_mean`, `dmi_roll3_std`, `dmi_roll6_mean` |
| **Rolling SST Niño 3.4** | `sst_nino34_roll3_mean`, `sst_nino34_roll3_std`, `sst_nino34_roll6_mean` |
| **Target** | `target_oni_lead_1m/3m/6m`, `target_phase_lead_1m/3m/6m` |

---

## Metrik Model (Verified dari Artifact)

### Horizon 1 Bulan — ★ Satu-satunya horizon andal
| Metrik | Validasi | Uji |
|---|---|---|
| Accuracy | 76,9% | **71,4%** |
| Balanced Accuracy | 79,2% | 71,4% |
| Macro F1 | 66,8% | 41,7% |
| LSTM RMSE (ONI) | 1,175 °C | **0,180 °C** |

**Confusion Matrix (Uji):** 5 benar dari 7 — 2 bulan Netral salah ditebak La Niña.

### Horizon 3 Bulan — Trivial Majority Class
| Metrik | Validasi | Uji |
|---|---|---|
| Accuracy | 23,1% | 100%* |
| LSTM RMSE (ONI) | 1,257 °C | 0,174 °C |

*Accuracy 100% semu: seluruh 7 bulan uji berkondisi Netral, model menebak Netral semua. Bukan skill prediktif nyata.

### Horizon 6 Bulan — Gagal
| Metrik | Validasi | Uji |
|---|---|---|
| Accuracy | 0% | **0%** |
| LSTM RMSE (ONI) | 1,258 °C | 0,217 °C |

Model selalu menebak satu kelas; prediksi tidak dapat diandalkan.

### Perbandingan dengan Persistence Baseline
> Model TIDAK mengalahkan persistence (prediksi "bulan ini sama dengan bulan lalu"):

| Horizon | MAE LSTM | MAE Persistence |
|---|---|---|
| 1 bulan | 0,172 | 0,108 |
| 3 bulan | 0,152 | 0,098 |
| 6 bulan | 0,197 | 0,100 |

---

## Domain Maritim yang Dipantau

| Domain | Koordinat | Peran |
|---|---|---|
| Pasifik Niño 3.4 | 5°LS–5°LU, 170°BB–120°BB | Referensi indeks ENSO utama |
| Selat Makassar | 5°LS–2°LU, 116°BT–120°BT | Respons lokal Indonesia |
| Selat Karimata | 3°LS–2°LU, 105°BT–110°BT | Respons lokal Indonesia |
| Selatan Jawa | 12°LS–8°LS, 105°BT–115°BT | Respons lokal Indonesia |
| Maluku–Papua | 3°LS–3°LU, 125°BT–140°BT | Respons lokal Indonesia |

---

## Struktur Proyek

```
KMRV-model/
├── dataset/                    # Data CSV (train/val/test + master)
│   ├── features_master_unscaled.csv
│   ├── train_features.csv      # Jan 2016–Des 2021 (72 baris)
│   ├── val_features.csv        # Jan 2022–Des 2023 (24 baris)
│   └── test_features.csv       # Jan 2024–Jun 2025 (18 baris)
├── model/
│   ├── enso_ensemble_1m/       # Artifact horizon 1 bulan
│   │   ├── lstm_horizon_1m.pt
│   │   ├── lightgbm_horizon_1m.txt
│   │   ├── feature_scaler_horizon_1m.joblib
│   │   ├── target_scaler_horizon_1m.joblib
│   │   ├── metrics_horizon_1m.json
│   │   └── test_predictions_horizon_1m.csv
│   ├── enso_ensemble_3m/       # Artifact horizon 3 bulan
│   ├── enso_ensemble_6m/       # Artifact horizon 6 bulan
│   └── model_manifest.json     # best_validation_horizon_months = 1
├── src/
│   ├── ml/
│   │   ├── 2lstm.py            # CausalLSTM (PyTorch)
│   │   ├── lgbm.py             # LightGBM phase classifier
│   │   └── ensemble.py         # Pipeline orkestrasi 2-tahap
│   ├── preprocessing.py        # Feature engineering
│   ├── etl.py                  # Data download & transformasi
│   ├── pipeline.py             # run_full_pipeline()
│   └── utils.py                # Helper
├── scripts/
│   └── export_dashboard_data.py # Ekspor realData.js dari CSV+artifacts
├── frontend/                   # React + Vite SPA
│   ├── src/
│   │   ├── pages/Dashboard.jsx
│   │   ├── components/         # Chart, map, confusion matrix, dll
│   │   ├── data/realData.js    # Data dihasilkan oleh export script
│   │   └── utils/
│   └── dist/                   # Build output
├── main.py                     # Entry point training
└── README.md                   # Dokumentasi ENSO & metodologi
```

---

## Pipeline Data ke Frontend

```
dataset/*_features.csv
  + model/enso_ensemble_*/metrics_*.json
  + model/enso_ensemble_*/test_predictions_*.csv
       ↓
  python scripts/export_dashboard_data.py
       ↓
  frontend/src/data/realData.js   ← satu-satunya sumber data UI
       ↓
  npm run build (Vite)
       ↓
  frontend/dist/   ← deployed static files
```

UI **tidak membuat network call apapun** untuk data. Semua angka bersumber dari `realData.js` yang dihasilkan dari dataset dan artifact model nyata.

---

## Observasi Terbaru (Juni 2025, dari Dataset)

| Indikator | Nilai | Interpretasi |
|---|---|---|
| ONI | −0,02 °C | **Netral** (antara −0,5 dan +0,5) |
| SOI | +0,097 | Sedikit positif |
| DMI | −0,477 °C | Mendekati batas negatif |
| SST Niño 3.4 | −0,119 °C (anomali) | Sedikit dingin dari normal |
| SST Selat Makassar | +0,181 °C (anomali) | Sedikit hangat |
| SST Selatan Jawa | +0,262 °C (anomali) | Sedikit hangat |

> **Catatan:** semua kolom SST adalah **anomali terhadap rata-rata bulan yang sama** (bukan suhu absolut). Bukan kondisi hari ini — ini adalah bulan terakhir dalam dataset historis.

---

## Keterbatasan yang Harus Dikomunikasikan

1. **Bukan realtime:** Data terakhir adalah Juni 2025. Tidak ada feed NOAA langsung.
2. **Persistence mengalahkan model di semua horizon MAE.**
3. **Kolom MHW (marine heatwave) mayoritas nol atau konstan** — data MHW regional Indonesia yang memadai tidak tersedia dalam dataset ini.
4. **Kolom curah hujan hanya proxy** (`rain_malaysia`, `rain_hawaii`) — matriks curah hujan regional Indonesia tidak tersedia.
5. **Horizon 3 dan 6 bulan tidak andal** — horizon 3 bulan adalah trivial majority class; horizon 6 bulan gagal total.
6. **Backend tidak diimplementasikan:** `backend/` hanya berisi `Dockerfile` dan `requirements.txt`.

---

## Prinsip Desain

1. **Kejujuran adalah desain.** Setiap angka dapat dilacak ke kolom dataset atau file artifact; horizon lemah dan baseline yang kalah ditampilkan, bukan disembunyikan.
2. **Kemudahan memahami menang.** Tampilkan ONI terbaru dan fasenya terlebih dahulu; detail ada di halaman evaluasi.
3. **Bukti, bukan janji.** Evaluasi historis saja; tidak ada prakiraan masa depan selama inferensi belum di-serve secara live.
4. **Berbasis Indonesia.** Niño 3.4 sebagai indeks, laut Indonesia sebagai domain respons.
5. **Bahasa Indonesia.** Seluruh teks UI dalam bahasa Indonesia; koma desimal Indonesia (mis., "−0,11 °C").

---

## Komitmen Brand

- **Nama produk:** Lautan.id
- **Tagline:** "Pantau Iklim & Dinamika Laut Indonesia"
- **Warna primer:** `#00a3c4` (biru laut)
- **Tipografi nilai numerik:** font monospaced (Outlier/Roboto Mono) untuk kejelasan angka
- **Semua teks UI:** Bahasa Indonesia; notasi desimal koma

---

## Aksesibilitas

Praktik baik tanpa target WCAG formal: kontras teks memadai, operabilitas keyboard dan fokus terlihat, chart dengan judul/deskripsi aksesibel, dan state El Niño/La Niña tidak disampaikan hanya lewat warna.

---

## Pengembangan Lanjutan (Belum Diimplementasikan)

- Feed NOAA realtime via backend proxy
- Retraining sehingga horizon 3/6 bulan mendapat skill nyata
- Peta interaktif Leaflet untuk arsip SST bulanan
- Inferensi live (saat ini model hanya tersimpan sebagai artifact statis)
