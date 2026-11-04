from flask import Flask, request, Response
import requests
from urllib.parse import urljoin, urlparse
import re

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>MEB Erişim Geçidi - Vercel</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; background-color: #f4f4f9; color: #333; }
            .container { background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 500px; }
            input[type="text"] { width: 100%; padding: 10px; margin-top: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background-color: #0056b3; }
            #status-box { margin-top: 20px; padding: 15px; border-radius: 4px; background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>MEB Erişim Geçidi (Vercel)</h2>
            <div id="status-box">✅ Otomatik Link Yönlendirme Aktif!</div>
            
            <form action="/proxy" method="get" style="margin-top: 20px;">
                <label for="url">Gitmek İstediğiniz Adres:</label>
                <input type="text" id="url" name="url" placeholder="https://www.ornek.com" required>
                <button type="submit">Git</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "Lütfen bir URL belirtin.", 400
    
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'https://' + target_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(target_url, headers=headers, timeout=12)
        content_type = resp.headers.get('Content-Type', '')

        # Eğer gelen içerik HTML ise linkleri proxy üzerinden geçecek şekilde güncelle
        if 'text/html' in content_type:
            html = resp.text
            
            # href, src ve action parametrelerindeki tüm yönlendirmeleri yakala ve proxy uzantısına çevir
            def rewrite_url(match):
                attr = match.group(1)
                quote = match.group(2)
                original_link = match.group(3)
                
                if original_link.startswith(('javascript:', 'mailto:', '#', 'data:')):
                    return f'{attr}={quote}{original_link}{quote}'
                
                full_url = urljoin(target_url, original_link)
                proxied_url = f'/proxy?url={full_url}'
                return f'{attr}={quote}{proxied_url}{quote}'

            pattern = re.compile(r'(href|src|action)=(["\'])(.*?)\2', re.IGNORECASE)
            modified_html = pattern.sub(rewrite_url, html)
            
            return Response(modified_html, resp.status_code, [(k, v) for k, v in resp.headers.items() if k.lower() not in ['content-encoding', 'content-length', 'transfer-encoding']])
        
        # HTML dışındaki dosya ve içerikleri (resim, video akışı vs.) doğrudan ilet
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers_list = [(name, value) for name, value in resp.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers_list)
            
    except Exception as e:
        return f"Bağlantı hatası oluştu: {str(e)}", 500
