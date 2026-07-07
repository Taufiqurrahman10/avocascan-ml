# AvocaScan AI Service

AI Service untuk aplikasi **AvocaScan**, sebuah sistem klasifikasi kematangan buah alpukat menggunakan pendekatan **Two-Stage Classification Pipeline** berbasis PyTorch dan FastAPI.

Repository ini hanya berisi layanan inferensi AI. Seluruh business logic aplikasi, autentikasi, database, dan manajemen pengguna berada pada repository Laravel Backend.

---

# System Architecture

```text
Flutter Mobile Application
            │
            ▼
Laravel Backend (Render)
            │
            ▼
FastAPI AI Service (Hugging Face Spaces)
            │
            ├── Stage 1 Model
            ├── Image Preprocessing
            ├── HSV Feature Extraction
            ├── GLCM Feature Extraction
            └── Stage 2 Model
```

---

# Features

* Two-Stage Image Classification
* FastAPI REST API
* MobileNetV3-based Classification
* Hybrid Feature Extraction
* HSV Feature Extraction
* GLCM Feature Extraction
* Prediction Confidence Score
* JSON REST Response
* Modular Architecture
* Production-Oriented Project Structure

---

# Technology Stack

## AI Framework

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

* Hugging Face Spaces (Docker)

---

# Project Structure

```text
ai-service/
│
├── app/
├── docs/
├── models/
├── tests/
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── README.md
└── AGENTS.md
```

Penjelasan lengkap mengenai struktur proyek tersedia pada:

```text
docs/02_PROJECT_STRUCTURE.md
```

---

# Documentation

Seluruh dokumentasi proyek tersedia pada folder:

```text
docs/
```

Dokumen utama:

* 00_PROJECT_OVERVIEW.md
* 01_AI_PIPELINE.md
* 02_PROJECT_STRUCTURE.md
* 03_API_SPEC.md
* 04_CODING_GUIDELINES.md
* 05_MODEL_SPECIFICATION.md
* 06_LARAVEL_INTEGRATION.md
* 07_DEPLOYMENT.md
* 08_TESTING.md
* 09_TODO.md
* 10_PROMPT_RULES.md

---

# Development Workflow

Urutan pengembangan yang direkomendasikan:

1. Menyiapkan struktur proyek.
2. Menyiapkan Model Loader.
3. Mengimplementasikan preprocessing.
4. Mengimplementasikan Stage 1.
5. Mengimplementasikan Feature Extraction.
6. Mengimplementasikan Stage 2.
7. Mengimplementasikan Pipeline.
8. Membuat REST API.
9. Melakukan pengujian.
10. Deployment.

---

# Running Locally

## 1. Clone Repository

```bash
git clone <repository-url>
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

---

## 3. Activate Virtual Environment

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Salin file:

```text
.env.example
```

menjadi

```text
.env
```

Kemudian sesuaikan seluruh konfigurasi.

---

## 6. Run FastAPI

```bash
uvicorn app.main:app --reload
```

---

## 7. Open API Documentation

Swagger UI

```text
http://localhost:8000/docs
```

OpenAPI

```text
http://localhost:8000/openapi.json
```

---

# API

Endpoint utama:

```http
POST /api/v1/predict
```

Health Check:

```http
GET /health
```

Spesifikasi lengkap tersedia pada:

```text
docs/03_API_SPEC.md
```

---

# Deployment

Production Deployment:

* Laravel Backend → Render
* AI Service → Hugging Face Spaces (Docker)

Panduan deployment tersedia pada:

```text
docs/07_DEPLOYMENT.md
```

---

# Development Rules

Seluruh implementasi harus mengikuti:

* AGENTS.md
* seluruh dokumentasi pada folder docs/

Jangan mengubah struktur proyek, kontrak API, atau pipeline inferensi tanpa memperbarui dokumentasi terkait.

---

# License

Repository ini dikembangkan sebagai bagian dari Proyek Akhir (Tugas Akhir) dan digunakan untuk tujuan akademik.
