# PROMPT_RULES.md

# Antigravity Development Rules

## Purpose

Dokumen ini mendefinisikan aturan yang harus diikuti sebelum menghasilkan kode, melakukan refactoring, atau memberikan rekomendasi implementasi.

Seluruh implementasi harus mengacu pada dokumentasi proyek yang berada di dalam folder `docs/`.

---

# Development Priority

Sebelum menulis kode, baca dokumen berikut secara berurutan:

1. PROJECT_OVERVIEW.md
2. AI_PIPELINE.md
3. PROJECT_STRUCTURE.md
4. API_SPEC.md
5. CODING_GUIDELINES.md
6. MODEL_SPECIFICATION.md
7. LARAVEL_INTEGRATION.md
8. DEPLOYMENT.md
9. TESTING.md
10. TODO.md

Apabila terdapat konflik, gunakan urutan prioritas tersebut.

---

# Primary Objective

Fokus utama adalah membangun AI Service yang:

* stabil
* modular
* mudah dipelihara
* mudah diuji
* sesuai dokumentasi

Jangan menambahkan fitur di luar ruang lingkup tanpa instruksi.

---

# Architecture Rules

Arsitektur yang digunakan adalah:

```text
Flutter
      │
      ▼
Laravel Backend (Render)
      │
      ▼
FastAPI AI Service (Hugging Face Spaces)
```

Jangan mengubah arsitektur ini tanpa instruksi.

---

# AI Pipeline Rules

Pipeline inferensi wajib mengikuti urutan berikut:

1. Image Validation
2. Image Preprocessing
3. Stage 1
4. Decision
5. HSV
6. GLCM
7. Stage 2
8. JSON Response

Tidak boleh mengubah urutan tersebut.

---

# Stage Rules

Stage 1

* hanya menentukan Alpukat atau Non-Alpukat.

Stage 2

* hanya dijalankan apabila Stage 1 menghasilkan Alpukat.

Stage 2 tidak boleh dipanggil pada kondisi lain.

Catatan: Stage 1 dan Stage 2 menggunakan preprocessing yang berbeda, sehingga implementasi harus dipisahkan dan tidak menggunakan satu pipeline preprocessing untuk kedua model.

---

# Project Structure Rules

Seluruh file harus mengikuti PROJECT_STRUCTURE.md.

Tidak diperbolehkan:

* membuat folder baru tanpa alasan
* memindahkan file sembarangan
* mencampurkan business logic dengan router

---

# API Rules

Gunakan endpoint yang telah ditentukan.

Jangan mengubah:

* URL endpoint
* request format
* response format

tanpa memperbarui API_SPEC.md.

---

# Coding Rules

Seluruh implementasi harus:

* menggunakan type hint
* memiliki docstring untuk class dan fungsi publik
* mengikuti prinsip SOLID
* mengikuti Clean Code
* menggunakan dependency injection jika diperlukan
* menghindari kode duplikat

---

# Model Rules

Model hanya boleh dimuat satu kali saat startup.

Jangan memuat model pada setiap request.

Seluruh inferensi dilakukan menggunakan model yang sudah berada di memori.

---

# Feature Extraction Rules

HSV

GLCM

harus diimplementasikan sebagai modul terpisah.

Jangan menggabungkan seluruh algoritma ke dalam satu file.

---

# Laravel Rules

Laravel bertanggung jawab terhadap:

* authentication
* authorization
* database
* prediction history
* komunikasi dengan AI Service

Laravel tidak menjalankan model AI.

---

# FastAPI Rules

FastAPI bertanggung jawab terhadap:

* preprocessing
* feature extraction
* inference
* response JSON

FastAPI tidak mengakses database aplikasi.

---

# Dependency Rules

Gunakan dependency yang stabil dan masih didukung.

Hindari penggunaan API yang telah deprecated.

Apabila terdapat perubahan besar pada library yang digunakan, sesuaikan implementasi dengan versi terbaru yang kompatibel dengan proyek.

---

# Error Handling Rules

Setiap error harus:

* ditangani
* dicatat pada log
* menghasilkan response JSON yang konsisten

Jangan mengembalikan stack trace kepada client.

---

# Logging Rules

Catat:

* startup
* shutdown
* request
* hasil Stage 1
* hasil Stage 2
* durasi inferensi
* error

Jangan mencatat:

* token
* password
* gambar pengguna
* informasi sensitif lainnya

---

# Security Rules

Gunakan:

* HTTPS
* Authorization Header
* Environment Variable

Jangan menyimpan secret pada source code.

---

# Documentation Rules

Apabila implementasi mengubah:

* struktur proyek
* endpoint
* pipeline
* model
* deployment

maka dokumentasi terkait harus diperbarui pada commit yang sama.

---

# Code Generation Rules

Saat diminta membuat kode:

1. Ikuti seluruh dokumentasi proyek.
2. Gunakan struktur proyek yang telah ditetapkan.
3. Berikan implementasi yang lengkap dan dapat dijalankan.
4. Jangan meninggalkan placeholder kecuali diminta.
5. Jangan membuat asumsi yang bertentangan dengan dokumentasi.
6. Jelaskan apabila terdapat ketidakpastian atau informasi yang kurang.

---

# Refactoring Rules

Saat melakukan refactoring:

* pertahankan perilaku sistem
* jangan mengubah kontrak API
* jangan mengubah pipeline inferensi
* jangan mengubah struktur response

---

# Testing Rules

Setiap fitur baru harus mempertimbangkan kebutuhan pengujian sesuai TESTING.md.

---

# Communication Rules

Apabila terdapat informasi yang bertentangan, jangan memilih secara otomatis.

Identifikasi konflik dan jelaskan bagian dokumentasi yang bertentangan sebelum memberikan solusi.

---

# Success Criteria

Implementasi dianggap berhasil apabila:

* sesuai seluruh dokumentasi proyek
* mudah dipelihara
* mudah diuji
* tidak menggunakan praktik yang telah deprecated
* dapat dideploy sesuai DEPLOYMENT.md
* dapat diintegrasikan dengan Laravel tanpa perubahan kontrak API
