# ==============================================================================
# MODÜL: ULeader Arka Plan Tünel ve Koruma Motoru (proxy.py)
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

IFRAME_INJECTED_HEAD = '''
<script>
try {
    Object.defineProperty(window, 'top', { get: function() { return window; }, configurable: true });
    Object.defineProperty(window, 'parent', { get: function() { return window; }, configurable: true });
    Object.defineProperty(window, 'frameElement', { get: function() { return null; }, configurable: true });
} catch(e) {}

(function() {
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

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
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
                    if '<head>' in modified_content.lower():
                        modified_content = re.sub(r'<head>', r'<head>' + IFRAME_INJECTED_HEAD, modified_content, count=1, flags=re.IGNORECASE)
                    else:
                        modified_content = IFRAME_INJECTED_HEAD + modified_content

                return Response(modified_content, status_code, headers_list)
            
            return Response(body, status_code, headers_list)
            
    except Exception as e:
        return f"Ağ geçidi bağlantı hatası: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
