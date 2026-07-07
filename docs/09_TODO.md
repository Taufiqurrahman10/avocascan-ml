# TODO.md

# AvocaScan AI Service Development Roadmap

## Purpose

Dokumen ini menjadi roadmap implementasi proyek AI Service.

Setiap tugas harus diselesaikan secara berurutan. Tahap berikutnya tidak boleh dimulai sebelum tahap sebelumnya selesai dan diverifikasi.

---

# Phase 1 — Project Setup

## Objectives

Membangun fondasi proyek.

### Tasks

* [ ] Membuat struktur proyek sesuai PROJECT_STRUCTURE.md
* [ ] Membuat repository Git
* [ ] Menambahkan dependency awal
* [ ] Membuat konfigurasi environment
* [ ] Membuat Dockerfile
* [ ] Membuat .dockerignore
* [ ] Membuat requirements.txt
* [ ] Menjalankan FastAPI pertama kali
* [ ] Memastikan aplikasi dapat berjalan

### Exit Criteria

* FastAPI berhasil dijalankan.
* Struktur proyek sesuai spesifikasi.

---

# Phase 2 — Model Preparation

## Objectives

Menyiapkan model AI.

### Tasks

* [ ] Menambahkan model Stage 1
* [ ] Menambahkan model Stage 2
* [ ] Menambahkan metadata model
* [ ] Menambahkan class mapping
* [ ] Membuat Model Loader
* [ ] Memastikan kedua model berhasil dimuat

### Exit Criteria

* Kedua model berhasil dimuat saat startup.

---

# Phase 3 — Image Processing

## Objectives

Menyiapkan preprocessing.

### Tasks

* [ ] Image Validation
* [ ] Image Loader
* [ ] Resize
* [ ] Normalize
* [ ] Tensor Conversion

### Exit Criteria

* Output preprocessing identik dengan training.

---

# Phase 4 — Feature Extraction

## Objectives

Mengimplementasikan seluruh ekstraksi fitur.

### Tasks

* [ ] HSV
* [ ] GLCM

### Exit Criteria

* Seluruh fitur sesuai dengan implementasi training.

---

# Phase 5 — Stage 1

## Objectives

Mengimplementasikan model Stage 1.

### Tasks

* [ ] Prediction
* [ ] Confidence Score
* [ ] Decision Logic

### Exit Criteria

* Model mampu membedakan Alpukat dan Non-Alpukat.

---

# Phase 6 — Stage 2

## Objectives

Mengimplementasikan model Stage 2.

### Tasks

* [ ] Hybrid Input
* [ ] Prediction
* [ ] Confidence Score

### Exit Criteria

* Model menghasilkan kelas Mentah, Matang, dan Busuk.

---

# Phase 7 — Pipeline

## Objectives

Menghubungkan seluruh proses inferensi.

### Tasks

* [ ] Validasi gambar
* [ ] Preprocessing
* [ ] Stage 1
* [ ] Decision
* [ ] Feature Extraction
* [ ] Stage 2
* [ ] JSON Response

### Exit Criteria

* Pipeline inferensi berjalan sesuai AI_PIPELINE.md.

---

# Phase 8 — REST API

## Objectives

Menyediakan endpoint FastAPI.

### Tasks

* [ ] GET /health
* [ ] POST /api/v1/predict
* [ ] Request Validation
* [ ] Response Schema
* [ ] Error Handling

### Exit Criteria

* Endpoint dapat diuji menggunakan Postman atau Bruno.

---

# Phase 9 — Laravel Integration

## Objectives

Menghubungkan Laravel dengan AI Service.

### Tasks

* [ ] Konfigurasi environment variable
* [ ] HTTP Client
* [ ] Authorization Header
* [ ] Upload gambar
* [ ] Parsing response
* [ ] Penyimpanan riwayat prediksi
* [ ] Penanganan error

### Exit Criteria

* Laravel berhasil menerima hasil prediksi dari AI Service.

---

# Phase 10 — Flutter Integration

## Objectives

Menghubungkan Flutter dengan Laravel.

### Tasks

* [ ] Upload gambar
* [ ] Menampilkan loading
* [ ] Menampilkan hasil Stage 1
* [ ] Menampilkan hasil Stage 2
* [ ] Menampilkan confidence
* [ ] Menampilkan pesan error

### Exit Criteria

* Flutter dapat melakukan prediksi end-to-end.

---

# Phase 11 — Testing

## Objectives

Melakukan pengujian menyeluruh.

### Tasks

* [ ] Unit Testing
* [ ] Integration Testing
* [ ] API Testing
* [ ] Functional Testing
* [ ] Error Testing

### Exit Criteria

* Semua test utama berhasil.

---

# Phase 12 — Deployment

## Objectives

Mendeploy seluruh sistem.

### Tasks

* [ ] Deploy Laravel ke Render
* [ ] Deploy AI Service ke Hugging Face Spaces
* [ ] Konfigurasi environment variable
* [ ] Uji komunikasi antar layanan
* [ ] Verifikasi endpoint production

### Exit Criteria

* Sistem dapat digunakan dari Flutter hingga AI Service.

---

# Final Checklist

Sebelum proyek dinyatakan selesai, pastikan:

* [ ] Dokumentasi lengkap
* [ ] Model final digunakan
* [ ] API sesuai API_SPEC.md
* [ ] Struktur proyek sesuai PROJECT_STRUCTURE.md
* [ ] Pipeline sesuai AI_PIPELINE.md
* [ ] Laravel berhasil terintegrasi
* [ ] Flutter berhasil terintegrasi
* [ ] Deployment berhasil
* [ ] Pengujian selesai
* [ ] Seluruh source code telah di-review
