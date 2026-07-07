# PROJECT_STRUCTURE.md

# FastAPI AI Service Project Structure

## Purpose

Dokumen ini mendefinisikan struktur direktori AI Service.

Seluruh implementasi harus mengikuti struktur ini. Tidak diperbolehkan membuat file atau folder di luar struktur tanpa alasan yang jelas.

---

# Root Directory

```text
ai-service/
│
├── app/
├── models/
├── tests/
├── docs/
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

---

# app/

Folder utama aplikasi FastAPI.

```text
app/
│
├── main.py
├── config.py
├── dependencies.py
├── routers/
├── services/
├── schemas/
├── preprocessing/
├── feature_extraction/
├── inference/
├── utils/
└── exceptions/
```

---

# main.py

Entry point aplikasi.

Bertanggung jawab untuk:

* Membuat instance FastAPI.
* Mendaftarkan router.
* Memuat model saat startup.
* Menutup resource saat shutdown.

Business logic tidak boleh ditulis di file ini.

---

# config.py

Berisi seluruh konfigurasi aplikasi.

Contoh:

* path model
* threshold
* timeout
* environment variable

Seluruh konfigurasi harus dibaca dari environment variable.

---

# dependencies.py

Berisi dependency injection FastAPI apabila diperlukan.

---

# routers/

Seluruh endpoint HTTP berada pada folder ini.

Contoh:

```text
routers/
│
└── prediction.py
```

Router hanya bertugas:

* menerima request
* memvalidasi input
* memanggil service
* mengembalikan response

Router tidak boleh menjalankan inferensi secara langsung.

---

# services/

Berisi business logic aplikasi.

Contoh:

```text
services/
│
└── prediction_service.py
```

Prediction Service bertanggung jawab untuk:

* menjalankan pipeline inferensi
* mengatur urutan proses
* menggabungkan hasil Stage 1 dan Stage 2

---

# preprocessing/

Berisi preprocessing gambar.

Contoh:

```text
preprocessing/
│
├── image_loader.py
├── resize.py
├── normalize.py
└── transform.py
```

Seluruh preprocessing harus identik dengan proses training.

Catatan: Stage 1 dan Stage 2 menggunakan preprocessing yang berbeda, sehingga implementasi harus dipisahkan dan tidak menggunakan satu pipeline preprocessing untuk kedua model.

---

# feature_extraction/

Berisi ekstraksi fitur.

```text
feature_extraction/
│
├── hsv.py
└── glcm.py
```

Masing-masing file hanya bertanggung jawab terhadap satu jenis fitur.

---

# inference/

Berisi seluruh kode yang berhubungan dengan model AI.

```text
inference/
│
├── model_loader.py
├── stage1.py
├── stage2.py
└── pipeline.py
```

---

## model_loader.py

Bertanggung jawab:

* memuat model Stage 1
* memuat model Stage 2
* menyimpan model di memori
* menyediakan akses model ke service

Model hanya boleh dimuat satu kali saat startup.

---

## stage1.py

Menjalankan inferensi Stage 1.

Input:

gambar hasil preprocessing.

Output:

* Alpukat
* Non-Alpukat

---

## stage2.py

Menjalankan inferensi Stage 2.

Input:

* image tensor
* HSV feature
* GLCM feature

Output:

* Mentah
* Matang
* Busuk

---

## pipeline.py

Mengatur seluruh pipeline.

Urutan:

1. preprocessing
2. stage 1
3. cek hasil
4. feature extraction
5. stage 2
6. response

Pipeline tidak boleh dilewati.

---

# schemas/

Berisi model request dan response.

Contoh:

```text
schemas/
│
├── request.py
└── response.py
```

Gunakan Pydantic v2.

---

# utils/

Berisi helper umum.

Contoh:

```text
utils/
│
├── image.py
├── logger.py
├── timer.py
└── file.py
```

Utility tidak boleh berisi business logic.

---

# exceptions/

Berisi custom exception.

Contoh:

```text
exceptions/
│
├── image_exception.py
├── inference_exception.py
└── model_exception.py
```

Gunakan exception khusus agar error mudah ditangani.

---

# models/

Berisi seluruh file model.

```text
models/
│
├── stage1/
│      ├── best_model.pth
│      ├── class_names.json
│      └── metadata.json
│
└── stage2/
       ├── best_model.pth
       ├── class_names.json
       └── metadata.json
```

Folder ini hanya berisi aset model.

Tidak boleh berisi kode Python.

---

# tests/

Berisi unit test dan integration test.

```text
tests/
│
├── test_stage1.py
├── test_stage2.py
├── test_pipeline.py
└── test_api.py
```

---

# docs/

Berisi dokumentasi proyek.

Contoh:

```text
docs/
│
├── PROJECT_OVERVIEW.md
├── AI_PIPELINE.md
├── PROJECT_STRUCTURE.md
├── API_SPEC.md
├── CODING_GUIDELINES.md
└── DEPLOYMENT.md
```

---

# Design Rules

Seluruh implementasi wajib mengikuti aturan berikut.

* Router tidak boleh memuat model.
* Router tidak boleh melakukan preprocessing.
* Router tidak boleh menjalankan inferensi.
* Business logic berada di service.
* Pipeline berada di inference.
* Feature extraction dipisahkan dari preprocessing.
* Model dimuat satu kali saat startup.
* Tidak ada hardcoded path.
* Seluruh path menggunakan konfigurasi.

---

# Communication Flow

```text
Flutter

↓

Laravel Backend

↓

POST /predict

↓

Prediction Router

↓

Prediction Service

↓

Inference Pipeline

↓

Stage 1

↓

HSV + GLCM

↓

Stage 2

↓

Response Schema

↓

Laravel

↓

Flutter
```
