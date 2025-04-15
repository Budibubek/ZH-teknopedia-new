from flask import Flask
from flask import jsonify
from bs4 import BeautifulSoup
import requests
from flask import request
import json

url = 'https://id.wikipedia.org/'
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
            title = title.replace(' - Wikipedia bahasa Indonesia, ensiklopedia bebas', ' - Ensiklopedia ')
            title = title.replace('wikipedia', 'Ensiklopedia')
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
                    ('table', 'box-Unreliable_sources plainlinks metadata ambox ambox-content ambox-unreliable_sources'),
                    ('div', 'side-box side-box-right plainlinks sistersitebox')
                ]
                for tag, class_name in elements_to_remove:
                    for element in content_container.find_all(tag, class_=class_name):
                        element.decompose()
                
                content = content_container.prettify()
            else:
                content = 'No content found'
            title = soup.find('title').text if soup.find('title') else 'No title found'
            title = title.replace(' - Wikipedia bahasa Indonesia, ensiklopedia bebas', ' - Ensiklopedia ')
            title = title.replace('wikipedia', 'Ensiklopedia')
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

app = Flask(__name__)
config_artikel = Scrape()

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

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
    enpoint = url + '/wiki/' + param
    enpoint = enpoint.replace('.html', '')
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