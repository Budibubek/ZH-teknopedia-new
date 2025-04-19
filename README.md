# 📘 Dokumentasi API Scraper Wikipedia Indonesia

**Versi:** 1.0  
**Author:** [Nama Kamu]  
**Stack:** Python + Flask + BeautifulSoup + Google Sheets

---

## 🚀 Cara Menjalankan Project

### 🔧 Requirements

Install dependencies terlebih dahulu:

```bash
pip install flask requests beautifulsoup4
```

### ▶️ Jalankan Server

```bash
python app.py
```

API akan berjalan di:
```
http://localhost:5000
```

---

## 📂 Format Google Sheet

Google Sheet harus memiliki kolom:
- `slug` — sebagai parameter pencarian
- `judul`, `deskripsi`, `gambar`, `konten` — akan diisi otomatis oleh API

---

## 📡 Endpoint API

### 1. `GET /artikel`

Mendapatkan daftar artikel dari Google Sheet.

#### ✅ Query Parameters:

| Nama       | Tipe   | Keterangan                       |
|------------|--------|----------------------------------|
| `sheet_id` | string | ID Google Sheet                  |
| `gid`      | string | ID sheet/tab di dalam dokumen    |
| `page`     | int    | (Opsional) Halaman               |
| `limit`    | int    | (Opsional) Jumlah per halaman    |

#### 📥 Contoh Request:

```
GET /artikel?sheet_id=1abc123xyz&gid=0&page=1&limit=10
```

#### 📤 Contoh Response:

```json
{
  "data": [
    {
      "judul": "Contoh Artikel",
      "slug": "contoh-artikel",
      "deskripsi": "Ini adalah contoh deskripsi.",
      "gambar": "https://...",
      "konten": "Isi konten lengkap artikel..."
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 10
}
```

---

### 2. `GET /artikel/detail`

Mendapatkan detail artikel berdasarkan slug.

#### ✅ Query Parameters:

| Nama       | Tipe   | Keterangan                         |
|------------|--------|------------------------------------|
| `sheet_id` | string | ID Google Sheet                    |
| `gid`      | string | ID sheet/tab di dalam dokumen      |
| `slug`     | string | Slug artikel yang ingin diambil    |

#### 📥 Contoh Request:

```
GET /artikel/detail?sheet_id=1abc123xyz&gid=0&slug=sejarah-indonesia
```

#### 📤 Contoh Response:

```json
{
  "judul": "Sejarah Indonesia",
  "slug": "sejarah-indonesia",
  "deskripsi": "Penjelasan singkat sejarah Indonesia...",
  "gambar": "https://...",
  "konten": "Isi artikel sejarah Indonesia..."
}
```

---

### 3. `GET /scrape`

Melakukan scraping konten dari Wikipedia Indonesia dan menyimpan hasilnya ke Google Sheet.

#### ✅ Query Parameters:

| Nama       | Tipe   | Keterangan                                |
|------------|--------|-------------------------------------------|
| `sheet_id` | string | ID Google Sheet                           |
| `gid`      | string | ID sheet/tab di dalam dokumen             |

> Scraper ini mengambil semua slug di kolom pertama (A), lalu mengakses Wikipedia Indonesia berdasarkan slug tersebut.

#### 📥 Contoh Request:

```
GET /scrape?sheet_id=1abc123xyz&gid=0
```

#### 📤 Contoh Response:

```json
{
  "message": "Scraping selesai.",
  "jumlah_data": 5,
  "waktu": "2025-04-16T12:00:00"
}
```

---

## ⚠️ Catatan

- Pastikan Google Sheet kamu bisa diakses publik (share: **Anyone with the link**).
- Slug Wikipedia adalah bagian akhir dari URL. Misalnya:  
  `https://id.wikipedia.org/wiki/Sejarah_Indonesia`  
  maka `slug`-nya adalah `Sejarah_Indonesia`.

---

## 📎 License

MIT License
