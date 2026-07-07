# TESTING.md

# Testing Specification

## Purpose

Dokumen ini mendefinisikan strategi pengujian AI Service, Laravel Backend, dan integrasi antar komponen pada proyek AvocaScan.

Tujuan utama pengujian adalah memastikan seluruh sistem berjalan sesuai spesifikasi sebelum deployment.

---

# Testing Scope

Pengujian meliputi:

* AI Service
* Laravel Backend
* Komunikasi Laravel ↔ AI Service
* Integrasi Flutter ↔ Laravel
* Pipeline inferensi
* Penanganan error

---

# Testing Levels

## Unit Testing

Unit test dilakukan pada setiap modul utama.

Modul yang diuji meliputi:

* Image Validation
* Image Preprocessing
* HSV Feature Extraction
* GLCM Feature Extraction
* Stage 1
* Stage 2
* Prediction Pipeline

Setiap modul harus dapat diuji secara terpisah.

---

## Integration Testing

Integration test memastikan komunikasi antar modul berjalan dengan baik.

Skenario:

* Router → Service
* Service → Pipeline
* Pipeline → Stage 1
* Pipeline → Stage 2
* Laravel → AI Service

---

## API Testing

Endpoint yang diuji:

```text id="1fwp6h"
GET /health

POST /api/v1/predict
```

---

# Functional Test Cases

## FT-01

Input:

Gambar alpukat mentah.

Expected Result:

* Stage 1 = Alpukat
* Stage 2 = Mentah

---

## FT-02

Input:

Gambar alpukat matang.

Expected Result:

* Stage 1 = Alpukat
* Stage 2 = Matang

---

## FT-03

Input:

Gambar alpukat busuk.

Expected Result:

* Stage 1 = Alpukat
* Stage 2 = Busuk

---

## FT-04

Input:

Gambar bukan alpukat.

Expected Result:

* Stage 1 = Non-Alpukat
* Stage 2 tidak dijalankan.

---

## FT-05

Input:

File bukan gambar.

Expected Result:

HTTP 415 Unsupported Media Type.

---

## FT-06

Input:

File kosong.

Expected Result:

HTTP 400 Bad Request.

---

## FT-07

Input:

Gambar rusak (corrupt).

Expected Result:

Request ditolak dengan pesan error yang sesuai.

---

## FT-08

Input:

Authorization tidak valid.

Expected Result:

HTTP 401 Unauthorized.

---

## FT-09

Input:

AI Service tidak tersedia.

Expected Result:

Laravel mengembalikan respons error yang sesuai kepada Flutter.

---

## FT-10

Input:

Model gagal dimuat.

Expected Result:

AI Service mengembalikan HTTP 500.

---

# Performance Testing

Pengujian performa dilakukan untuk memastikan:

* model hanya dimuat sekali
* tidak terjadi memory leak
* waktu inferensi masih dalam batas yang dapat diterima

---

# Logging Verification

Pastikan log mencatat:

* waktu request
* hasil Stage 1
* hasil Stage 2
* durasi inferensi
* error

Log tidak boleh menyimpan gambar pengguna maupun token.

---

# Security Testing

Pastikan:

* endpoint tidak dapat diakses tanpa autentikasi
* token tidak tercetak di log
* file selain gambar ditolak
* request yang tidak valid ditangani dengan aman

---

# Deployment Verification

Sebelum deployment dianggap berhasil, pastikan:

* AI Service dapat diakses
* endpoint health berfungsi
* endpoint predict berfungsi
* Laravel dapat berkomunikasi dengan AI Service
* Flutter menerima respons yang benar

---

# Success Criteria

Sistem dinyatakan siap apabila:

* seluruh test case utama berhasil
* pipeline dua tahap berjalan sesuai spesifikasi
* Laravel dan AI Service dapat berkomunikasi dengan baik
* respons API sesuai dengan API_SPEC.md
* tidak ditemukan error kritis selama pengujian
