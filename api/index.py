# ==============================================================================
# PROJE: ULeader Akademik Eğitim Notları ve Güvenli Arşiv Geçidi (Ultimate v11.0)
# AÇIKLAMA: MEB bot kamuflesi, kararlı /proxy?url= görsel/asset yönlendirmesi,
#           Anti-Detection koruması, CSS url(...) ve Unity WebGL tam desteği.
# ==============================================================================

from flask import Flask, request, Response, jsonify
import urllib.request
import urllib.error
import http.cookiejar
from urllib.parse import urljoin, urlparse
import re
import traceback
import sys

app = Flask(__name__)

# Küresel çerez kavanozu (CookieJar) ile oturum sürekliliği
cookie_jar = http.cookiejar.CookieJar()
cookie_handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(cookie_handler)
urllib.request.install_opener(opener)


# ==============================================================================
# BÖLÜM 1: MEB VE FORTİNET BOTLARI KAMUFLAJ KATMANI (BOT DEFENSE)
# ==============================================================================
def is_meb_bot(user_agent):
    if not user_agent:
        return True  # User-Agent başlığı olmayan şüpheli tarayıcıları doğrudan bot say
    
    bot_keywords = [
        'bot', 'crawler', 'spider', 'fortinet', 'fortiguard', 
        'cisco', 'zscaler', 'slurp', 'headless', 'netscaler', 'barracuda'
    ]
    return any(keyword in user_agent.lower() for keyword in bot_keywords)


# MEB denetim botlarına gösterilecek masum akademik içerik (Kamoflaj Sayfası)
FAKE_EDUCATION_PAGE = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Anadolu Selçuklu Devleti Dönemi Mimari Yapıları ve Kervansaraylar</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #222; background: #f8fafc; line-height: 1.7;">
    <div style="max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <h1 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 15px;">Anadolu Selçuklu Devleti Siyasi ve Kültürel Tarihi</h1>
        <p><strong>Öğrenci Araştırma ve Performans Notları:</strong> Bu akademik çalışma, 11. ve 13. yüzyıllar arasında Anadolu'da hüküm sürmüş olan Selçuklu hanedanının kültürel, mimari ve idari yapılarını incelemek amacıyla Milli Eğitim Bakanlığı müfredat standartlarına uygun olarak derlenmiştir.</p>
        
        <h3 style="color: #334155; margin-top: 25px;">1. Mimari Özellikler ve Kervansaraylar</h3>
        <p>Selçuklu dönemi mimarisinde taş işçiliği zirve noktasına ulaşmıştır. Ticaretin güvenle yürütülmesi ve tüccarların konaklaması için inşa edilen kervansaraylar, dönemin ekonomik refah düzeyini ve sosyal devlet anlayışını gözler önüne sermektedir.</p>
        
        <h3 style="color: #334155; margin-top: 25px;">2. İdari ve Askeri Teşkilatlanma</h3>
        <p>Merkezi otoritenin korunması amacıyla uç beylikleri kurulmuş, deniz ticaretine verilen önem neticesinde Alanya ve Sinop gibi stratejik liman şehirleri fethedilmiştir.</p>
        
        <div style="margin-top: 40px; padding-top: 15px; border-top: 1px solid #e2e8f0; font-size: 13px; color: #64748b;">
            Kaynak: MEB Ortaöğretim Tarih Ders Kitapları Arşivi © 2026
        </div>
    </div>
</body>
</html>'''


# ==============================================================================
# BÖLÜM 2: İSTEMCİ GÜVENLİK KALKANI VE ASSET YAKALAYICI SCRIPTLER
# ==============================================================================
INJECTED_HEAD = '''
<div id="proxy-top-bar" style="position: fixed; top: 0; left: 0; width: 100%; background: #0f172a; color: white; padding: 8px 15px; display: flex; justify-content: space-between; align-items: center; z-index: 2147483647; font-family: Arial, sans-serif; box-shadow: 0 4px 15px rgba(0,0,0,0.7); border-bottom: 2px solid #38bdf8;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">📚 Eğitim Arşivi</span>
        <span style="font-size: 12px; color: #94a3b8;">Hızlı Tünel Aktif</span>
    </div>
    <form action="/proxy" method="get" style="display: flex; gap: 6px; margin: 0; flex-grow: 1; max-width: 550px; margin-left: 15px; margin-right: 15px;">
        <input type="text" name="url" placeholder="Dosya veya kaynak adresi girin..." style="flex-grow: 1; padding: 6px 10px; border-radius: 4px; border: 1px solid #475569; background: #1e293b; color: white; font-size: 12px; outline: none;" required>
        <button type="submit" style="background: #2563eb; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;">Getir</button>
    </form>
    <div>
        <a href="/" style="color: #f87171; text-decoration: none; font-size: 12px; font-weight: bold; background: rgba(248,113,113,0.1); padding: 5px 10px; border-radius: 4px;">Ana Sayfa</a>
    </div>
</div>
<div style="height: 45px;"></div>

<script>
// --- ANTI-DETECTION KORUMASI ---
try {
    Object.defineProperty(navigator, 'webdriver', { get: function() { return false; }, configurable: true });
    Object.defineProperty(navigator, 'plugins', { get: function() { return [1, 2, 3, 4, 5]; }, configurable: true });
    window.console.error = window.console.error || function() {};
} catch(e) {}

// Domain ve Iframe Kalkanı
try {
    Object.defineProperty(window, 'top', { get: function() { return window; }, configurable: true });
    Object.defineProperty(window, 'parent', { get: function() { return window; }, configurable: true });
    Object.defineProperty(window, 'frameElement', { get: function() { return null; }, configurable: true });
    Object.defineProperty(document, 'referrer', { get: function() { return window.location.href; }, configurable: true });
} catch(e) {}

// --- DİNAMİK FETCH & XHR PROXY MOTORU ---
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

// Tık Yönlendirme Kontrolü
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
# BÖLÜM 3: AKADEMİK SOSYAL MÜHENDİSLİK ANA SAYFA RÖTASI
# ==============================================================================
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
            <p>Eğitim materyalleri, kaynaklar ve arşiv için adresi girin.</p>
            <form action="/proxy" method="get">
                <input type="text" name="url" placeholder="https://tr.y8.com" required>
                <button type="submit">Sisteme Bağlan</button>
            </form>
            <div class="hint">Yüksek hızlı şifrelenmiş tünel protokolü aktiftir.</div>
        </div>
    </body>
    </html>
    '''


# ==============================================================================
# BÖLÜM 4: PROXY MOTORU VE GÖRSEL / ASSET YÖNLENDİRİCİ
# ==============================================================================
@app.route('/proxy')
def proxy():
    user_agent = request.headers.get('User-Agent', '')
    if is_meb_bot(user_agent):
        return FAKE_EDUCATION_PAGE
        
    target_url = request.args.get('url')
    if not target_url:
        return "URL belirtilmedi.", 400
    
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'https://' + target_url

    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': target_url
    }
    
    incoming_cookie = request.headers.get('Cookie')
    if incoming_cookie:
        req_headers['Cookie'] = incoming_cookie

    try:
        req = urllib.request.Request(target_url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read()
            status_code = resp.status
            resp_headers = dict(resp.headers.items())
            
            content_type = resp_headers.get('Content-Type', '').lower()

            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'content-security-policy', 'connection', 'x-frame-options']
            headers_list = [(name, value) for name, value in resp_headers.items() if name.lower() not in excluded_headers]
            
            # CORS İzinleri (WebGL, .wasm, .data ve tüm resim formatları için şart)
            headers_list.append(('Access-Control-Allow-Origin', '*'))
            headers_list.append(('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE'))
            headers_list.append(('Access-Control-Allow-Headers', '*'))

            # HTML veya CSS dosyalarında linkleri ve görsel yollarını yeniden yaz
            if 'text/html' in content_type or 'text/css' in content_type:
                try:
                    content_str = body.decode('utf-8', errors='ignore')
                except:
                    content_str = body.decode('latin1', errors='ignore')
                
                def rewrite_url(match):
                    attr = match.group(1)
                    quote = match.group(2)
                    original_link = match.group(3)
                    
                    if original_link.startswith(('javascript:', 'mailto:', '#', 'data:', 'tel:')):
                        return f'{attr}={quote}{original_link}{quote}'
                    
                    if original_link.startswith('//'):
                        original_link = 'https:' + original_link
                    
                    full_url = urljoin(target_url, original_link)
                    proxied_url = f'/proxy?url={full_url}'
                    return f'{attr}={quote}{proxied_url}{quote}'

                # HTML etiketleri (href, src, data-src, srcset, poster vb.)
                pattern = re.compile(r'(href|src|action|srcset|data-src|data-original|poster)=(["\'])(.*?)\2', re.IGNORECASE)
                modified_content = pattern.sub(rewrite_url, content_str)

                # CSS background-image url(...) görsel yollarını düzeltme
                def rewrite_css_url(m):
                    q = m.group(1)
                    orig_url = m.group(2).strip()
                    if orig_url.startswith(('data:', 'javascript:')) or '/proxy?url=' in orig_url:
                        return f'url({q}{orig_url}{q})'
                    if orig_url.startswith('//'):
                        orig_url = 'https:' + orig_url
                    full_css_url = urljoin(target_url, orig_url)
                    return f'url({q}/proxy?url={full_css_url}{q})'

                css_pattern = re.compile(r'url\((["\']?)(.*?)\1\)', re.IGNORECASE)
                modified_content = css_pattern.sub(rewrite_css_url, modified_content)
                
                if 'text/html' in content_type:
                    if '<head>' in modified_content.lower():
                        modified_content = re.sub(r'<head>', r'<head>' + INJECTED_HEAD, modified_content, count=1, flags=re.IGNORECASE)
                    elif '<body' in modified_content.lower():
                        modified_content = re.sub(r'<body[^>]*>', lambda m: m.group(0) + INJECTED_HEAD, modified_content, count=1, flags=re.IGNORECASE)
                    else:
                        modified_content = INJECTED_HEAD + modified_content

                return Response(modified_content, status_code, headers_list)
            
            # Resimler, fontlar, sesler ve oyun binary dosyaları (.wasm, .data) ham bayt olarak hızlıca iletilir
            return Response(body, status_code, headers_list)
            
    except Exception as e:
        return f"Ağ geçidi bağlantı hatası: {str(e)}", 500


# ==============================================================================
# BÖLÜM 5: ÇALIŞTIRMA GÜVENLİĞİ VE SİSTEM KARARLILIĞI
# ==============================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
