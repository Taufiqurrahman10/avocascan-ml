# API_SPEC.md

# AI Service API Specification

## Purpose

Dokumen ini mendefinisikan spesifikasi endpoint yang disediakan oleh AI Service.

Seluruh komunikasi antara Laravel Backend dan FastAPI AI Service harus mengikuti spesifikasi pada dokumen ini.

AI Service tidak menerima request langsung dari Flutter.

---

# Base URL

Development

```text
http://localhost:8000
```

Production

```text
https://<hugging-face-space-url>
```

Seluruh endpoint menggunakan HTTPS pada lingkungan production.

---

# API Version

Versi API saat ini:

```text
v1
```

Endpoint menggunakan prefix:

```text
/api/v1
```

---

# Content Type

Request

```text
multipart/form-data
```

Response

```text
application/json
```

---

# Authentication

AI Service hanya menerima request dari Laravel Backend.

Metode autentikasi:

* Bearer Token
* API Key melalui Header

Nilai token disimpan menggunakan environment variable.

Contoh header:

```text
Authorization: Bearer <AI_SERVICE_TOKEN>
```

---

# Endpoint

## POST /api/v1/predict

Endpoint utama untuk melakukan prediksi.

---

## Description

Endpoint menerima satu gambar dan menjalankan seluruh pipeline inferensi.

Pipeline meliputi:

* Image Validation
* Image Preprocessing
* Stage 1
* Feature Extraction
* Stage 2
* Response Generation

---

# Request

Content-Type

```text
multipart/form-data
```

Body

| Field | Type | Required | Description                 |
| ----- | ---- | -------- | --------------------------- |
| image | File | Ya       | Gambar yang akan diprediksi |

---

# Success Response

HTTP Status

```text
200 OK
```

Contoh response apabila objek adalah alpukat:

```json
{
  "success": true,
  "message": "Prediction completed successfully.",
  "data": {
    "is_avocado": true,
    "stage1": {
      "label": "alpukat",
      "confidence": 0.998
    },
    "stage2": {
      "label": "matang",
      "confidence": 0.982
    },
    "processing_time_ms": 425
  }
}
```

---

# Non-Avocado Response

Apabila objek bukan alpukat:

HTTP Status

```text
200 OK
```

```json
{
  "success": true,
  "message": "Object is not an avocado.",
  "data": {
    "is_avocado": false,
    "stage1": {
      "label": "non_alpukat",
      "confidence": 0.996
    },
    "stage2": null,
    "processing_time_ms": 173
  }
}
```

Stage 2 tidak dijalankan.

---

# Validation Error

HTTP Status

```text
400 Bad Request
```

```json
{
  "success": false,
  "message": "Invalid image file."
}
```

---

# Unauthorized

HTTP Status

```text
401 Unauthorized
```

```json
{
  "success": false,
  "message": "Unauthorized."
}
```

---

# Unsupported Media Type

HTTP Status

```text
415 Unsupported Media Type
```

```json
{
  "success": false,
  "message": "Unsupported image format."
}
```

---

# Internal Server Error

HTTP Status

```text
500 Internal Server Error
```

```json
{
  "success": false,
  "message": "Internal server error."
}
```

---

# Response Rules

Semua response harus memiliki struktur berikut.

```json
{
  "success": true,
  "message": "...",
  "data": {}
}
```

atau

```json
{
  "success": false,
  "message": "..."
}
```

Tidak diperbolehkan menggunakan struktur response yang berbeda pada endpoint lain.

---

# Supported Image Format

Format yang didukung:

* JPG
* JPEG
* PNG

Format lain harus ditolak.

---

# Image Constraints

Ukuran maksimum file ditentukan melalui konfigurasi aplikasi.

AI Service tidak menyimpan file gambar setelah proses inferensi selesai.

---

# Timeout

AI Service harus mengembalikan response sebelum batas timeout yang ditentukan oleh deployment.

Jika proses melebihi timeout, request dianggap gagal.

---

# Processing Rules

Urutan proses wajib:

1. Validasi gambar
2. Preprocessing
3. Stage 1
4. Decision
5. Feature Extraction
6. Stage 2
7. JSON Response

Urutan tersebut tidak boleh diubah.

---

# Security

AI Service tidak boleh:

* menyimpan gambar pengguna
* menyimpan token pada source code
* mencatat informasi sensitif pada log

Seluruh secret harus berasal dari environment variable.

---

# API Compatibility

Apabila terdapat perubahan pada struktur request atau response, perubahan harus dilakukan melalui versi API baru.

Contoh:

```text
/api/v2/predict
```

Endpoint lama tetap dipertahankan selama masa transisi.

---

# Future Endpoints

Endpoint berikut dapat ditambahkan pada versi mendatang:

* GET /health
* GET /version
* GET /model-info
* POST /batch-predict

Penambahan endpoint baru tidak boleh mengubah perilaku endpoint yang sudah ada.
