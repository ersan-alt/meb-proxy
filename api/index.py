from flask import Flask, request, Response
import urllib.request
from urllib.parse import urljoin
import re

app = Flask(__name__)

INJECTED_HEAD = '''
<div id="proxy-top-bar" style="position: fixed; top: 0; left: 0; width: 100%; background: #0f172a; color: white; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; z-index: 999999; font-family: Arial, sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.5); border-bottom: 2px solid #38bdf8;">
    <span style="font-weight: bold; font-size: 14px; color: #38bdf8;">🛡️ MEB Tam Koruma</span>
    <form action="/proxy" method="get" style="display: flex; gap: 8px; margin: 0; flex-grow: 1; max-width: 650px; margin-left: 20px; margin-right: 20px;">
        <input type="text" name="url" placeholder="Oyun veya site adresi yazın..." style="flex-grow: 1; padding: 7px 12px; border-radius: 6px; border: 1px solid #475569; background: #1e293b; color: white; font-size: 13px;" required>
        <button type="submit" style="background: #2563eb; color: white; border: none; padding: 7px 18px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px;">Git</button>
    </form>
    <a href="/" style="color: #f87171; text-decoration: none; font-size: 13px; font-weight: bold; background: rgba(248,113,113,0.1); padding: 5px 10px; border-radius: 4px;">Ana Sayfa</a>
</div>
<div style="height: 50px;"></div>

<script>
document.addEventListener('click', function(e) {
    let target = e.target.closest('a');
    if (target && target.href) {
        let href = target.getAttribute('href');
        if (href && !href.startsWith('javascript:') && !href.startsWith('#') && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
            if (!href.includes('/proxy?url=')) {
                e.preventDefault();
                let absoluteUrl = new URL(href, window.location.href).href;
                window.location.href = '/proxy?url=' + encodeURIComponent(absoluteUrl);
            }
        }
    }
}, true);
</script>
'''

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>MEB Tam Korumalı Erişim Geçidi</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #090d16; color: #f1f5f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #111827; padding: 40px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 100%; max-width: 480px; text-align: center; border: 1px solid #1f2937; }
            h2 { margin-bottom: 10px; color: #38bdf8; font-size: 24px; }
            p { color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
            input[type="text"] { width: 100%; padding: 14px; margin-bottom: 15px; border: 1px solid #374151; background: #1f2937; color: white; border-radius: 8px; box-sizing: border-box; font-size: 15px; outline: none; }
            input[type="text"]:focus { border-color: #38bdf8; }
            button { width: 100%; background: #2563eb; color: white; padding: 14px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; transition: background 0.2s; }
            button:hover { background: #1d4ed8; }
            .badge { display: inline-block; background: rgba(56, 189, 248, 0.1); color: #38bdf8; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 20px; border: 1px solid rgba(56, 189, 248, 0.2); }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="badge">🚀 Tam Koruma Aktif</div>
            <h2>Erişim Geçidi</h2>
            <p>Engelsiz web ve oyun deneyimi için adresi yazın.</p>
            <form action="/proxy" method="get">
                <input type="text" name="url" placeholder="https://ornek.com" required>
                <button type="submit">Bağlan</button>
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

    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': target_url
    }
    
    try:
        req = urllib.request.Request(target_url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read()
            status_code = resp.status
            resp_headers = dict(resp.headers.items())
            
            content_type = resp_headers.get('Content-Type', '')

            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'content-security-policy', 'connection']
            headers_list = [(name, value) for name, value in resp_headers.items() if name.lower() not in excluded_headers]

            if 'text/html' in content_type:
                html = body.decode('utf-8', errors='ignore')
                
                def rewrite_url(match):
                    attr = match.group(1)
                    quote = match.group(2)
                    original_link = match.group(3)
                    
                    if original_link.startswith(('javascript:', 'mailto:', '#', 'data:', 'tel:')):
                        return f'{attr}={quote}{original_link}{quote}'
                    
                    full_url = urljoin(target_url, original_link)
                    proxied_url = f'/proxy?url={full_url}'
                    return f'{attr}={quote}{proxied_url}{quote}'

                pattern = re.compile(r'(href|src|action|srcset)=(["\'])(.*?)\2', re.IGNORECASE)
                modified_html = pattern.sub(rewrite_url, html)
                
                if '<head>' in modified_html.lower():
                    modified_html = re.sub(r'<head>', r'<head>' + INJECTED_HEAD, modified_html, count=1, flags=re.IGNORECASE)
                elif '<body' in modified_html.lower():
                    modified_html = re.sub(r'<body[^>]*>', lambda m: m.group(0) + INJECTED_HEAD, modified_html, count=1, flags=re.IGNORECASE)
                else:
                    modified_html = INJECTED_HEAD + modified_html

                return Response(modified_html, status_code, headers_list)
            
            return Response(body, status_code, headers_list)
            
    except Exception as e:
        return f"Bağlantı hatası veya hedef site engeli: {str(e)}", 500
