# DEPLOYMENT.md

# Deployment Specification

## Purpose

Dokumen ini mendefinisikan proses deployment seluruh komponen AvocaScan.

Deployment dilakukan secara terpisah agar setiap layanan dapat dikembangkan dan dipelihara secara independen.

---

# Deployment Architecture

```text
                   Android Application
                           │
                           ▼
                       Flutter App
                           │
                           │ HTTPS
                           ▼
              Laravel Backend (Render)
                           │
                           │ HTTPS
                           ▼
      FastAPI AI Service (Hugging Face Spaces)
                           │
                           ▼
                   Stage 1 AI Model
                           │
                           ▼
              Feature Extraction Module
                           │
                           ▼
                   Stage 2 AI Model
```

---

# Components

## Flutter

Deployment sebagai aplikasi Android.

Flutter tidak membutuhkan server.

Flutter hanya berkomunikasi dengan Laravel.

---

## Laravel Backend

Deployment menggunakan Render.

Laravel bertanggung jawab terhadap:

* Authentication
* Authorization
* Database
* Prediction History
* API Backend
* Komunikasi dengan AI Service

---

## AI Service

Deployment menggunakan Hugging Face Spaces.

AI Service terdiri dari:

* FastAPI
* PyTorch
* TorchVision
* OpenCV
* NumPy
* Pillow
* scikit-image

AI Service hanya menangani inferensi.

---

# Repository Structure

Disarankan menggunakan repository terpisah.

```text
avocascan-mobile/
```

Flutter.

```text
avocascan-backend/
```

Laravel.

```text
avocascan-ai/
```

FastAPI AI Service.

Setiap repository memiliki siklus deployment masing-masing.

---

# Hugging Face Spaces

Jenis Space yang digunakan:

Docker Space.

Alasan:

* Mendukung FastAPI.
* Bebas menentukan dependency.
* Mudah dikembangkan.
* Mudah dipindahkan ke platform lain.

---

# AI Service Startup

Ketika AI Service dijalankan:

1. Memuat konfigurasi.
2. Memuat model Stage 1.
3. Memuat model Stage 2.
4. Memastikan model berhasil dimuat.
5. Menyiapkan endpoint API.
6. Siap menerima request.

Model hanya dimuat satu kali saat startup.

---

# Environment Variables

AI Service menggunakan environment variable untuk konfigurasi.

Contoh:

* APP_ENV
* MODEL_STAGE1_PATH
* MODEL_STAGE2_PATH
* API_TOKEN
* LOG_LEVEL

Seluruh secret tidak boleh ditulis langsung pada source code.

---

# Laravel Environment Variables

Laravel menggunakan environment variable untuk komunikasi dengan AI Service.

Contoh:

* AI_SERVICE_URL
* AI_SERVICE_TOKEN
* AI_SERVICE_TIMEOUT

---

# Deployment Flow

## Flutter

Build aplikasi Android.

↓

Distribusi APK.

---

## Laravel

Push repository.

↓

Render melakukan build.

↓

Laravel aktif.

---

## AI Service

Push repository.

↓

Hugging Face Spaces melakukan build.

↓

Dependency diinstal.

↓

FastAPI dijalankan.

↓

Model dimuat.

↓

AI Service siap digunakan.

---

# Communication

```text
Flutter

↓

Laravel

↓

HTTPS

↓

FastAPI

↓

Prediction

↓

Laravel

↓

Flutter
```

Seluruh komunikasi menggunakan HTTPS.

---

# Logging

Laravel dan AI Service memiliki log masing-masing.

Log digunakan untuk:

* debugging
* monitoring
* troubleshooting

Log tidak boleh menyimpan informasi sensitif maupun gambar pengguna.

---

# Health Check

AI Service sebaiknya menyediakan endpoint:

```text
GET /health
```

Endpoint digunakan untuk:

* memastikan service aktif
* pengecekan deployment
* monitoring

---

# Scalability

Arsitektur memungkinkan:

* deployment ulang AI Service tanpa mengganggu Laravel
* pembaruan model tanpa mengubah Flutter
* pengembangan AI Service secara independen

---

# Security

Seluruh komunikasi antar layanan menggunakan:

* HTTPS
* Authorization Header
* Environment Variable
* Input Validation

Tidak diperbolehkan menyimpan token pada repository.

---

# Deployment Checklist

Sebelum deployment, pastikan:

* seluruh dependency telah terpasang
* model final telah tersedia
* environment variable telah dikonfigurasi
* endpoint API telah diuji
* komunikasi Laravel ↔ AI Service berhasil
* Flutter ↔ Laravel berhasil
* log berjalan dengan baik
* endpoint health dapat diakses

Deployment dianggap selesai apabila seluruh komponen dapat berkomunikasi dengan baik dan menghasilkan prediksi sesuai spesifikasi.
