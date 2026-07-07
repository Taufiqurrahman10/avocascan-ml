# AI_PIPELINE.md

# AI Inference Pipeline Specification

## Purpose

Dokumen ini mendefinisikan pipeline inferensi yang digunakan oleh AI Service AvocaScan.

Seluruh implementasi harus mengikuti spesifikasi pada dokumen ini. Perubahan terhadap urutan proses atau logika inferensi harus dilakukan secara sadar dan didokumentasikan.

---

# Pipeline Overview

AI Service menggunakan pendekatan **Two-Stage Classification Pipeline**.

Tahap pertama bertugas memverifikasi bahwa objek pada gambar merupakan buah alpukat. Tahap kedua hanya dijalankan apabila hasil tahap pertama adalah alpukat, kemudian menentukan tingkat kematangan buah.

```text
Flutter
    │
    ▼
Laravel Backend (Render)
    │
    ▼
FastAPI AI Service (Hugging Face Spaces)
    │
    ▼
Image Validation
    │
    ▼
Image Preprocessing
    │
    ▼
Stage 1 Classification
    │
    ├── Non-Alpukat
    │        │
    │        ▼
    │   Return Response
    │
    └── Alpukat
             │
             ▼
      Feature Extraction
      │
      ├── HSV
      └── GLCM
             │
             ▼
     Stage 2 Classification
             │
             ▼
      JSON Response
             │
             ▼
Laravel Backend
             │
             ▼
Flutter
```

---

# Communication Flow

Komunikasi antar komponen dilakukan melalui protokol HTTPS.

Alur komunikasi adalah sebagai berikut:

1. Flutter mengirim gambar ke Laravel.
2. Laravel melakukan validasi awal apabila diperlukan.
3. Laravel meneruskan gambar ke FastAPI AI Service.
4. FastAPI menjalankan seluruh proses inferensi.
5. FastAPI mengembalikan hasil dalam format JSON.
6. Laravel menyimpan hasil prediksi ke database.
7. Laravel mengirim respons kepada Flutter.

Flutter tidak berkomunikasi langsung dengan AI Service.

---

# Stage 0 — Receive Request

FastAPI menerima request HTTP POST dari Laravel.

Request menggunakan format:

* multipart/form-data
* satu file gambar

Setiap request hanya memproses satu gambar.

---

# Stage 1 — Image Validation

Sebelum inferensi dilakukan, sistem harus memastikan bahwa gambar dapat diproses.

Validasi meliputi:

* file tersedia
* file merupakan gambar
* gambar dapat dibaca
* format gambar didukung
* ukuran file masih dalam batas yang ditentukan

Apabila validasi gagal, proses dihentikan dan AI Service mengembalikan respons error.

---

# Stage 2 — Image Preprocessing

Gambar yang valid diproses agar sesuai dengan kebutuhan model.

Tahapan preprocessing harus identik dengan proses yang digunakan saat pelatihan model.

Preprocessing dapat mencakup:

* membaca gambar
* konversi ruang warna apabila diperlukan
* resize
* normalisasi
* konversi menjadi tensor

Seluruh parameter preprocessing harus konsisten dengan proses training.

Catatan: Stage 1 dan Stage 2 menggunakan preprocessing yang berbeda, sehingga implementasi harus dipisahkan dan tidak menggunakan satu pipeline preprocessing untuk kedua model.

---

# Stage 3 — Object Classification (Stage 1 Model)

Model pertama bertugas mengidentifikasi apakah objek pada gambar merupakan alpukat.

Input:

* citra hasil preprocessing

Output:

* Alpukat
* Non-Alpukat

---

# Decision Flow

## Jika hasil adalah Non-Alpukat

Pipeline dihentikan.

Feature extraction tidak dijalankan.

Stage 2 tidak dijalankan.

AI Service langsung mengembalikan respons bahwa objek bukan alpukat.

---

## Jika hasil adalah Alpukat

Pipeline dilanjutkan menuju proses ekstraksi fitur.

---

# Stage 4 — Feature Extraction

Feature extraction hanya dilakukan apabila objek telah dipastikan sebagai alpukat.

Fitur yang digunakan terdiri dari dua kelompok.

## HSV

Digunakan untuk memperoleh karakteristik warna buah.

---

## GLCM

Digunakan untuk memperoleh karakteristik tekstur permukaan buah.

---

Implementasi seluruh metode ekstraksi fitur harus identik dengan implementasi pada proses pelatihan model.

---

# Stage 5 — Ripeness Classification (Stage 2 Model)

Tahap kedua bertugas menentukan tingkat kematangan buah.

Input model terdiri dari:

* citra hasil preprocessing
* fitur HSV
* fitur GLCM

Output:

* Mentah
* Matang
* Busuk

Stage 2 tidak boleh dijalankan apabila Stage 1 menghasilkan kelas Non-Alpukat.

---

# Stage 6 — Confidence Score

Selain label prediksi, AI Service menghasilkan nilai confidence.

Confidence merupakan probabilitas prediksi yang dihasilkan model.

Nilai confidence berada pada rentang:

* 0.0
* 1.0

---

# Stage 7 — Response Generation

Setelah inferensi selesai, AI Service menghasilkan respons JSON yang dikirim kembali kepada Laravel.

Laravel menggunakan hasil tersebut untuk:

* menyimpan riwayat prediksi
* mengirim hasil ke Flutter

Seluruh respons harus menggunakan struktur JSON yang konsisten.

---

# Error Handling

AI Service harus menangani kondisi berikut:

* file tidak ditemukan
* format file tidak didukung
* gambar rusak
* model gagal dimuat
* proses preprocessing gagal
* feature extraction gagal
* inferensi gagal
* kesalahan internal

Seluruh error harus menghasilkan respons JSON yang informatif.

---

# Performance Requirements

Untuk meningkatkan performa, model harus dimuat satu kali ketika aplikasi FastAPI dijalankan.

Model tidak boleh dimuat ulang pada setiap request.

Seluruh request menggunakan model yang telah tersedia di memori.

---

# Logging

AI Service harus mencatat informasi berikut:

* waktu request
* durasi inferensi
* hasil Stage 1
* hasil Stage 2 apabila dijalankan
* status request
* pesan error apabila terjadi kegagalan

Log tidak boleh menyimpan gambar pengguna.

---

# Design Principles

Pipeline harus memenuhi prinsip berikut:

* setiap tahap memiliki satu tanggung jawab
* preprocessing dipisahkan dari feature extraction
* Stage 1 dan Stage 2 dipisahkan dalam modul yang berbeda
* feature extraction dipisahkan dari implementasi model
* seluruh pipeline bersifat modular
* perubahan pada satu modul tidak boleh memengaruhi modul lain secara signifikan

---

# Future Extensibility

Pipeline dirancang agar mendukung pengembangan di masa mendatang, seperti:

* penggantian model Stage 1
* penggantian model Stage 2
* penambahan metode ekstraksi fitur
* penambahan kelas baru
* penambahan endpoint inferensi
* model versioning
* monitoring dan logging yang lebih lengkap
