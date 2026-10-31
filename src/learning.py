"""BluePrint alur pembelajaran dan peramalan.

Tujuan
------
Membangun eksperimen peramalan klimatologi bulanan yang dapat direproduksi,
dimulai dari baseline sederhana, lalu dibandingkan secara adil dengan model
machine-learning. Modul ini belum melatih atau menyimpan model; docstring ini
menetapkan kontrak implementasi yang perlu diikuti berikutnya.

Produk peramalan
----------------
1. Prediksi ONI/SST-anomali Ni\u00f1o 3.4 untuk horizon bulanan yang tetap,
   misalnya 1, 3, 6, dan 12 bulan.
2. Probabilitas fase ENSO El Ni\u00f1o/netral/La Ni\u00f1a pada horizon yang sama,
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
  Resamling ONI musiman 3-bulanan harus didokumentasikan; jangan menganggap
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
