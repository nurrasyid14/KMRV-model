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

Sumber web diakses 25 Oktober 2026.
