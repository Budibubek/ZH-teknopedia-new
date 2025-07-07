from flask import Flask, request
from flask import jsonify, render_template
from bs4 import BeautifulSoup
import requests
from flask import request
import math
import pandas as pd
url = 'https://zh.wikipedia.org/'

class Scrape():
    def __init__(self):
        self._endpoint = url
    
    def set_url(self, url):
        self._endpoint = url
    
    def get_content(self):
        response = requests.get(self._endpoint)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.prettify()
        else:
            return 'Failed to retrieve content'
    def get_conent(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.content, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            title = soup.find('title').text if soup.find('title') else 'No title found'
            title = title.replace(' - Wikipedia bahasa Indonesia, ensiklopedia bebas', ' - Teknopedia ')
            title = title.replace('wikipedia', 'Teknopedia')
            if og_image:
                    return {
                'image': og_image['content'],
                'title': title,
                'url':url
            }
                    
            else:
                return {
                'image': False,
                'title': title,
                'url':url
                }
        else:
            return False
    def get_content_full(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.content, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            content_container = soup.find(id='mw-content-text')
            # content = content_container.prettify() if content_container else 'No content found'
            if content_container:
                elements_to_remove = [
                    ('table', 'plainlinks ombox ombox-protection'),
                    ('table', 'presentation'),
                    ('div', 'bgwiki'),
                    ('div', 'noprint'),
                    ('div', 'printfooter'),
                    ('div', 'metadata i-tooltip'),
                    ('div', 'metadata r-tooltip'),
                    ('div', 'metadata s-tooltip'),
                    ('span', 'mw-editsection'),
                    ('table', 'box-Very_long plainlinks metadata ambox ambox-style ambox-very_long'),
                    ('table', 'box-Tanpa_referensi plainlinks metadata ambox ambox-content ambox-Refimprove'),
                    ('table', 'plainlinks metadata ambox ambox-style'),
                    ('table', 'box-Periksa_terjemahan plainlinks metadata ambox ambox-content ambox-rough_translation'),
                    ('table', 'box-Tambah_referensi plainlinks metadata ambox ambox-content ambox-Refimprove'),
                    ('table', 'box-Kembangkan_bagian plainlinks metadata ambox mbox-small-left ambox-content'),
                    ('table', 'box-Unreliable_sources plainlinks metadata ambox ambox-content ambox-unreliable_sources'),
                    ('table', 'nowraplinks'),
                    ('div', 'nomobile mp-header'),
                    ('div', 'mp-footer'),
                    ('div', 'side-box side-box-right plainlinks sistersitebox')
                ]
                for tag, class_name in elements_to_remove:
                    for element in content_container.find_all(tag, class_=class_name):
                        element.decompose()

                content = content_container.prettify()
            else:
                content = 'No content found'
            title = soup.find('title').text if soup.find('title') else 'No title found'
            title = title.replace(' - Wikipedia bahasa Indonesia, ensiklopedia bebas', ' - Teknopedia ')
            title = title.replace('wikipedia', 'Teknopedia')
            if og_image:
                    return {
                'image': og_image['content'],
                'title': title,
                'url':url,
                'content':content
            }
                    
            else:
                return {
                'image': False,
                'title': title,
                'url':url,
                'content':content
                }
        else:
            return False


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



app = Flask(__name__)
config_artikel = Scrape()


@app.route('/')
def home():
    return render_template('home.html')
@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/artikel', methods=['GET'])
def list_artikel():
    sheet_id = request.args.get('sheet_id')
    gid = request.args.get('gid')
    if not sheet_id or not gid:
        return jsonify({"error": "sheet_id and gid are required"}), 500
  

    artikel_sheet = ArtikelSheet(sheet_id, gid)
    artikel_sheet.ambil_data()
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        data = artikel_sheet.get_artikel_paginated(page, limit)
        return jsonify({    
            "payload": data,
            "status": "success",
            "message": "Data berhasil diambil"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/artikel/detail', methods=['GET'])
def detail_artikel():
    data = request.get_json()
    if not data or 'sheet_id' not in data or 'gid' not in data:
        return jsonify({"error": "sheet_id and gid are required"}), 500
    
    slug = request.args.get('slug')
    if not slug:
        return jsonify({"error": "slug parameter is required"}), 400

    artikel_sheet = ArtikelSheet(data['sheet_id'], data['gid'])
    artikel_sheet.ambil_data()
    
    try:
        artikel = artikel_sheet.cari_artikel_by_slug(slug)
        if artikel:
            return jsonify({
                "payload": artikel,
                "status": "success",
                "message": f"Artikel dengan slug '{slug}' ditemukan"
            })
        else:
            return jsonify({
                "payload": None,
                "status": "error",
                "message": f"Artikel dengan slug '{slug}' tidak ditemukan"
            }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/artikel/category', methods=['GET'])
def artikel_by_category():
   
    sheet_id = request.args.get('sheet_id')
    gid = request.args.get('gid')
    category = request.args.get('category')
    if not sheet_id or not gid or not category:
      return jsonify({"error": "sheet_id, gid, and category are required"}), 500

    artikel_sheet = ArtikelSheet(sheet_id, gid)
    artikel_sheet.ambil_data()
    try:
      page = int(request.args.get('page', 1))
      limit = int(request.args.get('limit', 10))
      data = artikel_sheet.get_artikel_by_category(category, page, limit)
      if data:
        return jsonify({
          "payload": data,
          "status": "success",
          "message": f"Artikel dengan kategori '{category}' berhasil diambil"
        })
      else:
        return jsonify({
          "payload": None,
          "status": "error",
          "message": f"Tidak ada artikel dengan kategori '{category}'"
        }), 404
    except Exception as e:
      return jsonify({"error": str(e)}), 500
        
def get_category_terbanyak(self, top_n=10):
        if self.df is None or self.df.empty:
            print("⚠️ Data belum dimuat atau kosong. Panggil .ambil_data() dulu.")
            return None
        try:
            self.df['category'] = self.df['category'].astype(str).str.lower()
            kategori_terpisah = self.df['category'].str.split(',')

            # Flatten list kategori
            semua_kategori = kategori_terpisah.explode().str.strip()
            jumlah_per_kategori = semua_kategori.value_counts().head(top_n)

            hasil = [
                {"category": kategori, "jumlah_artikel": jumlah}
                for kategori, jumlah in jumlah_per_kategori.items()
            ]
            return hasil

        except Exception as e:
            print(f"❌ Terjadi kesalahan saat mengambil kategori terbanyak: {e}")
            return None
        
    
@app.route('/about')
def about():
    return 'About'

@app.route('/artikel/category-terbanyak', methods=['GET'])
def category_terbanyak():
        sheet_id = request.args.get('sheet_id')
        gid = request.args.get('gid')
        
        top_n = int(request.args.get('top', 10))  # Default to top 10 categories

        if not sheet_id or not gid:
            return jsonify({"error": "sheet_id and gid are required"}), 500

        artikel_sheet = ArtikelSheet(sheet_id, gid)
        artikel_sheet.ambil_data()

        try:
            data = artikel_sheet.get_category_terbanyak(top_n)
            if data:
                return jsonify({
                    "payload": data,
                    "status": "success",
                    "message": "Kategori terbanyak berhasil diambil"
                })
            else:
                return jsonify({
                    "payload": None,
                    "status": "error",
                    "message": "Tidak ada kategori yang ditemukan"
                }), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
@app.route('/portal')
def portal_artikel():
    max_links = request.args.get('max', default=1, type=int)
    
    config_artikel.set_url('https://id.wikipedia.org/wiki/Portal:Teknologi')
    artikel = config_artikel.get_content()
    soup = BeautifulSoup(artikel, 'html.parser')
    content_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
    tables = content_div.find('table', class_=False) if content_div else []
    links = tables.find_all('a') if tables else []
    links = [link.get('href') for link in links if link.get('href') and '/wiki/Portal:' in link.get('href')]
    links = list(dict.fromkeys(links))  # Remove duplicates while preserving order
    links = {index: {'link': link} for index, link in enumerate(links)}
    for key, value in links.items():
        enpoint = url + value['link']
        print(enpoint)
        amcor_portal = value['link']
        amcor_portal = amcor_portal.replace('/wiki/','')
        links[key]['ancor'] = amcor_portal
        artikel_links = get_link(enpoint, max_links)
        links[key]['artikel'] = {}
        for key2, value2 in artikel_links.items():
            enpoint2 = url + value2
            print(enpoint2)
            links[key]['artikel'][key2] = config_artikel.get_conent(enpoint2)
            links[key]['artikel'][key2]['url'] = value2.replace('/wiki/', '')
        
    
    data = {
        'payload':{"Portal": links}
    }
    return jsonify(data)

def get_link(param, max_links=5):
    config_artikel.set_url(param)
    artikel = config_artikel.get_content()
    soup = BeautifulSoup(artikel, 'html.parser')
    links = soup.find_all('a')
    
    links = [link.get('href') for link in links if link.get('href') and '/wiki/' in link.get('href')]
    exclusions = [
        'Portal',
        'http',
        'Halaman_Utama',
        'Wikipedia',
        'Halaman_sembarang',
        'Bahasa_Indonesia',
        'Ensiklopedia',
        ':',
        'Berkas:Kitagawa_Utamaro'
    ]
    links = [link for link in links if all(exclusion not in link for exclusion in exclusions)]    
    links = list(dict.fromkeys(links))  # Remove duplicates while preserving order
    links = links[:max_links]  # Take only the first max_links links
    links = {index: link for index, link in enumerate(links)}  
    
    data = {
        'links': links
    }
    return links


    
@app.route('/home-page')
def home_page():
    max_links = request.args.get('max', default=1, type=int)
    def extract_links(enpoint):
        config_artikel.set_url(enpoint)
        artikel = config_artikel.get_content()        
        soup = BeautifulSoup(artikel, 'html.parser')
        links = soup.find_all('a')
        exclusions = ['Halaman_Utama', 'Wikipedia', 'Halaman_sembarang', 'Bahasa_Indonesia', 'Ensiklopedia', 'Berkas:Kitagawa_Utamaro']
        links = [link.get('href') for link in links if link.get('href') and '/wiki/' in link.get('href') and not link.get('href').startswith('https') and all(exclusion not in link.get('href') for exclusion in exclusions)]
        links = list(dict.fromkeys(links))  # Remove duplicates while preserving order
        links = {index: link for index, link in enumerate(links)}
        return links
    def get_links(enpoint):
        config_artikel.set_url(enpoint)
        artikel = config_artikel.get_content()        
        soup = BeautifulSoup(artikel, 'html.parser')
        content_container = soup.find(id='mw-content-text')
        links = content_container.find_all('a') if content_container else []
        exclusions = ['Halaman_Utama','Templat:', 'Wikipedia', 'Halaman_sembarang', 'Portal:', 'Ensiklopedia', 'Berkas:','Kategori:','Bantuan:', 'Istimewa:']
        links = [link.get('href') for link in links if link.get('href') and '/wiki/' in link.get('href') and not link.get('href').startswith('https') and all(exclusion not in link.get('href') for exclusion in exclusions)]
        links = list(dict.fromkeys(links))  # Remove duplicates while preserving order
        links = links[:max_links]  # Take only the first 10 links
        links = {index: link for index, link in enumerate(links)}
        return links
    links = extract_links(url)
    portal_links = [value for value in links.values() if '/wiki/Portal:' in value]
    portal_links = list(dict.fromkeys(portal_links))  # Remove duplicates while preserving order
    portal_links = {index: {'link': link} for index, link in enumerate(portal_links)}
    
    for key, value in portal_links.items():
        enpoint = url + value['link']
        ancor_portal = value['link']
        ancor_portal = ancor_portal.replace('/wiki/','')
        portal_links[key]['ancor'] = ancor_portal
        portal_links[key]['artikel'] = get_links(enpoint)       
        # print(value['link'])
        for key2, value2 in portal_links[key]['artikel'].items():
            scrape = url + value2
            url_get = config_artikel.get_conent(scrape)
            portal_links[key]['artikel'][key2] = url_get
            link = value2.replace('/wiki/', '')
            
            portal_links[key]['artikel'][key2]['url'] = link
            portal_links[key]['artikel'][key2]['enpoint'] = url + value2          
    
        
    
    data = {
        'payload': {
            'Portal': portal_links,
        }
    }
    return jsonify(data)

@app.route('/get-content')
def get_content():
    param = request.args.get('url')
    enpoint = url + param    
    config_artikel.set_url(enpoint)
    content = config_artikel.get_content_full(enpoint)
    data = {
        'payload':{
            'enpoint':enpoint,
            'data':content
        }
    }
    return data


    
if __name__ == '__main__':
    app.run(port=5000, debug=True)
