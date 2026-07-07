# CODING_GUIDELINES.md

# AI Service Coding Guidelines

## Purpose

Dokumen ini mendefinisikan standar implementasi kode untuk AI Service AvocaScan.

Seluruh kode yang dibuat harus mengikuti pedoman pada dokumen ini agar tetap konsisten, mudah dipelihara, dan mudah dikembangkan.

---

# General Principles

Seluruh implementasi harus mengikuti prinsip berikut:

* Clean Code
* SOLID Principles
* Separation of Concerns
* Single Responsibility Principle
* DRY (Don't Repeat Yourself)
* KISS (Keep It Simple, Stupid)

Business logic tidak boleh dicampurkan dengan layer API.

---

# Python Version

Gunakan Python versi terbaru yang stabil dan kompatibel dengan dependency proyek.

Versi Python harus konsisten antara lingkungan pengembangan dan deployment.

---

# Framework

Gunakan:

* FastAPI
* Pydantic v2
* Uvicorn

Gunakan API yang masih didukung dan hindari penggunaan fitur yang telah deprecated.

---

# Project Structure

Seluruh implementasi harus mengikuti struktur direktori yang telah ditetapkan pada PROJECT_STRUCTURE.md.

Tidak diperbolehkan membuat struktur baru tanpa alasan yang jelas.

---

# Naming Convention

## File

Gunakan snake_case.

Contoh:

```text id="4o4qgo"
prediction_service.py
model_loader.py
image_preprocessing.py
```

---

## Variable

Gunakan snake_case.

Contoh:

```text id="tk9t0i"
image_tensor
prediction_result
confidence_score
```

---

## Class

Gunakan PascalCase.

Contoh:

```text id="hnjk09"
PredictionService
ModelLoader
```

---

## Function

Gunakan snake_case.

Contoh:

```text id="k1lwzu"
load_model()
predict_stage1()
extract_glcm()
```

---

# Type Hint

Seluruh function wajib menggunakan type hint.

Contoh:

```text id="onq7z9"
def predict(image: Image) -> PredictionResult
```

---

# Documentation

Setiap class dan function publik harus memiliki docstring.

Docstring menjelaskan:

* tujuan
* parameter
* nilai kembali
* exception yang mungkin terjadi

---

# Router Rules

Router hanya bertugas:

* menerima request
* validasi input
* memanggil service
* mengembalikan response

Router tidak boleh:

* memuat model
* menjalankan inferensi
* melakukan preprocessing
* melakukan feature extraction

---

# Service Rules

Business logic berada pada layer service.

Service bertanggung jawab untuk:

* mengatur pipeline inferensi
* memanggil preprocessing
* memanggil feature extraction
* memanggil Stage 1
* memanggil Stage 2
* menyusun hasil prediksi

---

# Model Rules

Model hanya boleh dimuat sekali ketika aplikasi dijalankan.

Model tidak boleh dimuat ulang pada setiap request.

Seluruh model dikelola oleh Model Loader.

---

# Preprocessing Rules

Seluruh preprocessing harus identik dengan preprocessing saat training.

Parameter preprocessing tidak boleh diubah tanpa memperbarui model.

Catatan: Stage 1 dan Stage 2 menggunakan preprocessing yang berbeda, sehingga implementasi harus dipisahkan dan tidak menggunakan satu pipeline preprocessing untuk kedua model.

---

# Feature Extraction Rules

Setiap metode ekstraksi fitur ditempatkan pada modul terpisah.

Contoh:

* hsv.py
* glcm.py

Masing-masing modul hanya bertanggung jawab terhadap satu algoritma.

---

# Configuration

Seluruh konfigurasi berasal dari environment variable.

Contoh konfigurasi:

* model path
* token
* timeout
* maksimum ukuran file
* mode aplikasi

Tidak diperbolehkan menggunakan nilai hardcoded untuk konfigurasi yang dapat berubah.

---

# Logging

Gunakan modul logging Python.

Log minimal mencakup:

* startup aplikasi
* model berhasil dimuat
* request masuk
* hasil Stage 1
* hasil Stage 2
* durasi inferensi
* error

Log tidak boleh menyimpan gambar pengguna maupun informasi sensitif.

---

# Error Handling

Gunakan custom exception.

Seluruh exception harus menghasilkan response JSON yang konsisten.

Jangan menampilkan stack trace kepada client.

---

# Response Format

Seluruh endpoint menggunakan format response yang telah ditetapkan pada API_SPEC.md.

Tidak diperbolehkan membuat struktur response baru tanpa memperbarui spesifikasi API.

---

# Dependency Management

Seluruh dependency didefinisikan pada requirements.txt.

Tidak diperbolehkan menginstal package secara manual di luar daftar dependency proyek.

---

# Testing

Seluruh modul utama harus dapat diuji secara terpisah.

Minimal meliputi:

* preprocessing
* feature extraction
* stage 1
* stage 2
* pipeline
* API endpoint

---

# Performance

Untuk meningkatkan performa:

* model dimuat saat startup
* hindari alokasi memori yang tidak diperlukan
* gunakan kembali objek yang dapat digunakan ulang
* bersihkan resource sementara setelah inferensi selesai

---

# Security

Tidak diperbolehkan:

* menyimpan secret pada source code
* menyimpan token pada repository
* mencetak environment variable ke log
* menerima request tanpa validasi

---

# Version Control

Seluruh perubahan harus:

* mempertahankan kompatibilitas dengan struktur proyek
* tidak mengubah kontrak API tanpa pembaruan dokumentasi
* menjaga konsistensi penamaan file dan modul

---

# Code Quality Checklist

Sebelum kode dianggap selesai, pastikan:

* mengikuti PROJECT_STRUCTURE.md
* mengikuti AI_PIPELINE.md
* mengikuti API_SPEC.md
* menggunakan type hint
* memiliki docstring
* tidak menggunakan fungsi deprecated
* tidak memuat model setiap request
* tidak mencampurkan business logic dengan router
* seluruh konfigurasi berasal dari environment variable
* mudah dipelihara dan mudah diuji
