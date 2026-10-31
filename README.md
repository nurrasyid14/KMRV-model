# ENSO dan Marine Heatwave: Tentang Data dan Alur Analisis

Dokumen ini merupakan artikel eksplanasi-ekposisi tentang hubungan ENSO,
SST, indeks oseanografi-atmosfer, curah hujan, dan label marine heatwave
(MHW). Pembahasan disusun untuk menjelaskan fenomena, menunjukkan seluruh
dataset yang dipakai, menilai kualitas dan batas penggunaannya, serta
menghubungkan data dengan alur pemodelan. Ambang ENSO bukan ambang suhu untuk
MHW; keduanya memiliki definisi dan tujuan evaluasi yang berbeda.

## El Niño dan La Niña: indikator dan mekanisme

El Niño–Southern Oscillation (ENSO) adalah pola iklim terkopel laut-atmosfer
tropis Pasifik yang memiliki fase hangat (El Niño), dingin (La Niña), dan netral.
Indikator yang saling melengkapi meliputi:

- **Suhu permukaan laut (SST):** anomali hangat atau dingin di Pasifik
  ekuatorial, terutama wilayah Niño 3.4.
- **Angin pasat dan sirkulasi Walker:** angin pasat umumnya melemah saat El Niño
  dan menguat saat La Niña; perubahan ini berhubungan dengan perubahan upwelling,
  termoklin, dan distribusi panas laut.
- **Tekanan udara:** Southern Oscillation Index (SOI), yang dihitung dari
  perbedaan tekanan permukaan laut Tahiti–Darwin, umumnya negatif saat El Niño
  dan positif saat La Niña.
- **Konveksi dan hujan:** pusat hujan tropis bergeser bersama perubahan laut dan
  sirkulasi atmosfer. Di Indonesia, El Niño sering berkaitan dengan kondisi
  lebih kering dan La Niña dengan kondisi lebih basah, tetapi dampaknya tidak
  pasti untuk setiap wilayah atau kejadian; musim, Indian Ocean Dipole (IOD),
  dan variasi atmosfer lain juga berpengaruh.

Karena ENSO merupakan fenomena terkopel, SST saja menunjukkan keadaan laut,
tetapi konfirmasi fase sebaiknya mempertimbangkan indikator atmosfer dan
pernyataan pemantauan resmi. [1][2][3]

## Wilayah observasi utama

Untuk menentukan fase ENSO, wilayah rujukan utama adalah **Niño 3.4**:
5°LU–5°LS, 170°BB–120°BB (setara 190°BB–240°BB dalam bujur 0–360°).
Indeks ini mewakili SST Pasifik ekuatorial tengah-timur. NOAA juga memantau
**Relative Oceanic Niño Index (RONI)**, yaitu anomali Niño 3.4 relatif terhadap
anomali rata-rata tropis, agar pemanasan global yang lebih luas tidak terlalu
mempengaruhi indeks. Per CPC, RONI digunakan untuk pemantauan dan prediksi ENSO
operasional; ONI tetap berguna sebagai indeks historis dan pembanding. [4][5]

Untuk analisis regional proyek, [dataset/get_data.py](dataset/get_data.py)
mengunduh SST NOAA OISST harian pada grid 0,25° untuk wilayah:

| Wilayah proyek | Batas lintang | Batas bujur |
|---|---:|---:|
| Pasifik Niño 3.4 | 5°LS–5°LU | 170°BB–120°BB |
| Selat Makassar | 5°LS–2°LU | 116°BT–120°BT |
| Selat Karimata | 3°LS–2°LU | 105°BT–110°BT |
| Selatan Jawa | 12°LS–8°LS | 105°BT–115°BT |
| Maluku Utara–Papua | 3°LS–3°LU | 125°BT–140°BT |

Dengan demikian, Niño 3.4 adalah wilayah rujukan untuk **indeks ENSO**,
sedangkan wilayah Indonesia adalah domain untuk menelaah **respons lokal**.
SST regional tidak menggantikan indeks ENSO resmi. [6][7]

## Ambang El Niño dan La Niña

Untuk pemantauan operasional NOAA/CPC saat ini:

- **El Niño:** RONI rata-rata bergerak 3 bulan **lebih besar dari +0,5 °C**.
- **La Niña:** RONI rata-rata bergerak 3 bulan **lebih kecil dari −0,5 °C**.
- Dalam pencatatan episode historis CPC, ambang harus terpenuhi sekurangnya
  **lima musim 3-bulanan bertumpang tindih berturut-turut**. Ambang indeks
  merupakan salah satu ukuran; kondisi atmosfer terkait juga perlu diperiksa.

ONI menggunakan rata-rata bergerak 3 bulan anomali SST ERSST di Niño 3.4 dengan
ambang ±0,5 °C dan tetap disediakan sebagai seri historis. Jangan mencampur
RONI dan ONI seolah-olah keduanya seri yang identik: definisi/acuan datanya
berbeda. Untuk laporan yang harus konsisten dengan pemantauan terbaru,
gunakan RONI CPC; untuk reproduksi analisis historis yang secara eksplisit
memakai ONI, gunakan seri ONI dan dokumentasikan pilihan tersebut. Nilai terbaru
dapat direvisi; CPC meminta nilai real-time terbaru diperlakukan sebagai
perkiraan. [4][5]

### Ambang MHW berbeda dari ambang ENSO

Ambang ±0,5 °C di atas **mengklasifikasikan fase ENSO**, bukan menentukan
marine heatwave. Definisi MHW yang banyak digunakan mengidentifikasi periode
saat SST harian berada di atas persentil ke-90 klimatologi musiman setempat
sekurangnya lima hari berturut-turut. Karena ambangnya relatif terhadap
klimatologi lokal dan musim, MHW tidak memiliki satu ambang suhu absolut yang
berlaku untuk semua wilayah. Tetapkan baseline klimatologi, metode persentil,
dan aturan durasi secara eksplisit sebelum membuat label pelatihan. [8]

## Tentang Data

Dataset proyek dibedakan menjadi sumber mentah, data bulanan yang telah
digabungkan, dan store analisis terverifikasi. Store utama berada pada
`dataset/climate_dataset.zarr`, sedangkan berkas CSV/NetCDF mentah tetap
disimpan di folder sumbernya. Seluruh deret bulanan pada store mencakup
Januari 2015 sampai Desember 2025, tetapi panjang rentang tidak berarti
dataset memiliki mutu, resolusi, atau cakupan yang sama.

### Sumber data

1. **SST grid harian:** NOAA Daily Optimum Interpolation Sea Surface
   Temperature (OISST) v2.1, beresolusi 0,25°, digunakan sebagai variabel
   laut absolut untuk lima wilayah. Store saat ini memuat Pasifik Niño 3.4,
   Selat Makassar, dan Selat Karimata; dua wilayah Indonesia regional lainnya
   dikecualikan oleh aturan verifikasi saat ini. Sumber pengunduhan dan preprocessing:
   [6][7].
2. **ONI ENSO:** seri NOAA Climate Prediction Center (CPC), berisi SST total
   (`TOTAL`) dan anomali (`ANOM`) dalam format musiman 3-bulanan yang dipetakan
   ke tanggal tengah bulan saat preprocessing. ONI bukan hasil rerata sederhana
   dari grid regional proyek dan perlu diperlakukan sebagai indeks resmi. [4][5]
3. **SOI:** Southern Oscillation Index bulanan, menggunakan selisih tekanan
   Tahiti–Darwin sebagai sisi atmosfer ENSO. Data ini digunakan untuk
   membandingkan sinyal tekanan dengan SST dan ONI, bukan untuk
   mengklasifikasikan ENSO sendiri. [3]
4. **IOD:** Dipole Mode Index (DMI), yaitu kontras anomali SST antara Samudra
   Hindia tropis barat (50°–70°BT, 10°LS–10°LU) dan tenggara
   (90°–110°BT, 10°LS–ekuator). DMI positif menunjukkan bagian barat relatif
   lebih hangat daripada tenggara; DMI berguna sebagai konteks tambahan bagi
   hujan Indonesia, bukan pengganti indeks ENSO. Metode dan definisi awal
   dijelaskan oleh Saji et al. [9]
5. **Curah hujan Malaysia:** CSV regional dekadal yang diaggregasi menjadi
   rerata bulanan. Variabel utama meliputi keadaan curah, akumulasi/rerata,
   dan kuantil yang tersedia pada sumber; variabel administratif tidak boleh
   dianggap pengukuran cuaca. Sumber proyek adalah HDX dataset
   `mys-rainfall-subnational`. [14]
6. **Curah hujan Hawaii:** beberapa CSV stasiun harian dari Hawaii
   dikonversi ke rerata hujan harian per stasiun, lalu dirata-ratakan secara
   regional. `rain_total_mm` adalah perkalian rerata hujan harian dengan jumlah
   hari dalam bulan. Sumber data resmi yang digunakan adalah Hawaiʻi Climate
   Data Portal. [15]
7. **Label MHW:** variabel pada `data_mhw/mhw_labels` memuat indikator kejadian,
   persentil, dan SST untuk empat wilayah yang termasuk dalam store. Label MHW
   berasal dari SST dan aturan ambang lokal, sehingga tidak boleh disamakan
   dengan ambang fase ENSO ±0,5 °C. [8]

### Deskripsi dan peran setiap group Zarr

| Group | Bentuk data | Peran dalam analisis |
|---|---|---|
| `data_curah_hujan/rainfall-mys` | Deret 132 bulan, nilai numerik Malaysia | Salah satu sumber curah hujan Malaysia dalam representasi agregat regional. |
| `data_rainfall_monthly/malaysia` | Deret 132 bulan, variabel curah hujan Malaysia | Data bulanan hasil pipeline untuk eksperimen curah hujan Malaysia. |
| `data_rainfall_monthly/hawaii` | Deret 132 bulan, rata-rata dan total regional | Data pembanding curah hujan wilayah timur laut Pasifik/Hawaii. |
| `sst_5_wilayah/pasifik_nino34` | Grid lat/lon × time | SST absolut regional Pasifik tengah; menjadi dasar anomali Niño 3.4 buatan proyek. |
| `sst_5_wilayah/selat_makassar` | Grid lat/lon × time | SST lokal untuk respons laut di Indonesia tengah. |
| `sst_5_wilayah/selat_karimata` | Grid lat/lon × time | SST lokal di Selat Karimata. |
| `data_mhw/mhw_labels` | Deret 132 bulan, variabel per wilayah | Target/label dan variabel pembantu untuk empat wilayah yang masuk store. |
| `data_oni/oni` | Deret musiman 132 bulan | Indeks ENSO resmi; `ANOM` menjadi benchmark dan `TOTAL` merupakan SST referensi tekstual. |
| `data_soi/soi` | Deret bulanan indeks 132 bulan | Pembanding tekanan atmosfer terhadap respons laut dan hujan. |
| `data_dmi/dmi` | Deret bulanan indeks 132 bulan | Kontrol mode Samudra Hindia yang dapat memodulasi dampak ENSO regional. |

Kelompok `data_curah_hujan/rainfall-mys` dan kelompok
`data_rainfall_monthly/malaysia` adalah dua representasi yang berbeda, bukan
dua pengamatan independen. Kedua file harus diverifikasi sebelum dipakai
bersama agar tidak menduplikasi satu sumber, sementara `Hawaii` dapat dijaga
sebagai pembanding lintas wilayah.

### Pembatasan dan prinsip pemakaian data

Kelengkapan kalender hanya memastikan bahwa semua 132 titik bulanan ada; tidak
menjamin setiap stasiun, titik grid, atau area administratif memiliki pengamatan
lengkap pada tiap titik waktu. Nilai yang hilang pada nilai hujan, SST, indeks,
atau observasi MHW tidak boleh diganti dengan nol karena nol dapat berarti
garis dasar yang berbeda atau keadaan kering, bukan ketidakhadirannya
pengamatan. Penggunaan variabel harus mengikuti satuan asli dan luas domain
masing-masing.

Data ONI, SOI, DMI, dan produk SST memiliki skala serta prosedur asal yang
berbeda. Karena itu, korelasi antarvariabel bukan bukti hubungan sebab-akibat.
Sebelum analisis, seluruh deret perlu disejajarkan pada timestamp bulanan yang
ditetapkan proyek; sebelum pemodelan, parameter normalisasi dan baseline
klimatologi harus ditetapkan hanya dari data training. Eksperimen benchmark
harus mempertahankan split, horizon prediksi, dan evaluasi yang sama dengan
model utama agar perbandingan adil.

### Metode pengambilan saat ini

Downloader mengambil OISST dari ERDDAP, memotong setiap domain, menyimpan
NetCDF per wilayah dan tahun, lalu menggabungkannya. Tanggal duplikat
dihilangkan dan dimensi spasial tiap wilayah diberi nama tersendiri sebelum
digabung. Tahap konversi berikutnya menyimpan dataset NetCDF sebagai Zarr.

Indeks RONI/ONI, SOI, dan DMI belum ditambahkan ke downloader saat ini; ambil
seri resminya secara terpisah dan gabungkan berdasarkan tanggal/bulan. Catat
nama produk, versi, waktu unduh, satuan, kalender, rentang data, serta definisi
indeks agar hasil dapat direproduksi. OISST v2.1 juga memiliki pembaruan
produksi; simpan metadata versi bila tersedia. [6]

### Pra-pemrosesan yang disarankan

1. Periksa satuan, koordinat, urutan lintang/bujur, kalender, nilai hilang, dan
   duplikasi waktu. Jangan mengubah nilai hilang menjadi suhu nol; nol bukan
   nilai pengganti yang bermakna untuk SST.
2. Untuk indeks ENSO, gunakan seri resmi CPC. Untuk analisis grid/regional,
   hitung anomali terhadap klimatologi yang didefinisikan dan konsisten, lalu
   pertahankan baik SST maupun anomali bila keduanya diperlukan.
3. Bila merata-ratakan grid, gunakan pembobotan luas (misalnya bobot
   proporsional terhadap cosinus lintang) dan dokumentasikan penanganan
   daratan/nilai hilang.
4. Untuk label MHW, hitung klimatologi dan persentil harian per lokasi serta
   musiman sesuai definisi yang dipilih; terapkan syarat durasi minimal secara
   eksplisit. Jangan menggunakan ambang ENSO sebagai label MHW.
5. Bagi data latih, validasi, dan uji secara kronologis. Hitung parameter
   normalisasi hanya dari data latih untuk menghindari kebocoran informasi masa
   depan.
6. Simpan array multidimensi di Zarr; gunakan PostgreSQL untuk metadata, indeks,
   dan hasil analisis/prediksi yang perlu dikueri.

### Inventaris dataset Zarr

`dataset/climate_dataset.zarr` telah diverifikasi dengan
`python src/verify_zarr.py`. Semua group berikut mencakup Januari 2015 sampai
Desember 2025 dan tidak memiliki bulan yang hilang.

| Group | Dimensi | Variabel data | Bulan |
|---|---|---|---:|
| `data_curah_hujan/rainfall-mys` | `time: 132` | `adm_id`, `adm_level`, `n_pixels`, `r1h`, `r1h_avg`, `r1q`, `r3h`, `r3h_avg`, `r3q`, `rfh`, `rfh_avg`, `rfq` | 132 |
| `data_dmi/dmi` | `time: 132` | `DMI` | 132 |
| `data_mhw/mhw_labels` | `time: 132` | `Maluku_Utara_Papua_is_mhw`, `Maluku_Utara_Papua_p90`, `Maluku_Utara_Papua_sst`, `Pasifik_Nino34_is_mhw`, `Pasifik_Nino34_p90`, `Pasifik_Nino34_sst`, `Selat_Karimata_is_mhw`, `Selat_Karimata_p90`, `Selat_Karimata_sst`, `Selat_Makassar_is_mhw`, `Selat_Makassar_p90`, `Selat_Makassar_sst`, `Selatan_Jawa_is_mhw`, `Selatan_Jawa_p90`, `Selatan_Jawa_sst` | 132 |
| `data_oni/oni` | `time: 132` | `ANOM`, `TOTAL` | 132 |
| `data_rainfall_monthly/hawaii` | `time: 132` | `n_stations`, `rain_mean_daily_mm`, `rain_total_mm` | 132 |
| `data_rainfall_monthly/malaysia` | `time: 132` | `n_obs`, `n_pixels`, `r1h`, `r1h_avg`, `r1q`, `r3h`, `r3h_avg`, `r3q`, `rfh`, `rfh_avg`, `rfq` | 132 |
| `data_soi/soi` | `time: 132` | `SOI` | 132 |
| `sst_5_wilayah/pasifik_nino34` | `lat: 41`, `lon: 201`, `time: 132`, `zlev: 1` | `sst` | 132 |
| `sst_5_wilayah/selat_karimata` | `lat: 21`, `lon: 21`, `time: 132`, `zlev: 1` | `sst` | 132 |
| `sst_5_wilayah/selat_makassar` | `lat: 29`, `lon: 17`, `time: 132`, `zlev: 1` | `sst` | 132 |

#### Kelengkapan parameter dan perlakuan anomali

Parameter utama untuk eksperimen sudah tersedia pada store:

| Parameter | Sumber Zarr | Status | Catatan penggunaan |
|---|---|---|---|
| Curah hujan Malaysia | `data_rainfall_monthly/malaysia` | Tersedia | Gunakan variabel hujan observasi utama; kolom wilayah/metadata tidak boleh diperlakukan sebagai deret hujan. |
| Curah hujan Hawaii | `data_rainfall_monthly/hawaii` | Tersedia | Gunakan `rain_mean_daily_mm` atau `rain_total_mm` sesuai target bulanan. |
| SST Pasifik tengah | `sst_5_wilayah/pasifik_nino34` | Tersedia | Variabel `sst` masih SST absolut. Kurangi baseline klimatologi yang ditetapkan secara terpisah sebelum membuat anomali SST. |
| ONI | `data_oni/oni` | Tersedia | `ANOM` adalah anomali ONI; `TOTAL` adalah SST total. Gunakan `ANOM` untuk pembanding ENSO dan jangan menyamakannya dengan SST Pasifik. |
| SOI | `data_soi/soi` | Tersedia | Indeks osilasi tekanan; tanda positif/negatif ditafsirkan bersama ONI karena SOI dan ONI dapat tidak sinkron. |
| DMI | `data_dmi/dmi` | Tersedia | Indeks gradien SST Samudra Hindia dan pembanding tambahan, bukan pengganti ENSO. |

Anomali harus memiliki acuan dan rentang baseline yang terdokumentasi. Untuk
model ini, baseline rekomendasinya adalah klimatologi yang diperbarui dari
periode referensi tetap, misalnya 1991–2020 bila data lengkap. Jangan menghitung
SST anomaly, normalisasi, atau climatology dari keseluruhan data uji lalu
memasukkannya kembali ke training. Di bawah ini, **anomali SST dan ONI berfungsi
sebagai benchmark pembanding**, bukan hasil yang otomatis dianggap model baru:

| Benchmark | Aturan prediksi | Pemetaan keluaran |
|---|---|---|
| Persistence | Nilai SST/anomali indeks bulan saat ini dianggap bertahan pada horizon target. | Baseline pertama untuk ONI, DMI, SOI, dan SST. |
| Climatologi bulanan | Gunakan nilai rerata bulanan dari periode training saja pada bulan kalender yang sama. | Baseline untuk SST dan hujan tanpa momentum ENSO. |
| ONI persistence | Pertahankan `ANOM` terakhir pada horizon prediksi yang diuji. | Pembanding khusus fase ENSO. |

Seluruh benchmark dan model dievaluasi pada split kronologis yang sama dengan
horizon dan wilayah yang sama. Pembanding utama harus dilaporkan sebelum,
bersamaan dengan, dan sesudah implementasi model agar klaim peningkatan tidak
berasal dari definisi evaluasi yang berbeda.

## Workflow prosedural: dari data ke keluaran

Jangan memperlakukan semua keluaran sebagai satu target model. Proyek ini
memiliki tiga pertanyaan berbeda: **(A)** probabilitas fase ENSO mendatang,
**(B)** perubahan SST dan kejadian panas laut, dan **(C)** respons cuaca/iklim
di Indonesia. Prediksi ENSO untuk beberapa musim ke depan adalah sasaran
musiman-probabilistik; siklus ENSO yang rata-rata berulang tiap beberapa tahun
tidak berarti tahun atau fase berikutnya dapat diprediksi seperti jadwal.
Gunakan prakiraan ensemble operasional sebagai pembanding dan jangan
menjanjikan prediksi deterministik beberapa tahun ke depan. IRI mempublikasikan
plume ensemble bulanan dengan model dinamis dan statistik serta probabilitas
fase yang bergantung pada lead time dan musim. [2][10]

| Blok | Masukan | Prosedur | Keluaran/status |
|---|---|---|---|
| 0. Definisikan produk prediksi | Kebutuhan analis/pengguna | Tetapkan target, wilayah, musim, lead time, satuan, ambang keputusan, dan tanggal penerbitan. Pisahkan A (fase RONI), B (SST/anomali/MHW), dan C (hujan/suhu/dampak Indonesia). | Spesifikasi target; belum ada keputusan horizon multi-tahun. |
| 1. Ambil data laut Pasifik | SST historis dan terkini, indeks resmi | Untuk prediksi ENSO, arsipkan domain tropis Pasifik yang cukup lebar untuk menangkap evolusi pola, bukan hanya kotak Niño 3.4. Sertakan Niño 3.4/RONI resmi, SOI, dan bila tersedia angin serta suhu laut bawah permukaan/heat content. Produk operasional/ensemble IRI menjadi acuan prakiraan, bukan diganti oleh rekonstruksi sendiri. | Arsip laut dan indeks dengan provenance/versi. |
| 2. Ambil data dampak Indonesia | Hujan, suhu udara, angin, kelembapan dan kalender musim | Prioritaskan data stasiun BMKG untuk validasi lokal; lengkapi dengan grid CHIRPS v3 untuk hujan daratan dan ERA5 untuk variabel atmosfer/reanalisis. Simpan mask darat/laut. CHIRPS v3 adalah estimasi hujan gridded; jangan samakan dengan pengamatan stasiun atau menganggapnya pengamatan laut. | Arsip tiap parameter dengan resolusi, cakupan, dan kualitas tercatat. |
| 3. Simpan sumber mentah | Unduhan asli (NetCDF/CSV/gridded) | Simpan tanpa perubahan, bersama metadata produk, URL, waktu unduh, versi, lisensi, satuan, kalender, dan checksum. Gunakan Zarr untuk array multidimensi yang akan dibaca per wilayah/waktu; simpan tabel ringkas/indeks sumber di PostgreSQL. | Data mentah yang dapat diulang dan ditelusuri. |
| 4. QC dan penyelarasan | Arsip multi-sumber | Verifikasi unit, kalender, timestamp, grid, koordinat, nilai hilang, duplikasi, perubahan versi, dan cakupan. Samakan kalender/resolusi hanya setelah mencatat metode; agregasikan daily ke monthly/seasonal sesuai definisi indeks atau target. Jangan mengisi SST hilang dengan nol. | Dataset analisis selaras dan laporan QC. |
| 5. Bentuk fitur dan label | SST, indeks, atmosfer, observasi Indonesia | Bentuk anomali terhadap baseline yang tetap dan didokumentasikan; sertakan siklus musiman. Buat target ENSO dari seri resmi RONI/ONI dan fase; buat target dampak per wilayah/musim (misalnya anomali hujan atau peluang hujan di bawah persentil); hitung label MHW secara terpisah dari ambang ENSO. Fitur dapat mencakup lag RONI/SST, SOI, DMI, monsun, angin, dan panas bawah permukaan. | Tabel fitur/label berversi; definisi label tetap. |
| 6. Bentuk eksperimen hindcast | Fitur/target historis | Untuk setiap tanggal awal prakiraan, gunakan hanya data yang memang tersedia pada tanggal itu. Lakukan rolling-origin/forward-chaining secara kronologis; simpan banyak periode uji dan evaluasi per musim, lead time, dan wilayah. Jangan random-split baris deret waktu atau memakai klimatologi yang dihitung dari masa depan. | Prakiraan historis yang mereplikasi penggunaan operasional. |
| 7. Latih dan kalibrasi | Train/validation hindcast | Mulai dari baseline klimatologi dan persistence, lalu bandingkan regresi/CCA atau model probabilistik dengan prakiraan ensemble dinamika/statistika resmi. Model ML tabular (regularized regression, gradient boosting) adalah pembanding tambahan; gunakan LSTM/ConvLSTM hanya jika cakupan historis, variabel, dan jumlah hindcast memadai. Pilih model berdasarkan skill di luar sampel, bukan kecocokan train. Kalibrasikan probabilitas fase. | Model terpilih per target/lead dan kartu evaluasi. |
| 8. Terbitkan dan pantau | Model tervalidasi, input terbaru | Terbitkan probabilitas El Niño/netral/La Niña untuk lead yang telah tervalidasi, prakiraan/anomali SST per wilayah, serta probabilitas dampak musiman Indonesia. Sertakan ketidakpastian, tanggal data, lead time, kualitas, dan peringatan saat input berubah. Pantau drift dan skor saat observasi baru tiba. | Produk prakiraan dapat ditafsirkan; bukan jaminan cuaca harian. |
| 9. Simpan dan sajikan | Metadata, indeks, skor, prediksi | Simpan array besar di Zarr/object storage. Simpan run, versi model, waktu penerbitan, wilayah, lead, probabilitas, metrik, dan referensi Zarr di PostgreSQL; jangan masukkan seluruh tensor grid ke tabel relasional. | Audit trail, analitik, dan akses anggota tim. |

### Rekomendasi metode menurut pertanyaan

#### A. Apakah El Niño atau La Niña akan terjadi?

- **Gunakan target kontinu dahulu:** prediksi RONI/Niño 3.4 untuk beberapa lead
  bulanan yang realistis, lalu konversi prakiraan kontinu/ensemble menjadi
  probabilitas tiga kelas sesuai definisi fase. Jangan melatih klasifikasi dari
  label tahunan yang kasar jika seri indeks bulanan tersedia.
- **Pembanding wajib:** klimatologi musiman, persistence (indeks terkini
  bertahan), serta plume/probabilitas ensemble dari IRI dan produk operasional
  resmi. Periksa apakah model tambahan memberi skill di atas pembanding ini.
  IRI menggabungkan model dinamis dan statistik serta menyesuaikan sebaran
  probabilitas dengan skill menurut musim dan lead. [10]
- **Model buatan sendiri:** regresi regularized/CCA atau model autoregresif
  multivariat sebagai baseline; setelah itu coba gradient boosting untuk fitur
  lag terstruktur. Model deep learning spasio-temporal (CNN/LSTM) hanya sebagai
  eksperimen lanjutan dengan hindcast panjang dan evaluasi ketat.
- **Masukan fisik yang disarankan:** SST/indeks Niño lintas wilayah ekuatorial,
  RONI/ONI resmi, SOI/tekanan, angin pasat, dan suhu/heat content bawah
  permukaan. SST permukaan Pasifik yang luas saja lebih baik dari kotak tunggal,
  tetapi tetap tidak menggantikan state laut-atmosfer yang terkopel.
- **Batas horizon:** mulai dengan prakiraan beberapa musim sampai sekitar satu
  tahun dan laporkan skill per lead. Untuk “tahun-tahun mendatang”, berikan
  skenario/probabilitas dengan ketidakpastian besar atau gunakan outlook
  multi-model resmi; jangan klaim kepastian fase ENSO beberapa tahun di muka.

#### B. Perubahan suhu laut dan kejadian panas laut

- Hitung klimatologi/anomali SST per grid dan musim; agregasikan wilayah dengan
  pembobotan luas. Tampilkan deret waktu, peta anomali, tren, distribusi
  persentil, serta perbandingan antarwilayah.
- Untuk tren historis, gunakan regresi tren dan estimator robust seperti
  Theil–Sen; laporkan ketidakpastian dan autokorelasi, jangan simpulkan tren
  iklim dari hubungan satu kejadian ENSO saja.
- Untuk MHW, gunakan ambang persentil harian lokal dan aturan durasi definisi
  Hobday, kemudian ukur frekuensi, durasi, intensitas maksimum/rata-rata, serta
  luas spasial. MHW adalah target peristiwa laut yang berbeda dari prediksi
  kategori ENSO.
- Model prediksi: mulai dari baseline musiman/persistence dan regresi per
  lead; gradient boosting dapat diuji untuk fitur tabular. Model grid
  convolutional/spatio-temporal memerlukan arsip luas dan hindcast yang cukup.

#### C. Respons hujan/cuaca di Indonesia

- Targetkan **anomali atau probabilitas per wilayah dan musim**, bukan klaim
  “El Niño selalu menyebabkan kekeringan”. Analisis terpisah DJF/MAM/JJA/SON
  atau kalender musim lokal dan wilayah; hubungan ENSO–hujan berbeda secara
  spasial, musiman, dan antar-kejadian.
- Mulai dengan komposit dan regresi/GAM yang menjelaskan hujan terhadap RONI,
  DMI, musim/monsoon, serta interaksi ENSO×IOD. Gunakan model campuran atau
  efek wilayah bila menggabungkan beberapa stasiun; gunakan quantile regression
  atau quantile forest untuk risiko ekor kering/basah.
- Bandingkan dengan prakiraan musiman operasional dan validasi menggunakan
  stasiun BMKG yang tidak dipakai sebagai input. CHIRPS v3 memberi data hujan
  daratan gridded 0,05° sejak 1981 hingga mendekati kini; ERA5 memberi variabel
  atmosfer global berbasis asimilasi. Keduanya adalah produk analisis, bukan
  pengganti observasi lokal. [11][12]
- Terbitkan peta probabilitas/anomali dan rentang ketidakpastian per kabupaten
  atau wilayah laut yang didukung data. Untuk respons operasional (misalnya
  pertanian, kebakaran, banjir), kolaborasikan validasi dengan pengguna dan
  sumber lokal BMKG.

### Metrik evaluasi minimum

| Produk | Metrik yang disarankan | Pemeriksaan penting |
|---|---|---|
| RONI/Niño 3.4 kontinu | MAE, RMSE, korelasi anomali | Skor per lead dan musim; bandingkan persistence/climatology. |
| Fase ENSO probabilistik | Brier score, log loss, reliability/calibration, confusion matrix | Jangan hanya melaporkan accuracy; kelas dapat tidak seimbang. |
| SST/anomali per grid | MAE/RMSE, bias, anomaly correlation | Laporkan per wilayah dan musim; periksa peta bias. |
| Hujan/dampak probabilistik | Brier score dan reliability untuk ambang; MAE untuk anomali | Evaluasi per musim/wilayah dan terhadap stasiun independen. |
| MHW | Precision/recall/F1 dan galat durasi/intensitas | Cocokkan definisi episode dan baseline klimatologi. |

Semua metrik harus dihitung dari hindcast yang kronologis dan tidak bocor.
Laporkan interval ketidakpastian atau bootstrap menurut tahun/episode; sampel
hari yang saling bertumpang tindih bukan sampel independen.

### Prioritas implementasi proyek

1. **Sekarang:** perpanjang arsip OISST melampaui 2015–2025 dan tambahkan
   seri RONI/ONI, SOI, DMI, hujan, serta data stasiun/ERA5. Rentang 11 tahun
   saat ini terlalu pendek untuk membangun dan menguji prakiraan ENSO yang
   andal atau baseline klimatologi multi-dekadal.
2. **Berikutnya:** buat alur QC, anomali dan label berversi; simpan NetCDF/Zarr
   mentah/terproses dan metadata sumber.
3. **Lalu:** buat eksperimen hindcast rolling-origin dan ukur baseline
   persistence/climatology serta skill plume IRI sebelum memilih model ML.
4. **Baru setelah skill terukur:** tambahkan model probabilistik, kalibrasi,
   analisis dampak regional, dan antarmuka penyajian.

Kode saat ini sudah mencakup pengunduhan SST OISST regional, konversi NetCDF
ke Zarr, ringkasan EDA, beberapa utilitas preprocessing, dan rancangan
penyimpanan PostgreSQL. Pengunduhan indeks iklim/hujan, training, hindcast,
kalibrasi, dan prediksi dampak Indonesia **belum diimplementasikan**. [13]

## Interpretasi

| Sinyal | Interpretasi umum | Batas interpretasi |
|---|---|---|
| RONI > +0,5 °C | Sinyal fase hangat / El Niño menurut ambang indeks | Periksa persistensi episode dan sinyal atmosfer; bukan jaminan dampak lokal. |
| RONI < −0,5 °C | Sinyal fase dingin / La Niña menurut ambang indeks | Periksa persistensi episode dan sinyal atmosfer; bukan jaminan dampak lokal. |
| SOI negatif | Mendukung pola atmosfer El Niño | Baca bersama SST dan definisi seri SOI yang dipakai. |
| SOI positif | Mendukung pola atmosfer La Niña | Baca bersama SST dan definisi seri SOI yang dipakai. |
| DMI positif/negatif | Menunjukkan gradien SST timur-barat IOD | IOD adalah variasi Samudra Hindia yang dapat memodulasi kondisi regional; bukan klasifikasi ENSO. |
| SST lokal di atas persentil ke-90 ≥5 hari | Kandidat MHW berdasarkan definisi Hobday yang umum digunakan | Harus dihitung terhadap klimatologi lokal dan metode baseline yang dinyatakan. |

Nilai RONI/ONI, SOI, dan DMI adalah **indikator iklim**, bukan prediksi langsung
SST atau dampak di suatu sel grid. Interpretasikan keluaran model per wilayah
dengan metrik ketidakpastian dan validasi historis; korelasi dengan ENSO tidak
membuktikan bahwa ENSO adalah satu-satunya penyebab anomali lokal.

## Akses database dari anggota kelompok di Wi-Fi/LAN yang sama

Docker Compose menerbitkan PostgreSQL pada port yang ditetapkan di `.env`.
Salin `.env.example` menjadi `.env` dan isi kata sandi unik yang kuat. File
`.env` diabaikan Git; jangan kirim atau commit file tersebut.

- Jalankan database di komputer host dengan `docker compose up -d postgres-db`.
- Anggota kelompok harus memakai **alamat IPv4 LAN komputer host**, bukan
  `localhost`. Contoh format URL:
  `postgresql+psycopg2://mhw_member:<password>@<IP-LAN-host>:5432/mhw_db`.
- Izinkan koneksi masuk TCP pada port yang dikonfigurasi hanya untuk profil
  jaringan **Private** dan subnet Wi-Fi/LAN kelompok melalui Windows Firewall.
  Jangan membuat port-forwarding router atau membuka port PostgreSQL ke
  internet publik.
- Komputer host, Docker, dan container database harus tetap berjalan; alamat IP
  host perlu tetap diketahui (gunakan DHCP reservation bila tersedia).
- Beberapa Wi-Fi mengaktifkan client/AP isolation. Dalam kondisi itu, perangkat
  satu Wi-Fi pun tidak dapat saling menjangkau; ubah pengaturan jaringan atau
  gunakan VPN tepercaya. Untuk anggota di luar LAN, gunakan VPN, bukan port
  PostgreSQL publik.

URL `DATABASE_URL` pada `.env` lokal memakai `localhost` agar kode Python pada
komputer host terhubung. Backend yang berjalan di Docker Compose menggunakan
nama layanan `postgres-db` secara internal. `init.sql` membuat akun
`DB_MEMBER_USER` terpisah yang dapat membaca, menambah, dan memperbarui data,
tetapi tidak dapat menghapus tabel atau mengubah skema. Bagikan hanya kredensial
akun anggota melalui saluran tepercaya; jangan bagikan `POSTGRES_USER` atau
`POSTGRES_PASSWORD` (akun administrator/bootstrap).

Catatan: skrip dalam `init.sql` dijalankan otomatis hanya saat volume database
pertama kali dibuat. Jika volume `postgres_data` sudah pernah diinisialisasi,
menambah variabel atau mengubah `.env` tidak otomatis membuat akun atau
mengubah kata sandi di dalam database; lakukan migrasi/rotasi kredensial
terencana dan jangan menghapus volume yang berisi data.

## Daftar Pustaka

1. NOAA Climate.gov, [ENSO](https://www.climate.gov/enso).
2. NOAA Physical Sciences Laboratory, [ENSO basics and impacts](https://www.psl.noaa.gov/enso/).
3. NOAA CPC, [Southern Oscillation Index data](https://www.cpc.ncep.noaa.gov/data/indices/soi).
4. NOAA CPC, [Relative Oceanic Niño Index (RONI)](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/).
5. NOAA CPC, [Oceanic Niño Index (ONI), ERSSTv6](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/) and [historical ONI series](https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt).
6. NOAA NCEI, [Daily Optimum Interpolation Sea Surface Temperature (OISST)](https://www.ncei.noaa.gov/products/optimum-interpolation-sst).
7. NOAA CoastWatch ERDDAP, [OISST v2.1 gridded dataset](https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.html).
8. Hobday, A. J. et al. (2016), [A hierarchical approach to defining marine heatwaves](https://doi.org/10.1016/j.pocean.2015.12.014), *Progress in Oceanography*.
9. Saji, N. H. et al. (1999), [A dipole mode in the tropical Indian Ocean](https://doi.org/10.1038/43854), *Nature*.
10. Columbia Climate School / IRI, [ENSO prediction plume, model outlook, and forecast probabilities](https://iri.columbia.edu/our-expertise/climate/forecasts/enso/current/).
11. Climate Hazards Center, [CHIRPS v3 data and documentation](https://www.chc.ucsb.edu/data/chirps3).
12. Copernicus Climate Data Store, [ERA5 hourly data on single levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels).
13. [NOAA CoastWatch ERDDAP OISST dataset used by the current downloader](https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.html).
14. Humanitarian Data Exchange, [Malaysia rainfall — subnational dataset](https://data.humdata.org/dataset/mys-rainfall-subnational).
15. University of Hawaiʻi, [Hawaiʻi Climate Data Portal](https://www.hawaii.edu/climate-data-portal/data-portal/).

Sumber web diakses 31 Oktober 2026.
