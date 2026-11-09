/**
 * KMRV-model: Sumber data terpusat (Mock & Telemetri Iklim)
 * Memisahkan state data dari komponen UI agar mudah dihubungkan ke endpoint FastAPI backend.
 * Seluruh data prakiraan dan dampak saat ini bertanda isSimulated: true.
 */

export const climateDatasetMeta = {
  version: "v2.1-preview",
  lastUpdated: "4 November 2026",
  nextScheduledUpdate: "11 November 2026",
  sstProvider: "NOAA Daily OISST v2.1 (AVHRR-only 0,25°)",
  climateIndicesProvider: "NOAA Climate Prediction Center (CPC) & BOM Australia",
  rainfallProvider: "CHIRPS v2.0 & ERA5 Reanalysis (Validasi BMKG)",
  backendStatus: "Modul inferensi offline (simulasi)"
};

// Nilai Indeks Terkini
export const currentClimateState = {
  roniLatest: 0.62,
  roniStatus: "El Niño Lemah",
  roniDate: "November 2026 (Rata-rata bergerak 3 bulan)",
  oniHistorical: 0.58,
  soiValue: -7.8,
  soiStatus: "Sirkulasi Walker melemah (konsisten El Niño)",
  dmiValue: 0.12,
  dmiStatus: "Fase IOD Netral",
  leadTimes: {
    "1 bulan": {
      label: "Lead 1 Bulan",
      targetMonth: "Desember 2026",
      roniForecast: "+0,68 °C",
      uncertaintyBand: "±0,22 °C",
      elNinoProb: 58,
      neutralProb: 34,
      laNinaProb: 8,
      kmrvMae: 0.31,
      persMae: 0.38,
      klimMae: 0.65,
      brierScore: 0.14
    },
    "3 bulan": {
      label: "Lead 3 Bulan",
      targetMonth: "Februari 2027",
      roniForecast: "+0,94 °C",
      uncertaintyBand: "±0,35 °C",
      elNinoProb: 64,
      neutralProb: 26,
      laNinaProb: 10,
      kmrvMae: 0.42,
      persMae: 0.55,
      klimMae: 0.71,
      brierScore: 0.19
    },
    "6 bulan": {
      label: "Lead 6 Bulan",
      targetMonth: "Mei 2027",
      roniForecast: "+1,20 °C",
      uncertaintyBand: "±0,48 °C",
      elNinoProb: 68,
      neutralProb: 24,
      laNinaProb: 8,
      kmrvMae: 0.54,
      persMae: 0.72,
      klimMae: 0.79,
      brierScore: 0.24
    }
  }
};

// 24 Bulan Historis RONI + 6 Bulan Prakiraan Model KMRV
export const roniTimeSeries = [
  { date: 'Nov 24', value: -0.42, isForecast: false },
  { date: 'Des 24', value: -0.55, isForecast: false },
  { date: 'Jan 25', value: -0.68, isForecast: false },
  { date: 'Feb 25', value: -0.62, isForecast: false },
  { date: 'Mar 25', value: -0.45, isForecast: false },
  { date: 'Apr 25', value: -0.30, isForecast: false },
  { date: 'Mei 25', value: -0.15, isForecast: false },
  { date: 'Jun 25', value: 0.05, isForecast: false },
  { date: 'Jul 25', value: 0.18, isForecast: false },
  { date: 'Agu 25', value: 0.24, isForecast: false },
  { date: 'Sep 25', value: 0.32, isForecast: false },
  { date: 'Okt 25', value: 0.45, isForecast: false },
  { date: 'Nov 25', value: 0.52, isForecast: false },
  { date: 'Des 25', value: 0.48, isForecast: false },
  { date: 'Jan 26', value: 0.35, isForecast: false },
  { date: 'Feb 26', value: 0.22, isForecast: false },
  { date: 'Mar 26', value: 0.18, isForecast: false },
  { date: 'Apr 26', value: 0.25, isForecast: false },
  { date: 'Mei 26', value: 0.38, isForecast: false },
  { date: 'Jun 26', value: 0.42, isForecast: false },
  { date: 'Jul 26', value: 0.49, isForecast: false },
  { date: 'Agu 26', value: 0.55, isForecast: false },
  { date: 'Sep 26', value: 0.58, isForecast: false },
  { date: 'Okt 26', value: 0.62, isForecast: false },
  // 6 Bulan Prakiraan KMRV dengan batas atas & bawah (80% CI)
  { date: 'Nov 26', value: 0.68, lower: 0.46, upper: 0.90, isForecast: true },
  { date: 'Des 26', value: 0.78, lower: 0.50, upper: 1.06, isForecast: true },
  { date: 'Jan 27', value: 0.88, lower: 0.55, upper: 1.21, isForecast: true },
  { date: 'Feb 27', value: 0.94, lower: 0.59, upper: 1.29, isForecast: true },
  { date: 'Mar 27', value: 1.05, lower: 0.65, upper: 1.45, isForecast: true },
  { date: 'Apr 27', value: 1.20, lower: 0.72, upper: 1.68, isForecast: true }
];

// Anomali SST 5 Wilayah Perairan KMRV
export const regionalOceanData = [
  {
    id: "nino34",
    name: "Pasifik Niño 3.4",
    sstVal: 27.8,
    climatology: 26.9,
    anomaly: "+0,9",
    num: 0.9,
    mhwStatus: "Tidak ada",
    mhwDuration: 0,
    mhwIntensity: "-",
    significance: "Indeks rujukan global; anomali hangat melemahkan sirkulasi konvektif di atas Indonesia.",
    isSimulated: false
  },
  {
    id: "makassar",
    name: "Selat Makassar",
    sstVal: 29.4,
    climatology: 28.7,
    anomaly: "+0,7",
    num: 0.7,
    mhwStatus: "Aktif (Kategori II Moderat)",
    mhwDuration: 14,
    mhwIntensity: "+1,4 °C di atas P90",
    significance: "Jalur utama Arlindo (Indonesian Throughflow); retensi panas memicu pergeseran migrasi ikan pelagis.",
    isSimulated: true
  },
  {
    id: "karimata",
    name: "Selat Karimata",
    sstVal: 29.1,
    climatology: 28.7,
    anomaly: "+0,4",
    num: 0.4,
    mhwStatus: "Tidak ada",
    mhwDuration: 0,
    mhwIntensity: "-",
    significance: "Penghubung perairan dangkal paparan Sunda; suplai uap air ke wilayah barat Indonesia.",
    isSimulated: true
  },
  {
    id: "jawa",
    name: "Selatan Jawa",
    sstVal: 26.8,
    climatology: 26.6,
    anomaly: "+0,2",
    num: 0.2,
    mhwStatus: "Tidak ada",
    mhwDuration: 0,
    mhwIntensity: "-",
    significance: "Zona upwelling musiman dinamis; respons tinggi terhadap interaksi ENSO dan angin pasat tenggara.",
    isSimulated: true
  },
  {
    id: "maluku",
    name: "Maluku-Papua",
    sstVal: 29.3,
    climatology: 29.4,
    anomaly: "-0,1",
    num: -0.1,
    mhwStatus: "Tidak ada",
    mhwDuration: 0,
    mhwIntensity: "-",
    significance: "Kolam hangat Pasifik barat; pusat konveksi konstan dengan variabilitas musiman rendah.",
    isSimulated: true
  }
];

// Tabel Kejadian Marine Heatwave (MHW) Berdasarkan Definisi Hobday et al. (2016)
export const mhwEventsRecords = [
  {
    region: "Selat Makassar",
    startDate: "21 Okt 2026",
    status: "Sedang berlangsung",
    duration: "14 hari",
    maxIntensity: "+1,42 °C",
    category: "Kategori II (Moderat)",
    impactSummary: "Tekanan termal pada ekosistem terumbu karang karang dangkal dan penurunan klorofil-a.",
    isSimulated: true
  },
  {
    region: "Selatan Jawa",
    startDate: "12 Agu 2026",
    status: "Selesai",
    duration: "8 hari",
    maxIntensity: "+1,15 °C",
    category: "Kategori I (Lemah)",
    impactSummary: "Upwelling tertekan sementara, penundaan puncak musim tangkap lemuru.",
    isSimulated: true
  },
  {
    region: "Selat Karimata",
    startDate: "02 Mei 2026",
    status: "Selesai",
    duration: "6 hari",
    maxIntensity: "+0,98 °C",
    category: "Kategori I (Lemah)",
    impactSummary: "Suhu permukaan laut meningkat tipis tanpa dampak pemutihan karang meluas.",
    isSimulated: true
  }
];

// Matriks Respons Hujan Regional Indonesia per Musim (Heatmap)
// Angka mewakili persentase deviasi curah hujan dari klimatologi 1991-2020 selama fase El Niño aktif
export const regionalRainfallMatrix = [
  {
    region: "Sumatera (Bagian Selatan)",
    djf: -10,
    mam: -18,
    jja: -32,
    son: -28,
    primaryRisk: "Penurunan curah hujan puncak kemarau (JJA) meningkatkan potensi hotspot kebakaran hutan dan lahan.",
    isSimulated: true
  },
  {
    region: "Jawa, Bali, dan Nusa Tenggara",
    djf: -8,
    mam: -22,
    jja: -45,
    son: -38,
    primaryRisk: "Keterlambatan awal musim hujan dan kemarau lebih kering, menekan ketersediaan air irigasi waduk utama.",
    isSimulated: true
  },
  {
    region: "Kalimantan (Selatan & Tengah)",
    djf: -5,
    mam: -15,
    jja: -38,
    son: -30,
    primaryRisk: "Pengeringan lapisan gambut pada fase kemarau mempercepat eskalasi kabut asap regional.",
    isSimulated: true
  },
  {
    region: "Sulawesi (Selatan & Tenggara)",
    djf: -12,
    mam: -16,
    jja: -28,
    son: -25,
    primaryRisk: "Penurunan debit air sungai memicu penyesuaian jadwal tanam komoditas pangan padi sawah.",
    isSimulated: true
  },
  {
    region: "Maluku dan Papua",
    djf: +4,
    mam: -6,
    jja: -14,
    son: -12,
    primaryRisk: "Pengaruh El Niño moderat; dampak lebih banyak dikontrol oleh topografi lokal dan kolam hangat barat.",
    isSimulated: true
  }
];

// Inventaris Sumber Data & Provenance
export const dataProvenanceRecords = [
  {
    source: "NOAA Daily OISST v2.1",
    provider: "NOAA National Centers for Environmental Information (NCEI)",
    variable: "Suhu Permukaan Laut (SST) & Anomali Harian",
    resolution: "Grid reguler 0,25° (~27 km)",
    timeRange: "1981 s.d. saat ini (Harian)",
    license: "Domain Publik Global (Open Data)",
    lastFetch: "04 Nov 2026, 03:00 UTC"
  },
  {
    source: "RONI (Rolling ONI)",
    provider: "NOAA Climate Prediction Center (CPC)",
    variable: "Rata-rata bergerak 3 bulan anomali SST Niño 3.4",
    resolution: "Skalar regional (5°N–5°S, 170°W–120°W)",
    timeRange: "1950 s.d. saat ini (Bulanan)",
    license: "Domain Publik (Operasional)",
    lastFetch: "01 Nov 2026"
  },
  {
    source: "Southern Oscillation Index (SOI)",
    provider: "Bureau of Meteorology (BOM) Australia",
    variable: "Deviasi perbedaan tekanan atmosfer Tahiti dan Darwin",
    resolution: "Indeks atmosfer berskala bulanan",
    timeRange: "1876 s.d. saat ini",
    license: "Domain Publik",
    lastFetch: "02 Nov 2026"
  },
  {
    source: "Dipole Mode Index (DMI / IOD)",
    provider: "JAMSTEC / BOM Australia",
    variable: "Gradien anomali SST Samudra Hindia barat dan timur",
    resolution: "Indeks dwi-kutub mingguan & bulanan",
    timeRange: "1958 s.d. saat ini",
    license: "Domain Publik",
    lastFetch: "03 Nov 2026"
  },
  {
    source: "CHIRPS v2.0 & ERA5",
    provider: "UCSB Climate Hazards Center & ECMWF",
    variable: "Estimasi Presipitasi Satelit & Reanalisis Curah Hujan",
    resolution: "Grid 0,05° (CHIRPS) dan 0,25° (ERA5)",
    timeRange: "1981 s.d. 2026",
    license: "Open Access Ilmiah",
    lastFetch: "01 Nov 2026"
  }
];

// Glosarium Iklim Ramah Awam
export const climateGlossary = [
  {
    term: "ENSO (El Niño–Southern Oscillation)",
    short: "Siklus interaksi laut dan atmosfer di Samudra Pasifik tropis.",
    detail: "ENSO terdiri dari tiga fase: El Niño (laut menghangat, curah hujan Indonesia cenderung berkurang), La Niña (laut mendingin, curah hujan Indonesia cenderung bertambah), dan Netral (kondisi mendekati rata-rata iklim).",
    analystNote: "Kopling osilasi antara sirkulasi Walker dan gelombang Kelvin ekuatorial bawah laut."
  },
  {
    term: "RONI (Rolling ONI)",
    short: "Indeks operasional untuk memantau apakah El Niño sedang berlangsung.",
    detail: "RONI dihitung dari rata-rata bergerak 3 bulan anomali suhu di wilayah Pasifik tengah (Niño 3.4). Jika nilainya di atas +0,5 °C selama minimal 5 periode berurutan, kondisi operasional El Niño dinyatakan aktif.",
    analystNote: "RONI menggunakan periode referensi klimatologi terbaru (1991–2020) yang diperbarui setiap 5 tahun."
  },
  {
    term: "SST & Anomali SST",
    short: "Suhu permukaan laut dan seberapa jauh suhunya menyimpang dari rata-rata.",
    detail: "SST (Sea Surface Temperature) adalah suhu air laut di lapisan paling atas (0–1 meter). Anomali adalah selisih antara suhu saat ini dengan rata-rata suhu normal puluhan tahun pada tanggal yang sama.",
    analystNote: "Diukur melalui sensor inframerah satelit AVHRR dan validasi buoy Argo secara harian."
  },
  {
    term: "Marine Heatwave (MHW)",
    short: "Gelombang panas di laut ketika suhu air laut luar biasa panas beberapa hari berturut-turut.",
    detail: "Terjadi ketika suhu laut melebihi ambang batas ekstrem (persentil ke-90) minimal selama 5 hari berturut-turut. Kondisi ini dapat memicu pemutihan karang dan menekan populasi ikan.",
    analystNote: "Metodologi Hobday et al. (2016) menggunakan baseline 30 tahun; terbagi dalam kategori I (Moderat) hingga IV (Ekstrem)."
  },
  {
    term: "IOD & DMI (Indian Ocean Dipole)",
    short: "Dinamika suhu laut di Samudra Hindia yang turut mempengaruhi musim hujan Indonesia.",
    detail: "IOD Positif menyebabkan Samudra Hindia dekat Sumatra mendingin sehingga mengurangi hujan di Indonesia barat. IOD Negatif sebaliknya membawa tambahan pasokan uap air.",
    analystNote: "Dihitung dari selisih anomali SST kutub barat Samudra Hindia (50°E–70°E, 10°S–10°N) dan timur (90°E–110°E, 10°S–0°)."
  },
  {
    term: "Mengapa Prediksi Iklim Bersifat Probabilistik?",
    short: "Atmosfer dan laut adalah sistem dinamis yang tidak bisa dipastikan 100%.",
    detail: "Alih-alih menyatakan 'pasti kemarau panjang', model iklim modern menyajikan probabilitas (misalnya: 64% peluang El Niño). Ini memberi ruang bagi pengambil kebijakan untuk menghitung risiko secara jujur dan adaptif.",
    analystNote: "Ensemble multi-run memperhitungkan ketidakpastian kondisi awal dan efek Spring Predictability Barrier."
  }
];
