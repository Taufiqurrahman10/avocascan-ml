# AGENTS.md

# AI Development Guide

## Purpose

Repository ini dikembangkan dengan bantuan AI coding agent.

Sebelum membuat, mengubah, atau menghapus kode, AI agent **wajib membaca seluruh dokumentasi proyek** yang terdapat pada folder `docs/`.

Seluruh implementasi harus mengikuti spesifikasi yang telah ditetapkan.

---

# Required Reading Order

Sebelum menghasilkan kode, baca dokumen berikut secara berurutan.

```text
docs/
│
├── 00_PROJECT_OVERVIEW.md
├── 01_AI_PIPELINE.md
├── 02_PROJECT_STRUCTURE.md
├── 03_API_SPEC.md
├── 04_CODING_GUIDELINES.md
├── 05_MODEL_SPECIFICATION.md
├── 06_LARAVEL_INTEGRATION.md
├── 07_DEPLOYMENT.md
├── 08_TESTING.md
├── 09_TODO.md
└── 10_PROMPT_RULES.md
```

Apabila terdapat konflik antar dokumen, gunakan urutan di atas sebagai prioritas.

---

# Project Overview

Repository ini merupakan AI Service untuk aplikasi **AvocaScan**.

AI Service menggunakan:

* FastAPI
* PyTorch
* Two-Stage Classification
* MobileNetV3
* HSV Feature Extraction
* GLCM Feature Extraction

Deployment dilakukan menggunakan Hugging Face Spaces.

Laravel Backend berjalan secara terpisah di Render.

Flutter tidak berkomunikasi langsung dengan AI Service.

---

# Development Goals

Prioritas utama pengembangan adalah:

* kode bersih
* modular
* mudah diuji
* mudah dipelihara
* mengikuti dokumentasi
* siap untuk deployment

Kecepatan implementasi tidak boleh mengorbankan kualitas arsitektur.

---

# General Rules

Selalu:

* ikuti struktur proyek
* gunakan type hint
* gunakan docstring
* gunakan dependency terbaru yang stabil dan kompatibel
* gunakan environment variable untuk konfigurasi
* tangani seluruh error secara eksplisit

Jangan:

* menggunakan fungsi deprecated
* mengubah struktur proyek tanpa alasan
* mengubah kontrak API
* mengubah pipeline inferensi
* menambahkan dependency tanpa kebutuhan yang jelas

---

# AI Pipeline

Pipeline inferensi wajib mengikuti urutan berikut.

1. Image Validation
2. Image Preprocessing
3. Stage 1 Classification
4. Decision
5. HSV Feature Extraction
6. GLCM Feature Extraction
7. Stage 2 Classification
8. JSON Response

Stage 2 hanya boleh dijalankan apabila Stage 1 menghasilkan kelas **alpukat**.

Catatan: Stage 1 dan Stage 2 menggunakan preprocessing yang berbeda, sehingga implementasi harus dipisahkan dan tidak menggunakan satu pipeline preprocessing untuk kedua model.

---

# Code Generation Rules

Saat diminta membuat kode:

* hasil harus lengkap dan dapat dijalankan
* jangan meninggalkan placeholder kecuali diminta
* jangan membuat asumsi yang bertentangan dengan dokumentasi
* gunakan struktur folder yang telah ditentukan
* buat kode yang mudah diuji
* pertahankan kompatibilitas dengan implementasi yang sudah ada

---

# Refactoring Rules

Saat melakukan refactoring:

* pertahankan perilaku sistem
* jangan mengubah response API
* jangan mengubah pipeline
* jangan mengubah struktur folder
* jangan menghapus fitur tanpa instruksi

---

# Documentation Rules

Apabila implementasi mengubah:

* API
* struktur proyek
* deployment
* pipeline
* model
* konfigurasi

maka dokumentasi terkait harus diperbarui pada perubahan yang sama.

Implementasi dan dokumentasi harus selalu sinkron.

---

# When Information Is Missing

Apabila informasi yang dibutuhkan belum tersedia:

* jangan menebak
* identifikasi informasi yang kurang
* minta klarifikasi sebelum mengimplementasikan perubahan yang berisiko

---

# Definition of Done

Sebuah tugas dianggap selesai apabila:

* implementasi mengikuti seluruh dokumentasi
* kode dapat dijalankan
* tidak ada error yang diketahui
* tidak menggunakan API atau library yang telah deprecated
* mudah dipelihara
* siap untuk diuji
* tidak melanggar arsitektur proyek

---

# Final Instruction

Sebelum menulis satu baris kode pun:

1. Baca seluruh dokumentasi pada folder `docs/`.
2. Pastikan implementasi sesuai dengan spesifikasi proyek.
3. Jika menemukan konflik atau ketidakjelasan, hentikan implementasi dan jelaskan konflik tersebut terlebih dahulu.
4. Jangan menyimpang dari arsitektur tanpa instruksi eksplisit dari pengembang.
