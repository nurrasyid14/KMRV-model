# Menggunakan official TensorFlow image dengan dukungan CPU (gunakan tag -gpu jika menggunakan GPU NVIDIA)
FROM tensorflow/tensorflow:2.12.0-py3

# Menetapkan working directory di dalam container
WORKDIR /app

# Menyalin requirements.txt jika ada
COPY requirements.txt .

# Menginstal dependensi tambahan jika diperlukan
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode aplikasi dan model ke dalam container
COPY . /app

# Menjalankan aplikasi Python saat container dimulai
CMD ["python", "app.py"]