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
            self.df = pd.read_csv(self.url, skiprows=10)
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
            total_artikel = len(self.df)
            total_halaman = math.ceil(total_artikel / per_page)
            page = max(1, min(page, total_halaman))  # hindari halaman invalid

            start = (page - 1) * per_page
            end = start + per_page
            paginated_df = self.df.iloc[start:end]

            return {
                "halaman_sekarang": page,
                "total_artikel": total_artikel,
                "total_halaman": total_halaman,
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
            hasil = self.df[self.df['slug'].astype(str).str.lower() == slug.lower()]
            if hasil.empty:
                print(f"🔍 Artikel dengan slug '{slug}' tidak ditemukan.")
                return None
            return hasil.to_dict(orient="records")[0]  # return satu artikel (pertama)
        except Exception as e:
            print(f"❌ Terjadi kesalahan saat mencari slug: {e}")
            return None



# Buat instance
sheet = ArtikelSheet(
    sheet_id="1SkXjSTwoKLWmIgRccg30hbZruBBi1kwgIL3tsVOZX6I",
    gid="854406851"
)

# Ambil datanya
sheet.ambil_data()

# Ambil artikel ke-12 (baris ke-11 karena index mulai dari 0)
artikel = sheet.get_artikel_paginated()
print(artikel)
for a in artikel['artikel']:
    print(a['slug'])