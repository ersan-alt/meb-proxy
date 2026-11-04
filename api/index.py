from flask import Flask, request, Response
import requests
from urllib.parse import urljoin, urlparse
import re

app = Flask(__name__)

# Proxy içindeyken sayfaların üstüne eklenen pratik gezinti çubuğu
TOP_BAR_HTML = b'''
<div id="proxy-top-bar" style="position: fixed; top: 0; left: 0; width: 100%; background: #1a1a1a; color: white; padding: 8px 15px; display: flex; justify-content: space-between; align-items: center; z-index: 999999; font-family: Arial, sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.5);">
    <span style="font-weight: bold; font-size: 14px; color: #00ffcc;">MEB Geçit V2</span>
    <form action="/proxy" method="get" style="display: flex; gap: 8px; margin: 0; flex-grow: 1; max-width: 600px; margin-left: 20px; margin-right: 20px;">
        <input type="text" name="url" placeholder="Adres veya arama yazın..." style="flex-grow: 1; padding: 5px 10px; border-radius: 4px; border: none; font-size: 13px;" required>
        <button type="submit" style="background: #007bff; color: white; border: none; padding: 5px 15px; border-radius: 4px; cursor: pointer; font-weight: bold;">Git</button>
    </form>
    <a href="/" style="color: #ff4d4d; text-decoration: none; font-size: 13px; font-weight: bold;">Ana Sayfa</a>
</div>
<div style="height: 45px;"></div>
'''

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>MEB Üst Düzey Erişim Geçidi</title>
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 100%; max-width: 450px; text-align: center; }
            h2 { margin-bottom: 20px; color: #38bdf8; }
            input[type="text"] { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #475569; background: #0f172a; color: white; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
            button { width: 100%; background: #3b82f6; color: white; padding: 12px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; transition: background 0.2s; }
            button:hover { background: #2563eb; }
            .status { margin-top: 15px; font-size: 13px; color: #4ade80; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Erişim Geçidi V2</h2>
            <div class="status">⚡ Üst Düzey Yönlendirme Aktif</div>
            <form action="/proxy" method="get" style="margin-top: 20px;">
                <input type="text" name="url" placeholder="https://ornek.com" required>
                <button type="submit">Güvenli Bağlan</label>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "URL belirtilmedi.", 400
    
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'https://' + target_url

    # Tarayıcı istek taklidini güçlendir
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': target_url
    }
    
    # Kullanıcıdan gelen çerezleri (cookies) ve yetki başlıklarını hedefe ilet
    incoming_cookies = request.cookies
    
    try:
        resp = requests.get(target_url, headers=headers, cookies=incoming_cookies, allow_redirects=True, timeout=15)
        
        # Eğer hedef site başka bir URL'ye yönlendirdiyse, onu da proxy formatına çevir
        if resp.history:
            final_url = resp.url
            return f'<meta http-equiv="refresh" content="0;url=/proxy?url={final_url}">', 200

        content_type = resp.headers.get('Content-Type', '')

        # HTML içeriklerini akıllıca filtrele ve tüm yolları proxy'ye bağla
        if 'text/html' in content_type:
            html = resp.text
            
            def rewrite_url(match):
                attr = match.group(1)
                quote = match.group(2)
                original_link = match.group(3)
                
                if original_link.startswith(('javascript:', 'mailto:', '#', 'data:', 'tel:')):
                    return f'{attr}={quote}{original_link}{quote}'
                
                full_url = urljoin(target_url, original_link)
                proxied_url = f'/proxy?url={full_url}'
                return f'{attr}={quote}{proxied_url}{quote}'

            # href, src, action ve srcset etiketlerini yakala
            pattern = re.compile(r'(href|src|action|srcset)=(["\'])(.*?)\2', re.IGNORECASE)
            modified_html = pattern.sub(rewrite_url, html)
            
            # Sayfanın en başına yönetim çubuğunu enjekte et
            if b'<body' in modified_html.lower():
                modified_html = re.sub(b'<body[^>]*>', lambda m: m.group(0) + TOP_BAR_HTML, modified_html, count=1, flags=re.IGNORECASE)
            else:
                modified_html = TOP_BAR_HTML.decode('utf-8') + modified_html

            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'content-security-policy']
            headers_list = [(name, value) for name, value in resp.headers.items() if name.lower() not in excluded_headers]
            return Response(modified_html, resp.status_code, headers_list)
        
        # Medya, resim ve diğer dosyaları doğrudan aktar
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'content-security-policy']
        headers_list = [(name, value) for name, value in resp.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers_list)
            
    except Exception as e:
        return f"Bağlantı hatası veya hedef site engeli: {str(e)}", 500
