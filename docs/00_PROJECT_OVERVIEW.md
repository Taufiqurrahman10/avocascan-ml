# PROJECT_OVERVIEW.md

# AvocaScan AI Service

## Project Overview

AvocaScan adalah sistem klasifikasi kematangan buah alpukat berbasis kecerdasan buatan yang terdiri dari aplikasi Flutter sebagai client, Laravel sebagai backend utama, dan FastAPI sebagai AI Inference Service.

Sistem menggunakan dua tahap klasifikasi (Two-Stage Classification Pipeline) untuk meningkatkan akurasi serta mencegah prediksi terhadap objek yang bukan alpukat.

AI Service dipisahkan dari backend utama agar proses machine learning berjalan secara independen dan lebih mudah dikembangkan.

---

# Objectives

Tujuan AI Service adalah:

* Menyediakan endpoint inferensi berbasis HTTP.
* Menjalankan seluruh pipeline machine learning.
* Menyembunyikan kompleksitas model dari Flutter dan Laravel.
* Menghasilkan respons JSON yang konsisten.
* Mudah dideploy secara terpisah dari backend.
* Memungkinkan penggantian model tanpa mengubah aplikasi Flutter maupun Laravel.

---

# System Architecture

```text
                Flutter Mobile Application
                           │
                           │ HTTPS
                           ▼
                Laravel Backend (Render)
                           │
                           │ HTTPS
                           ▼
           FastAPI AI Service (Hugging Face Spaces)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  Stage 1 Model      Image Processing   Stage 2 Model
                        HSV
                        GLCM
                           │
                           ▼
                    Prediction Result
```

---

# Component Responsibilities

## Flutter

Bertanggung jawab untuk:

* Mengambil gambar dari kamera atau galeri.
* Mengirim gambar ke Laravel.
* Menampilkan hasil prediksi.
* Menampilkan riwayat prediksi.

Flutter tidak menjalankan proses machine learning.

---

## Laravel Backend (Render)

Laravel menjadi Backend API utama.

Tanggung jawab:

* Authentication.
* Authorization.
* Manajemen pengguna.
* Penyimpanan riwayat prediksi.
* Penyimpanan data aplikasi.
* Validasi request.
* Meneruskan gambar ke AI Service.
* Menyimpan hasil prediksi ke database.
* Mengirim hasil kembali ke Flutter.

Laravel tidak menjalankan model AI.

---

## FastAPI AI Service (Hugging Face Spaces)

FastAPI merupakan layanan khusus untuk inferensi machine learning.

Tanggung jawab:

* Memuat model saat startup.
* Melakukan preprocessing gambar.
* Menjalankan Stage 1.
* Mengekstraksi fitur HSV.
* Mengekstraksi fitur GLCM.
* Menjalankan Stage 2.
* Menghasilkan confidence score.
* Mengembalikan respons JSON.

FastAPI tidak memiliki akses langsung ke database aplikasi.

---

# Deployment Architecture

## Flutter

Didistribusikan sebagai aplikasi Android.

---

## Laravel

Deployment menggunakan Render.

Komponen yang berjalan:

* Laravel API
* Database Connection
* Authentication
* Business Logic

---

## AI Service

Deployment menggunakan Hugging Face Spaces.

Komponen yang berjalan:

* FastAPI
* PyTorch
* TorchVision
* OpenCV
* NumPy
* Pillow
* scikit-image

Model Stage 1 dan Stage 2 dimuat ke memori saat aplikasi FastAPI dijalankan.

---

# AI Pipeline Overview

Sistem menggunakan dua tahap inferensi.

## Stage 1

Tujuan:

Menentukan apakah objek merupakan alpukat.

Output:

* Alpukat
* Non-Alpukat

Apabila hasil adalah Non-Alpukat, proses inferensi dihentikan.

---

## Stage 2

Stage 2 hanya dijalankan apabila Stage 1 menghasilkan Alpukat.

Model menggunakan:

* Informasi visual dari citra.
* Fitur HSV.
* Fitur GLCM.

Output:

* Mentah
* Matang
* Busuk.

---

# Technology Stack

## Mobile

* Flutter

## Backend

* Laravel

## AI Service

* Python
* FastAPI
* Uvicorn

## Machine Learning

* PyTorch
* TorchVision
* OpenCV
* NumPy
* Pillow
* scikit-image

## Deployment

* Render (Laravel Backend)
* Hugging Face Spaces (FastAPI AI Service)

---

# Communication Flow

```text
Flutter

↓

Laravel API (Render)

↓

FastAPI AI Service (Hugging Face Spaces)

↓

Stage 1

↓

Jika Alpukat

↓

HSV + GLCM

↓

Stage 2

↓

Prediction JSON

↓

Laravel

↓

Flutter
```

---

# Design Principles

Seluruh implementasi harus mengikuti prinsip berikut.

* Single Responsibility Principle.
* Separation of Concerns.
* Model hanya dimuat sekali saat startup.
* Business logic dipisahkan dari layer API.
* Konfigurasi menggunakan environment variable.
* Tidak menggunakan API atau library yang telah deprecated.
* Setiap komponen hanya memiliki satu tanggung jawab utama.

---

# Scope

AI Service hanya bertanggung jawab terhadap proses inferensi.

AI Service tidak menangani:

* autentikasi
* database
* riwayat prediksi
* penyimpanan pengguna
* business logic Laravel

Seluruh fungsi tersebut menjadi tanggung jawab Laravel.

---

# Future Development

Arsitektur dirancang agar mendukung pengembangan berikut tanpa mengubah Flutter maupun Laravel:

* pembaruan model AI
* penambahan kelas baru
* penambahan endpoint inferensi
* model versioning
* monitoring
* logging
* deployment AI Service secara independen
