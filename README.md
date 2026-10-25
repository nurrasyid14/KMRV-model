# ENSO, data, dan alur analisis

Dokumen ini merangkum indikator El Niño–La Niña, data yang relevan untuk
proyek, dan batas interpretasinya. Ambang ENSO di bawah adalah definisi
operasional iklim, bukan ambang prediksi atau diagnosis gelombang panas laut
(marine heatwave/MHW).

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

## Data yang diperlukan

### Sumber data

1. **SST harian dan anomali grid:** NOAA Daily Optimum Interpolation Sea Surface
   Temperature (OISST) v2.1, produk gabungan harian beresolusi 0,25°. Proyek
   saat ini meminta variabel `sst` melalui NOAA CoastWatch ERDDAP. [6][7]
2. **Indeks ENSO:** seri dan penjelasan RONI/ONI dari NOAA Climate Prediction
   Center (CPC). Unduh seri indeks yang dipilih dari sumber resmi; jangan
   mengasumsikan rata-rata sederhana dari kotak regional identik dengan RONI
   atau ONI CPC. [4][5]
3. **SOI:** nilai bulanan dari CPC untuk menguji konsistensi atmosfer dengan
   sinyal laut Niño 3.4. [3]
4. **IOD:** Dipole Mode Index (DMI), yaitu kontras anomali SST antara Samudra
   Hindia tropis barat (50°–70°BT, 10°LS–10°LU) dan tenggara
   (90°–110°BT, 10°LS–ekuator). DMI positif menunjukkan bagian barat relatif
   lebih hangat daripada tenggara; DMI berguna sebagai konteks tambahan bagi
   hujan Indonesia, bukan pengganti indeks ENSO. Metode dan definisi awal
   dijelaskan oleh Saji et al. [9]
5. **Label MHW:** dihitung dari SST harian dan baseline klimatologi menggunakan
   definisi MHW yang dipilih (misalnya Hobday et al.); label ini belum dibuat
   oleh tahap pengunduhan saat ini. [8]

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

## Referensi

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

Sumber web diakses 25 Oktober 2026.
