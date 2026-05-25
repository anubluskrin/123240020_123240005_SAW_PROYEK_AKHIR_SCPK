# 🗺️ SPK Wisata Jogja — Metode SAW

Sistem Pendukung Keputusan (SPK) berbasis web untuk merekomendasikan destinasi wisata terbaik di Yogyakarta menggunakan metode **Simple Additive Weighting (SAW)**.

Dibangun dengan **Python + Streamlit**, aplikasi ini memungkinkan wisatawan memilih destinasi secara objektif berdasarkan preferensi dan bobot kriteria yang dapat dikustomisasi.

---

## 📸 Tampilan Aplikasi

| Halaman | Deskripsi |
|---|---|
| **Beranda** | Ringkasan dataset, kriteria penilaian, dan alur metode SAW |
| **Dataset** | Eksplorasi & filter 437 destinasi wisata Jogja |
| **Hitung SPK** | Konfigurasi bobot, jalankan SAW, lihat peringkat |
| **Visualisasi** | Grafik distribusi, scatter plot, histogram, dan skor SAW |

---

## 🧮 Metode SAW

Simple Additive Weighting (SAW) adalah metode MADM (*Multi-Attribute Decision Making*) yang bekerja dengan:

1. **Membangun Matriks Keputusan** — nilai setiap alternatif pada tiap kriteria
2. **Normalisasi** — benefit: `xᵢⱼ / max(xⱼ)` | cost: `min(xⱼ) / xᵢⱼ`
3. **Pembobotan** — `Skor = Σ(wⱼ × rᵢⱼ)`
4. **Perangkingan** — alternatif diurutkan dari skor tertinggi

### Kriteria Penilaian

| Kode | Kriteria | Tipe | Keterangan |
|---|---|---|---|
| C1 | Rating Wisatawan | Benefit | Nilai rating dari pengunjung (skala 1–5) |
| C2 | Harga Tiket (HTM) | Cost | Harga tiket masuk dalam Rupiah |
| C3 | Fasilitas | Benefit | Skor fasilitas berdasarkan jenis wisata (1–5) |
| C4 | Aksesibilitas | Benefit | Skor kemudahan akses ke lokasi (2–5) |
| C5 | Popularitas | Benefit | Skor popularitas berbasis rating (1–5) |

---

## 📦 Struktur Proyek

```
spk-wisata-jogja/
├── app.py                  # Aplikasi utama Streamlit
└── tourism_jogja.csv       # Dataset 437 destinasi wisata

```

---

## ⚙️ Instalasi & Menjalankan

### Prasyarat
- Python 3.8+
- pip

### Langkah-langkah

```bash
# 1. Clone repositori
git clone https://github.com/username/spk-wisata-jogja.git
cd spk-wisata-jogja

# 2. Buat virtual environment (opsional tapi disarankan)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependensi
pip install -r requirements.txt

# 4. Jalankan aplikasi
streamlit run app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

---

## 📋 Dependensi

```txt
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
```

---

## 📊 Dataset

Dataset `tourism_jogja.csv` berisi **437 destinasi wisata** di Yogyakarta dengan kolom utama:

| Kolom | Deskripsi |
|---|---|
| `place_id` | ID unik destinasi |
| `name` | Nama destinasi wisata |
| `type` | Jenis wisata (Alam, Budaya, Pantai, dll.) |
| `rating` | Rating wisatawan |
| `htm` | Harga tiket masuk (Rp) |

Kolom turunan (`fasilitas`, `aksesibilitas`, `popularitas`) dibangkitkan secara programatik berdasarkan aturan domain dan seed deterministik.

**Sumber:** Kaggle / Data Primer Destinasi Wisata Yogyakarta

---

## 🎛️ Cara Penggunaan

1. Buka halaman **Hitung SPK** di sidebar
2. Atur **bobot kriteria** (C1–C5) sesuai preferensi — total harus = 100%
3. Tentukan **filter jenis wisata** dan **batas harga tiket**
4. Klik **"Jalankan Perhitungan SAW"**
5. Lihat hasil perangkingan dan top 3 rekomendasi
6. Kunjungi halaman **Visualisasi** untuk analitik grafis

---



> Dibuat untuk keperluan akademis — Praktikum Sistem Cerdas Pendukung Keputusan.
