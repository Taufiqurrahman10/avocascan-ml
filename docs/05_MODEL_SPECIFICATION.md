# MODEL_SPECIFICATION.md

# AI Model Specification

## Purpose

Dokumen ini menjelaskan spesifikasi model machine learning yang digunakan pada AI Service AvocaScan.

Seluruh implementasi inferensi harus mengikuti spesifikasi pada dokumen ini.

---

# Overview

Sistem menggunakan dua model yang dijalankan secara berurutan.

Model pertama melakukan validasi objek.

Model kedua melakukan klasifikasi tingkat kematangan.

Seluruh pipeline dikendalikan oleh AI Service.

---

# Stage 1 Model

## Purpose

Menentukan apakah objek pada gambar merupakan buah alpukat.

Stage 1 berfungsi sebagai penyaring (gatekeeper) sebelum menjalankan proses klasifikasi kematangan.

---

## Input

Input berupa satu gambar RGB.

Ukuran gambar harus mengikuti ukuran yang digunakan saat proses pelatihan model.

Proses preprocessing harus identik dengan preprocessing saat training.

---

## Output

Model menghasilkan dua kelas:

* alpukat
* non_alpukat

Selain label prediksi, model juga menghasilkan nilai confidence.

---

## Decision Rule

Apabila hasil prediksi adalah:

```text
non_alpukat
```

maka:

* pipeline dihentikan
* Stage 2 tidak dijalankan
* feature extraction tidak dijalankan

AI Service langsung mengembalikan response kepada Laravel.

---

Apabila hasil prediksi adalah:

```text
alpukat
```

pipeline dilanjutkan menuju Stage 2.

---

# Stage 2 Model

## Purpose

Menentukan tingkat kematangan buah alpukat.

Stage 2 hanya menerima gambar yang telah dipastikan sebagai alpukat oleh Stage 1.

---

## Input

Stage 2 menerima:

* citra hasil preprocessing
* fitur HSV
* fitur GLCM

Seluruh input harus diproses menggunakan pipeline yang sama dengan proses training.

---

## Output

Model menghasilkan tiga kelas:

* mentah
* matang
* busuk

Selain label prediksi, model juga menghasilkan nilai confidence.

---

# Hybrid Model Architecture

Stage 2 menggunakan model hybrid.

Model menggabungkan dua sumber informasi.

## Visual Features

Diperoleh dari citra yang telah diproses menggunakan backbone MobileNetV3.

---

## Manual Features

Manual features diperoleh melalui proses:

* HSV Feature Extraction
* GLCM Feature Extraction

Feature tersebut digabungkan dengan visual feature sebelum proses klasifikasi.

---

# Feature Extraction

## HSV

Digunakan untuk memperoleh karakteristik warna kulit buah.

Implementasi harus identik dengan proses training.

---

## GLCM

Digunakan untuk memperoleh karakteristik tekstur permukaan buah.

Implementasi harus identik dengan proses training.

---

# Preprocessing Consistency

Seluruh tahapan preprocessing harus identik dengan proses pelatihan.

Tidak diperbolehkan mengubah:

* ukuran citra
* normalisasi
* urutan preprocessing

tanpa melatih ulang model.

Catatan: Stage 1 dan Stage 2 menggunakan preprocessing yang berbeda, sehingga implementasi harus dipisahkan dan tidak menggunakan satu pipeline preprocessing untuk kedua model.

---

# Model Loading

AI Service menggunakan dua model.

Model harus dimuat satu kali ketika aplikasi FastAPI dijalankan.

Model tidak boleh dimuat ulang pada setiap request.

---

# Inference Sequence

Urutan inferensi adalah sebagai berikut.

```text
Receive Image

↓

Validation

↓

Preprocessing

↓

Stage 1

↓

Apakah Alpukat?

├── Tidak
│
└── Return Response

↓

Ya

↓

HSV

↓

GLCM

↓

Stage 2

↓

Prediction

↓

JSON Response
```

---

# Confidence Score

Setiap model menghasilkan nilai confidence.

Confidence harus dikembalikan bersama label prediksi.

---

# Model Files

Model Stage 1 dan Stage 2 disimpan secara terpisah.

Contoh struktur:

```text
models/

stage1/
    best_model.pth
    class_names.json
    metadata.json

stage2/
    best_model.pth
    class_names.json
    metadata.json
```

---

# Metadata

Setiap model sebaiknya memiliki metadata.

Contoh informasi:

* nama model
* versi
* tanggal pelatihan
* jumlah kelas
* nama kelas
* ukuran input
* framework
* versi PyTorch

Metadata digunakan untuk dokumentasi dan debugging.

---

# Prediction Rules

Stage 2 hanya boleh dijalankan apabila:

Stage 1 == alpukat

Selain kondisi tersebut, AI Service wajib menghentikan pipeline.

---

# Design Principles

Model harus diperlakukan sebagai komponen independen.

Perubahan pada:

* Stage 1

tidak boleh memerlukan perubahan besar pada Stage 2.

Demikian pula sebaliknya.

---

# Future Compatibility

Arsitektur harus memungkinkan:

* penggantian model Stage 1
* penggantian model Stage 2
* pembaruan bobot model
* penambahan kelas
* peningkatan metode feature extraction

tanpa mengubah kontrak API.

---

# Important Notes

Seluruh implementasi inferensi harus menggunakan:

* model final
* preprocessing final
* parameter final
* feature extraction final

AI Service tidak diperbolehkan menggunakan parameter yang berbeda dari proses pelatihan model.

Apabila model dilatih ulang dengan parameter baru, dokumen ini harus diperbarui agar tetap sesuai dengan implementasi.
