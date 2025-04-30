import pandas as pd

import pandas as pd

import pandas as pd
import math

class ArtikelSheet:
    def __init__(self, sheet_id, gid):
        self.sheet_id = sheet_id
        self.gid = gid
        self.url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?format=csv&gid={self.gid}"        
        self.df = None

    def ambil_data(self):
        try:
            self.df = pd.read_csv(self.url)
            print("✅ Data berhasil dimuat.")
        except Exception as e:
            print("❌ Gagal memuat data:", e)

    def get_artikel(self):
        if self.df is None or self.df.empty:
            print("⚠️ Data belum dimuat atau kosong. Panggil .ambil_data() dulu.")
            return None
        try:
            return self.df.to_dict(orient="records")
        except Exception as e:
            print(f"❌ Terjadi kesalahan saat mengambil data: {e}")
            return None

    def get_artikel_paginated(self, page=1, per_page=10):
        if self.df is None or self.df.empty:
            print("⚠️ Data belum dimuat atau kosong. Panggil .ambil_data() dulu.")
            return None
        try:
            # Batasi data hanya sampai kolom I
            self.df = self.df.iloc[:, :9].dropna()

            total_artikel = len(self.df)
            total_halaman = math.ceil(total_artikel / per_page)
            page = max(1, min(page, total_halaman))  # hindari halaman invalid

            start = (page - 1) * per_page
            end = start + per_page
            # Filter out rows where the date has not passed
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')  # Ensure 'date' is in datetime format
            today = pd.Timestamp.now()
            self.df = self.df[self.df['date'] <= today]  # Keep only rows where the date is in the past or today

            self.df = self.df.sort_values(by='date', ascending=False)  # Sort by date in descending order
            paginated_df = self.df.iloc[start:end]
            print(paginated_df)

            return {
                "pagination":{
                    "halaman_sekarang": page,
                    "total_artikel": total_artikel,
                    "total_halaman": total_halaman,
                },
                "artikel": paginated_df.to_dict(orient="records")
            }
        except Exception as e:
            print(f"❌ Terjadi kesalahan saat paginasi: {e}")
            return None

    def cari_artikel_by_slug(self, slug):
        if self.df is None or self.df.empty:
            print("⚠️ Data belum dimuat atau kosong. Panggil .ambil_data() dulu.")
            return None
        try:
            self.df = self.df.iloc[:, :9]
            hasil = self.df[self.df['slug'].astype(str).str.lower() == slug.lower()]
            if hasil.empty:
                print(f"🔍 Artikel dengan slug '{slug}' tidak ditemukan.")
                return None
            return hasil.to_dict(orient="records")[0]  # return satu artikel (pertama)
        except Exception as e:
            print(f"❌ Terjadi kesalahan saat mencari slug: {e}")
            return None
    
    def get_artikel_by_category(self, category_yang_dicari, page=1, per_page=10):
        if self.df is None or self.df.empty:
            print("⚠️ Data belum dimuat atau kosong. Panggil .ambil_data() dulu.")
            return None
        try:
            self.df = self.df.iloc[:, :9]  # Batasi kolom sampai kolom I
            self.df['category'] = self.df['category'].astype(str).str.lower()
            category_yang_dicari = category_yang_dicari.lower().strip()

            # Pastikan kolom 'date' dalam format datetime
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
            today = pd.Timestamp.now()
            self.df = self.df[self.df['date'] <= today]

            # Filter berdasarkan category (case-insensitive, pisah koma)
            hasil = self.df[self.df['category'].str.contains(rf'\b{category_yang_dicari}\b', regex=True)]

            if hasil.empty:
                print(f"🔍 Tidak ada artikel dengan kategori '{category_yang_dicari}'.")
                return None

            hasil = hasil.sort_values(by='date', ascending=False)

            total_artikel = len(hasil)
            total_halaman = math.ceil(total_artikel / per_page)
            page = max(1, min(page, total_halaman))  # Hindari page invalid

            start = (page - 1) * per_page
            end = start + per_page
            paginated_df = hasil.iloc[start:end]

            return {
                "pagination": {
                    "halaman_sekarang": page,
                    "total_artikel": total_artikel,
                    "total_halaman": total_halaman,
                },
                "artikel": paginated_df.to_dict(orient="records")
            }

        except Exception as e:
            print(f"❌ Terjadi kesalahan saat mencari category dengan pagination: {e}")
            return None




# Buat instance
sheet = ArtikelSheet(
    sheet_id="1ihJgwluS40Ekr_0vA8ntltn2f6HWqBaax3RDoHHOt7k",
    gid="710523043"
)

# Ambil datanya
sheet.ambil_data()

# Ambil artikel ke-12 (baris ke-11 karena index mulai dari 0)
artikel = sheet.get_artikel_by_category("bisnis")
print(artikel)