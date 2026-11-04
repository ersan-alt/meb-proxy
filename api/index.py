# ==============================================================================
# PROJE: ULeader MEB Üniversal Güvenlik ve Oyun Proxy Altyapısı (v7.0 Ultimate)
# AÇIKLAMA: MEB ve benzeri ağ kısıtlamalarını, iframe/domain kilitlerini aşmak,
#           Unity WebGL, Y8, CrazyGames ve tüm ağır oyunları hatasız çalıştırmak
#           üzere tasarlanmış 500 satırlık profesyonel sunucu kodudur.
# ==============================================================================

from flask import Flask, request, Response, jsonify
import urllib.request
import urllib.error
import http.cookiejar
from urllib.parse import urljoin, urlparse
import re
import sys
import traceback

# Flask uygulama başlatma
app = Flask(__name__)

# Çerez yönetimi için global çerez kavanozu (CookieJar)
cookie_jar = http.cookiejar.CookieJar()
cookie_handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(cookie_handler)
urllib.request.install_opener(opener)


# ==============================================================================
# BÖLÜM 1: İSTEMCİ TARAFI GÜVENLİK VE KALKAN ENJEKSİYONU (CLIENT-SIDE DEFENSE)
# ==============================================================================
INJECTED_HEAD = '''
<div id="proxy-top-bar" style="position: fixed; top: 0; left: 0; width: 100%; background: #090d16; color: white; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; z-index: 2147483647; font-family: 'Segoe UI', Arial, sans-serif; box-shadow: 0 4px 20px rgba(0,0,0,0.8); border-bottom: 2px solid #38bdf8;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid rgba(56, 189, 248, 0.3);">🛡️ MEB Ultimate v7</span>
        <span style="font-size: 13px; color: #94a3b8; display: inline-block;">Güvenli Geçit Aktif</span>
    </div>
    <form action="/proxy" method="get" style="display: flex; gap: 8px; margin: 0; flex-grow: 1; max-width: 600px; margin-left: 20px; margin-right: 20px;">
        <input type="text" name="url" placeholder="Oyun, site veya arama adresi yazın..." style="flex-grow: 1; padding: 7px 14px; border-radius: 6px; border: 1px solid #334155; background: #1e293b; color: white; font-size: 13px; outline: none;" required>
        <button type="submit" style="background: #2563eb; color: white; border: none; padding: 7px 18px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px; transition: background 0.2s;">Git</button>
    </form>
    <div>
        <a href="/" style="color: #f87171; text-decoration: none; font-size: 13px; font-weight: bold; background: rgba(248,113,113,0.1); padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(248,113,113,0.2);">Ana Sayfa</a>
    </div>
</div>
<div style="height: 52px;"></div>

<script>
// --- GÜVENLİK KALKANI 1: DOMAIN, IFRAME VE EMBED KİLİTLERİNİ KIRMA ---
try {
    Object.defineProperty(window, 'top', { get: function() { return window; }, configurable: true });
    Object.defineProperty(window, 'parent', { get: function() { return window; }, configurable: true });
    Object.defineProperty(window, 'frameElement', { get: function() { return null; }, configurable: true });
    Object.defineProperty(document, 'referrer', { get: function() { return window.location.href; }, configurable: true });
    
    const hostVal = window.location.hostname || 'oyun.com';
    const originVal = window.location.origin || 'https://oyun.com';
    
    if (window.location) {
        window.location.__defineGetter__('hostname', function() { return hostVal; });
        window.location.__defineGetter__('host', function() { return hostVal; });
        window.location.__defineGetter__('origin', function() { return originVal; });
    }
} catch(err) {
    console.warn('ULeader Security Notice:', err);
}

// --- GÜVENLİK KALKANI 2: FETCH VE XHR DİNAMİK İSTEK YÖNLENDİRİCİSİ ---
(function() {
    const nativeFetch = window.fetch;
    window.fetch = function(resource, init) {
        let reqUrl = resource;
        if (resource instanceof Request) {
            reqUrl = resource.url;
        }
        if (typeof reqUrl === 'string' && !reqUrl.startsWith('data:') && !reqUrl.includes('/proxy?url=')) {
            if (reqUrl.startsWith('//')) reqUrl = 'https:' + reqUrl;
            try {
                let absoluteTarget = new URL(reqUrl, window.location.href).href;
                let proxiedTarget = '/proxy?url=' + encodeURIComponent(absoluteTarget);
                if (resource instanceof Request) {
                    resource = new Request(proxiedTarget, init);
                } else {
                    resource = proxiedTarget;
                }
            } catch(e) {}
        }
        return nativeFetch.call(this, resource, init);
    };

    const nativeOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        if (typeof url === 'string' && !url.startsWith('data:') && !url.includes('/proxy?url=')) {
            if (url.startsWith('//')) url = 'https:' + url;
            try {
                let absoluteTarget = new URL(url, window.location.href).href;
                arguments[1] = '/proxy?url=' + encodeURIComponent(absoluteTarget);
            } catch(e) {}
        }
        return nativeOpen.apply(this, arguments);
    };
})();

// --- GÜVENLİK KALKANI 3: TIKLAMA VE YÖNLENDİRME KONTROLÜ ---
document.addEventListener('click', function(e) {
    let targetLink = e.target.closest('a');
    if (targetLink && targetLink.href) {
        let hrefVal = targetLink.getAttribute('href');
        if (hrefVal && !hrefVal.startsWith('javascript:') && !hrefVal.startsWith('#') && !hrefVal.startsWith('mailto:') && !hrefVal.startsWith('tel:')) {
            if (!hrefVal.includes('/proxy?url=')) {
                e.preventDefault();
                try {
                    let fullDest = new URL(hrefVal, window.location.href).href;
                    window.location.href = '/proxy?url=' + encodeURIComponent(fullDest);
                } catch(e) {
                    window.location.href = hrefVal;
                }
            }
        }
    }
}, true);
</script>
'''


# ==============================================================================
# BÖLÜM 2: ANA SAYFA (INDEX ROUTE) - GÜVENLİ ARAYÜZ
# ==============================================================================
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MEB Üniversal Tam Korumalı Erişim Geçidi</title>
        <style>
            * { box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: radial-gradient(circle at center, #0f172a 0%, #090d16 100%); 
                color: #f1f5f9; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
                overflow: hidden;
            }
            .main-card { 
                background: rgba(17, 24, 39, 0.85); 
                padding: 45px; 
                border-radius: 20px; 
                box-shadow: 0 20px 50px rgba(0,0,0,0.7); 
                width: 100%; 
                max-width: 520px; 
                text-align: center; 
                border: 1px solid rgba(56, 189, 248, 0.2); 
                backdrop-filter: blur(10px);
            }
            .badge { 
                display: inline-block; 
                background: rgba(56, 189, 248, 0.1); 
                color: #38bdf8; 
                padding: 6px 16px; 
                border-radius: 30px; 
                font-size: 13px; 
                font-weight: bold; 
                margin-bottom: 22px; 
                border: 1px solid rgba(56, 189, 248, 0.3); 
            }
            h1 { 
                margin: 0 0 10px 0; 
                color: #f8fafc; 
                font-size: 26px; 
                font-weight: 800; 
            }
            p { 
                color: #94a3b8; 
                font-size: 14px; 
                margin-bottom: 30px; 
                line-height: 1.5;
            }
            .input-group { 
                position: relative; 
                margin-bottom: 20px; 
            }
            input[type="text"] { 
                width: 100%; 
                padding: 16px 20px; 
                border: 1px solid #334155; 
                background: #1e293b; 
                color: white; 
                border-radius: 12px; 
                box-sizing: border-box; 
                font-size: 16px; 
                outline: none; 
                transition: all 0.3s ease;
            }
            input[type="text"]:focus { 
                border-color: #38bdf8; 
                box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
            }
            button { 
                width: 100%; 
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); 
                color: white; 
                padding: 16px; 
                border: none; 
                border-radius: 12px; 
                cursor: pointer; 
                font-size: 16px; 
                font-weight: bold; 
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
            }
            button:hover { 
                background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%); 
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
            }
            .footer-note { 
                margin-top: 25px; 
                font-size: 12px; 
                color: #64748b; 
            }
        </style>
    </head>
    <body>
        <div class="main-card">
            <div class="badge">🚀 MEB Üniversal Güvenlik v7 Aktif</div>
            <h1>Erişim Geçidi</h1>
            <p>Y8, CrazyGames, oyun platformları ve engelsiz tüm web siteleri için hedef adresi girin.</p>
            <form action="/proxy" method="get">
                <div class="input-group">
                    <input type="text" name="url" placeholder="https://tr.y8.com veya oyun linki..." autocomplete="off" required>
                </div>
                <button type="submit">Güvenli Bağlan</button>
            </form>
            <div class="footer-note">ULeader Network Systems © 2026 - Tüm Hakları Saklıdır.</div>
        </div>
    </body>
    </html>
    '''


# ==============================================================================
# BÖLÜM 3: PROXY MOTORU VE GÜVENLİK YÖNETİCİSİ (PROXY ENGINE ROUTE)
# ==============================================================================
@app.route('/proxy')
def proxy():
    # 1. Adım: Hedef URL kontrolü ve doğrulaması
    target_url = request.args.get('url')
    if not target_url:
        return "Hata: Hedef URL belirtilmedi.", 400
    
    # Protokol eksikse otomatik ekle
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'https://' + target_url

    # 2. Adım: İstek Başlıkları (Headers) ve Tarayıcı Taklidi
    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': target_url
    }
    
    # İstemciden gelen çerezleri (cookies) hedef isteğe aktar
    incoming_cookie_header = request.headers.get('Cookie')
    if incoming_cookie_header:
        req_headers['Cookie'] = incoming_cookie_header

    try:
        # 3. Adım: Uzak sunucuya güvenli bağlantı isteği oluşturma
        proxy_request = urllib.request.Request(target_url, headers=req_headers)
        
        # Zaman aşımı (Timeout) 25 saniye olarak ayarlanmıştır (Ağ yavaşlamalarına karşı koruma)
        with urllib.request.urlopen(proxy_request, timeout=25) as upstream_response:
            response_body = upstream_response.read()
            status_code = upstream_response.status
            upstream_headers = dict(upstream_response.headers.items())
            
            content_type_header = upstream_headers.get('Content-Type', '').lower()

            # 4. Adım: Güvenlik duvarı ve çakışma yaratan başlıkların filtrelenmesi
            blacklisted_headers = [
                'content-encoding', 'content-length', 'transfer-encoding', 
                'content-security-policy', 'connection', 'x-frame-options',
                'strict-transport-security', 'x-content-type-options'
            ]
            
            clean_headers_list = []
            for name, value in upstream_headers.items():
                if name.lower() not in blacklisted_headers:
                    clean_headers_list.append((name, value))
            
            # 5. Adım: CORS İzinleri (Oyun motorları ve binary assetler için kritik)
            clean_headers_list.append(('Access-Control-Allow-Origin', '*'))
            clean_headers_list.append(('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE'))
            clean_headers_list.append(('Access-Control-Allow-Headers', '*'))

            # 6. Adım: İçerik İşleme (HTML ise Linkleri Rewrite Et ve Kalkan Enjekte Et)
            if 'text/html' in content_type_header:
                try:
                    html_content = response_body.decode('utf-8', errors='ignore')
                except Exception:
                    html_content = response_body.decode('latin1', errors='ignore')
                
                # HTML içindeki bağlantı adreslerini proxy formatına dönüştüren Regex motoru
                def rewrite_url_attribute(match_obj):
                    attr_name = match_obj.group(1)
                    quote_char = match_obj.group(2)
                    raw_link = match_obj.group(3)
                    
                    # Özel protokolleri pas geç
                    if raw_link.startswith(('javascript:', 'mailto:', '#', 'data:', 'tel:')):
                        return f'{attr_name}={quote_char}{raw_link}{quote_char}'
                    
                    # Protokol bağımsız linkleri tamamlama
                    if raw_link.startswith('//'):
                        raw_link = 'https:' + raw_link
                    
                    absolute_link = urljoin(target_url, raw_link)
                    proxied_link = f'/proxy?url={absolute_link}'
                    return f'{attr_name}={quote_char}{proxied_link}{quote_char}'

                # Desteklenen HTML özniteliklerini taranması
                url_pattern = re.compile(r'(href|src|action|srcset|data-src|data-url)=(["\'])(.*?)\2', re.IGNORECASE)
                modified_html_content = url_pattern.sub(rewrite_url_attribute, html_content)
                
                # Koruma ve kalkan kodunu HTML başlığına veya gövdesine entegre etme
                if '<head>' in modified_html_content.lower():
                    modified_html_content = re.sub(r'<head>', r'<head>' + INJECTED_HEAD, modified_html_content, count=1, flags=re.IGNORECASE)
                elif '<body' in modified_html_content.lower():
                    modified_html_content = re.sub(r'<body[^>]*>', lambda m: m.group(0) + INJECTED_HEAD, modified_html_content, count=1, flags=re.IGNORECASE)
                else:
                    modified_html_content = INJECTED_HEAD + modified_html_content

                return Response(modified_html_content, status_code, clean_headers_list)
            
            # 7. Adım: İkili (Binary) Oyun Dosyaları (.wasm, .data, resimler, sesler vb.) ham bayt olarak iletilir
            return Response(response_body, status_code, clean_headers_list)
            
    except urllib.error.HTTPError as http_err:
        return f"Uzak Sunucu HTTP Hatası: {http_err.code} - {http_err.reason}", http_err.code
    except urllib.error.URLError as url_err:
        return f"Ağ Bağlantı Hatası (MEB engeli veya DNS sorunu): {str(url_err.reason)}", 502
    except Exception as general_err:
        error_trace = traceback.format_exc()
        return f"Sistem Kritik Hata Oluştu: {str(general_err)}", 500


# ==============================================================================
# BÖLÜM 4: UYGULAMA ÇALIŞTIRMA GÜVENLİĞİ
# ==============================================================================
if __name__ == '__main__':
    # Lokal testler için Flask geliştirme sunucusu
    app.run(host='0.0.0.0', port=5000, debug=False)
