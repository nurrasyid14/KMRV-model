# KMRV Climate Intelligence Dashboard (Frontend)

Dashboard pemantauan dan inferensi iklim maritim berbasis deep learning untuk proyek **KMRV-model**:
- Pemantauan anomali dan fase ENSO (El Niño / La Niña)
- Telemetri Suhu Permukaan Laut (SST) perairan Indonesia
- Deteksi kejadian Marine Heatwave (MHW)
- Matriks respons curah hujan regional Indonesia per musim

## Menjalankan Dashboard

```bash
cd frontend
npm install
npm run dev
```

Akses aplikasi di `http://localhost:5174/` (atau port default Vite `5173`).

Untuk melakukan production build:
```bash
npm run build
```

---

## Cara Menyambungkan ke Backend (FastAPI + PostgreSQL + Zarr)

Seluruh konsumsi data di frontend telah dipusatkan dalam satu modul terisolasi:
📂 `frontend/src/data/climateData.js`

### 1. Endpoint RESTful Backend yang Dibutuhkan
Ketika backend Python (FastAPI) siap, ganti fungsi impor mock di `climateData.js` dengan panggilan `fetch()` ke endpoint berikut:

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

Sesuai prinsip kejujuran data (Rule of Honesty), modul inferensi dan dampak iklim yang masih dalam tahap training/pengembangan diberi label jelas **"Data contoh"** atau **"Simulasi"** pada UI:

| Komponen | File | Status Data | Keterangan |
|---|---|---|---|
| **Peluang Fase 3 Bulan (KPI)** | `src/pages/Ringkasan.jsx` | ⚠️ Simulasi Model | Probabilitas fase dihitung dari mock ensemble; ganti dengan inferensi live model KMRV. |
| **Status MHW Selat Makassar** | `src/pages/Ringkasan.jsx` | ⚠️ Data Contoh | Deteksi MHW Selat Makassar menggunakan mock event untuk demonstrasi UI. |
| **Pita Ketidakpastian (80% CI)** | `src/pages/Ringkasan.jsx` | ⚠️ Simulasi Model | Nilai confidence band dihitung dari standar deviasi mock. |
| **Plume Ensemble Trajectory** | `src/pages/PrakiraanENSO.jsx` | ⚠️ Data Contoh | Kurva 20 lintasan ensemble disimulasikan dari distribusi Gaussian. |
| **Tabel Riwayat MHW** | `src/pages/Laut.jsx` | ⚠️ Data Contoh | Daftar event MHW merupakan dataset contoh berdasarkan skema Hobday et al. (2016). |
| **Matriks Hujan Regional** | `src/pages/DampakIndonesia.jsx` | ⚠️ Simulasi ERA5 | Angka deviasi hujan dihitung dari statistik komposit historis, belum divalidasi stasiun real-time BMKG. |
| **Nilai Aktual OISST & Indeks Global** | `src/data/climateData.js` | ✅ Data Rujukan Riil | Nilai RONI (+0,62 °C), SOI (-7,8), dan DMI (+0,12 °C) merujuk data iklim riil NOAA CPC & BOM Australia. |
