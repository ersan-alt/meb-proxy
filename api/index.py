# ==============================================================================
# PROJE: ULeader Akademik Eğitim Notları ve Güvenli Arşiv Geçidi (Ultimate v23.0)
# AÇIKLAMA: window.open ve Popup Engelleme/Tünele Kilitleme Motoru
# ==============================================================================

from flask import Flask, request, Response
import urllib.request
import urllib.error
import http.cookiejar
from urllib.parse import urljoin, urlparse
import re

app = Flask(__name__)

cookie_jar = http.cookiejar.CookieJar()
cookie_handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(cookie_handler)
urllib.request.install_opener(opener)

def is_meb_bot(user_agent):
    if not user_agent:
        return True
    bot_keywords = ['bot', 'crawler', 'spider', 'fortinet', 'fortiguard', 'cisco', 'zscaler', 'slurp', 'headless', 'netscaler']
    return any(keyword in user_agent.lower() for keyword in bot_keywords)

FAKE_EDUCATION_PAGE = '''<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><title>Anadolu Selçuklu Devleti Dönemi Mimari Yapıları</title></head>
<body style="font-family: Arial, sans-serif; padding: 40px; background: #f8fafc; color: #222;">
    <div style="max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <h1 style="color: #1e3a8a;">Anadolu Selçuklu Devleti Siyasi ve Kültürel Tarihi</h1>
        <p>Bu akademik çalışma MEB standartlarına uygundur.</p>
    </div>
</body>
</html>'''

MAIN_INJECTED_HEAD = '''
<div id="proxy-top-bar" style="position: fixed; top: 0; left: 0; width: 100%; background: #0f172a; color: white; padding: 8px 15px; display: flex; justify-content: space-between; align-items: center; z-index: 2147483647; font-family: Arial, sans-serif; box-shadow: 0 4px 15px rgba(0,0,0,0.7); border-bottom: 2px solid #38bdf8;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">📚 Eğitim Arşivi</span>
        <span style="font-size: 12px; color: #94a3b8;">Üniversal Oyun Tüneli Aktif</span>
    </div>
    <form action="/proxy" method="get" style="display: flex; gap: 6px; margin: 0; flex-grow: 1; max-width: 550px; margin-left: 15px; margin-right: 15px;">
        <input type="text" name="url" placeholder="Poki, CrazyGames, Y8 veya site adresi yazın..." style="flex-grow: 1; padding: 6px 10px; border-radius: 4px; border: 1px solid #475569; background: #1e293b; color: white; font-size: 12px; outline: none;" required>
        <button type="submit" style="background: #2563eb; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;">Getir</button>
    </form>
    <div>
        <a href="/" style="color: #f87171; text-decoration: none; font-size: 12px; font-weight: bold; background: rgba(248,113,113,0.1); padding: 5px 10px; border-radius: 4px;">Ana Sayfa</a>
    </div>
</div>
<div style="height: 45px;"></div>

<script>
try {
    Object.defineProperty(navigator, 'webdriver', { get: function() { return false; }, configurable: true });
    Object.defineProperty(navigator, 'plugins', { get: function() { return [1, 2, 3, 4, 5]; }, configurable: true });
    window.console.error = window.console.error || function() {};
} catch(e) {}

(function() {
    // 1. WINDOW.OPEN HOOK (Oyunların yeni sekme açma girişimlerini tünele kilitler)
    const nativeWindowOpen = window.open;
    window.open = function(url, target, features) {
        if (url) {
            if (url.startsWith('//')) url = 'https:' + url;
            try {
                let absUrl = new URL(url, window.location.href).href;
                url = '/proxy?url=' + encodeURIComponent(absUrl);
            } catch(e) {}
            window.location.href = url;
        }
        return null;
    };

    // 2. Tüm tıklama ve yönlendirmeleri proxy tüneline kilitleme
    document.addEventListener('click', function(e) {
        let targetLink = e.target.closest('a, [data-url], [data-href]');
        if (targetLink) {
            let hrefVal = targetLink.getAttribute('href') || targetLink.getAttribute('data-url') || targetLink.getAttribute('data-href');
            if (hrefVal && !hrefVal.startsWith('javascript:') && !hrefVal.startsWith('#') && !hrefVal.startsWith('mailto:') && !hrefVal.startsWith('tel:') && !hrefVal.startsWith('data:')) {
                if (!hrefVal.includes('/proxy?url=')) {
                    e.preventDefault();
                    if (hrefVal.startsWith('//')) hrefVal = 'https:' + hrefVal;
                    try {
                        let fullDest = new URL(hrefVal, window.location.href).href;
                        window.location.href = '/proxy?url=' + encodeURIComponent(fullDest);
                    } catch(err) {
                        window.location.href = hrefVal;
                    }
                }
            }
        }
    }, true);

    // 3. Dinamik Iframe Yakalayıcı
    const origCreateElement = document.createElement;
    document.createElement = function(tagName) {
        const el = origCreateElement.call(document, tagName);
        if (tagName.toLowerCase() === 'iframe') {
            const origSetAttribute = el.setAttribute;
            el.setAttribute = function(name, val) {
                if (name.toLowerCase() === 'src' && val && !val.startsWith('data:') && !val.includes('/proxy?url=')) {
                    if (val.startsWith('//')) val = 'https:' + val;
                    try {
                        let abs = new URL(val, window.location.href).href;
                        val = '/proxy?url=' + encodeURIComponent(abs);
                    } catch(e) {}
                }
                return origSetAttribute.call(this, name, val);
            };
        }
        return el;
    };

    // 4. Fetch ve XHR İstekleri Tünelleme
    const nativeFetch = window.fetch;
    window.fetch = function(resource, init) {
        let reqUrl = resource instanceof Request ? resource.url : resource;
        if (typeof reqUrl === 'string' && !reqUrl.startsWith('data:') && !reqUrl.includes('/proxy?url=')) {
            if (reqUrl.startsWith('//')) reqUrl = 'https:' + reqUrl;
            try {
                let absoluteTarget = new URL(reqUrl, window.location.href).href;
                let proxiedTarget = '/proxy?url=' + encodeURIComponent(absoluteTarget);
                resource = resource instanceof Request ? new Request(proxiedTarget, init) : proxiedTarget;
            } catch(e) {}
        }
        return nativeFetch.call(this, resource, init);
    };

    const nativeOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        if (typeof url === 'string' && !url.startsWith('data:') && !url.includes('/proxy?url=')) {
            if (url.startsWith('//')) url = 'https:' + url;
            try {
                arguments[1] = '/proxy?url=' + encodeURIComponent(new URL(url, window.location.href).href);
            } catch(e) {}
        }
        return nativeOpen.apply(this, arguments);
    };
})();
</script>
'''

IFRAME_INJECTED_HEAD = '''
<script>
(function() {
    const nativeWindowOpen = window.open;
    window.open = function(url, target, features) {
        if (url) {
            if (url.startsWith('//')) url = 'https:' + url;
            try {
                let absUrl = new URL(url, window.location.href).href;
                url = '/proxy?url=' + encodeURIComponent(absUrl);
            } catch(e) {}
            window.location.href = url;
        }
        return null;
    };

    document.addEventListener('click', function(e) {
        let targetLink = e.target.closest('a, [data-url], [data-href]');
        if (targetLink) {
            let hrefVal = targetLink.getAttribute('href') || targetLink.getAttribute('data-url') || targetLink.getAttribute('data-href');
            if (hrefVal && !hrefVal.startsWith('javascript:') && !hrefVal.startsWith('#') && !hrefVal.startsWith('data:')) {
                if (!hrefVal.includes('/proxy?url=')) {
                    e.preventDefault();
                    if (hrefVal.startsWith('//')) hrefVal = 'https:' + hrefVal;
                    try {
                        let fullDest = new URL(hrefVal, window.location.href).href;
                        window.location.href = '/proxy?url=' + encodeURIComponent(fullDest);
                    } catch(err) {}
                }
            }
        }
    }, true);

    const nativeFetch = window.fetch;
    window.fetch = function(resource, init) {
        let reqUrl = resource instanceof Request ? resource.url : resource;
        if (typeof reqUrl === 'string' && !reqUrl.startsWith('data:') && !reqUrl.includes('/proxy?url=')) {
            if (reqUrl.startsWith('//')) reqUrl = 'https:' + reqUrl;
            try {
                let absoluteTarget = new URL(reqUrl, window.location.href).href;
                let proxiedTarget = '/proxy?url=' + encodeURIComponent(absoluteTarget);
                resource = resource instanceof Request ? new Request(proxiedTarget, init) : proxiedTarget;
            } catch(e) {}
        }
        return nativeFetch.call(this, resource, init);
    };
})();
</script>
'''

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '')
    if is_meb_bot(user_agent):
        return FAKE_EDUCATION_PAGE
        
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>ULeader Dijital Eğitim Notları ve Dosya Depolama Sistemi</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f1f5f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #111827; padding: 40px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); width: 100%; max-width: 480px; text-align: center; border: 1px solid #1f2937; }
            h2 { margin-bottom: 10px; color: #38bdf8; font-size: 22px; }
            p { color: #94a3b8; font-size: 13px; margin-bottom: 25px; }
            input[type="text"] { width: 100%; padding: 14px; margin-bottom: 15px; border: 1px solid #374151; background: #1f2937; color: white; border-radius: 8px; box-sizing: border-box; font-size: 14px; outline: none; }
            input[type="text"]:focus { border-color: #38bdf8; }
            button { width: 100%; background: #2563eb; color: white; padding: 14px; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: bold; transition: background 0.2s; }
            button:hover { background: #1d4ed8; }
            .badge { display: inline-block; background: rgba(56, 189, 248, 0.1); color: #38bdf8; padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; margin-bottom: 20px; border: 1px solid rgba(56, 189, 248, 0.2); }
            .hint { font-size: 11px; color: #64748b; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="badge">📖 Akademik Arşiv ve Dosya Yönetimi</div>
            <h2>Erişim ve Depo Geçidi</h2>
            <p>Eğitim materyalleri, kaynaklar ve oyunlar için adresi girin.</p>
            <form action="/proxy" method="get">
                <input type="text" name="url" placeholder="https://poki.com" required>
                <button type="submit">Sisteme Bağlan</button>
            </form>
            <div class="hint">Tam korumalı tünel ve bot engelleme katmanı aktiftir.</div>
        </div>
    </body>
    </html>
    '''

@app.route('/proxy', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy():
    if request.method == 'OPTIONS':
        resp = Response('', status=200)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = '*'
        return resp

    user_agent = request.headers.get('User-Agent', '')
    if is_meb_bot(user_agent):
        return FAKE_EDUCATION_PAGE
        
    target_url = request.args.get('url')
    if not target_url:
        return "URL belirtilmedi.", 400
    
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'https://' + target_url

    parsed_target = urlparse(target_url)
    target_origin = f"{parsed_target.scheme}://{parsed_target.netloc}"

    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'identity',
        'Cache-Control': 'no-cache',
        'Referer': target_origin + '/',
        'Origin': target_origin
    }
    
    for h_key, h_val in request.headers:
        if h_key.lower() not in ['host', 'content-length', 'connection', 'accept-encoding']:
            req_headers[h_key] = h_val

    request_data = request.get_data() if request.method in ['POST', 'PUT', 'PATCH'] else None

    try:
        req = urllib.request.Request(target_url, data=request_data, headers=req_headers, method=request.method)
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            status_code = resp.status
            resp_headers = dict(resp.headers.items())
            
            content_type = resp_headers.get('Content-Type', '').lower()
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'content-security-policy', 'connection', 'x-frame-options']
            headers_list = [(name, value) for name, value in resp_headers.items() if name.lower() not in excluded_headers]
            
            headers_list.append(('Access-Control-Allow-Origin', '*'))
            headers_list.append(('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE'))
            headers_list.append(('Access-Control-Allow-Headers', '*'))

            if 'text/html' in content_type or 'text/css' in content_type:
                try:
                    content_str = body.decode('utf-8', errors='ignore')
                except:
                    content_str = body.decode('latin1', errors='ignore')
                
                def rewrite_url(match):
                    attr, quote, orig = match.group(1), match.group(2), match.group(3)
                    if orig.startswith(('javascript:', 'mailto:', '#', 'data:', 'tel:')):
                        return f'{attr}={quote}{orig}{quote}'
                    if orig.startswith('//'):
                        orig = 'https:' + orig
                    return f'{attr}={quote}/proxy?url={urljoin(target_url, orig)}{quote}'

                modified_content = re.compile(r'(href|src|action|srcset|data-src|data-original|poster)=(["\'])(.*?)\2', re.IGNORECASE).sub(rewrite_url, content_str)

                if 'text/html' in content_type:
                    sec_dest = request.headers.get('Sec-Fetch-Dest', '')
                    injection_script = IFRAME_INJECTED_HEAD if sec_dest == 'iframe' else MAIN_INJECTED_HEAD

                    if '<head>' in modified_content.lower():
                        modified_content = re.sub(r'<head>', r'<head>' + injection_script, modified_content, count=1, flags=re.IGNORECASE)
                    else:
                        modified_content = injection_script + modified_content

                return Response(modified_content, status_code, headers_list)
            
            return Response(body, status_code, headers_list)
            
    except Exception as e:
        return f"Ağ geçidi bağlantı hatası: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
