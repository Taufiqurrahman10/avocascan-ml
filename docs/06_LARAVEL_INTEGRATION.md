# LARAVEL_INTEGRATION.md

# Laravel Integration Specification

## Purpose

Dokumen ini menjelaskan bagaimana Laravel Backend berkomunikasi dengan AI Service yang berjalan pada Hugging Face Spaces.

Laravel merupakan Backend utama aplikasi dan menjadi satu-satunya komponen yang berkomunikasi dengan Flutter maupun AI Service.

Flutter tidak diperbolehkan mengakses AI Service secara langsung.

---

# System Architecture

```text
Flutter
    │
    │ HTTPS
    ▼
Laravel Backend (Render)
    │
    │ HTTPS
    ▼
FastAPI AI Service (Hugging Face Spaces)
```

---

# Responsibilities

## Flutter

Flutter bertanggung jawab untuk:

* Login
* Registrasi
* Upload gambar
* Menampilkan hasil prediksi
* Menampilkan riwayat prediksi

Flutter tidak mengetahui keberadaan AI Service.

---

## Laravel

Laravel merupakan pusat business logic.

Laravel bertanggung jawab untuk:

* Authentication
* Authorization
* Validasi request
* Penyimpanan data
* Penyimpanan riwayat prediksi
* Komunikasi dengan AI Service
* Penanganan error
* Mengembalikan response kepada Flutter

Laravel tidak menjalankan model AI.

---

## FastAPI AI Service

FastAPI hanya bertanggung jawab terhadap:

* preprocessing
* feature extraction
* inferensi model
* response JSON

FastAPI tidak mengetahui database aplikasi.

---

# Prediction Flow

```text
Flutter

↓

POST /prediction

↓

Laravel

↓

Validasi User

↓

Validasi File

↓

POST /api/v1/predict

↓

FastAPI

↓

Inference

↓

Prediction JSON

↓

Laravel

↓

Simpan Riwayat

↓

Response

↓

Flutter
```

---

# Laravel Endpoint

Endpoint yang digunakan Flutter.

```http
POST /prediction
```

Endpoint ini menjadi satu-satunya endpoint prediksi yang diketahui Flutter.

---

# Communication With AI Service

Laravel mengirim request HTTP POST ke AI Service.

Request menggunakan:

* multipart/form-data
* Authorization Header
* Timeout yang dapat dikonfigurasi

Laravel tidak mengubah isi gambar.

---

# Request Payload

Laravel meneruskan:

* image

Tidak melakukan preprocessing.

Tidak melakukan resize.

Tidak melakukan normalisasi.

Seluruh preprocessing dilakukan oleh AI Service.

---

# AI Response

Laravel menerima JSON dari AI Service.

Contoh:

* status
* message
* stage1
* stage2
* confidence
* processing time

Laravel bertanggung jawab mengubah response tersebut menjadi response aplikasi apabila diperlukan.

---

# Prediction History

Apabila inferensi berhasil, Laravel menyimpan:

* user
* nama file (opsional)
* hasil Stage 1
* hasil Stage 2
* confidence
* waktu prediksi

Laravel tidak menyimpan gambar apabila tidak diperlukan oleh aplikasi.

---

# Error Handling

Apabila AI Service gagal diakses:

Laravel mengembalikan response yang sesuai kepada Flutter.

Kemungkinan kondisi:

* timeout
* connection refused
* unauthorized
* internal server error

Laravel tidak boleh menampilkan detail internal AI Service kepada pengguna.

---

# Retry Policy

Laravel tidak melakukan retry otomatis.

Setiap request hanya dikirim satu kali.

Retry dapat dipertimbangkan pada pengembangan berikutnya.

---

# Timeout

Timeout komunikasi dengan AI Service harus dapat dikonfigurasi menggunakan environment variable.

Nilai timeout tidak boleh ditulis langsung pada source code.

---

# Environment Variables

Contoh konfigurasi:

* AI_SERVICE_URL
* AI_SERVICE_TOKEN
* AI_SERVICE_TIMEOUT

Seluruh konfigurasi harus berasal dari environment variable.

---

# Security

Laravel wajib:

* mengirim Authorization Header
* memvalidasi file sebelum diteruskan
* memvalidasi user
* melindungi endpoint menggunakan authentication

Flutter tidak boleh mengetahui token AI Service.

---

# Logging

Laravel mencatat:

* request prediction
* response AI Service
* durasi request
* error

Laravel tidak mencatat token maupun informasi sensitif.

---

# Future Development

Arsitektur harus memungkinkan:

* penggantian AI Service
* penambahan endpoint AI
* model versioning
* batch prediction

Perubahan AI Service tidak boleh memerlukan perubahan besar pada Flutter.
