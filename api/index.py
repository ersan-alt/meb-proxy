from flask import Flask, request, Response, jsonify
import urllib.request
import urllib.error
import json
from urllib.parse import urljoin
import re

app = Flask(__name__)

# --- GEMINI API CONFIG & ULEADER AI BACKEND ENGINE ---
GEMINI_API_KEY = "AQ.Ab8RN6JD3weYGwhaU6cD-Rci0-NEEDdkQwsMh9r8X99pfqRXdA"

def ask_uleader_ai(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    system_prompt = (
        "Sen ULeaderAI adlı gelişmiş bir yapay zeka asistanısın. "
        "Kurucun, geliştiricin ve sahibin Ersan Ercan'dır. "
        "Sana kurucun, yaratıcın veya sahibin kim diye sorulduğunda kesinlikle 'Ersan Ercan' olduğunu belirtmelisin. "
        "Kullanıcılara her konuda yardımcı, akıllı ve samimi bir asistansın.\n\n"
        f"Kullanıcı Mesajı: {prompt}"
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": system_prompt}]
        }]
    }
    
    req_data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url, 
        data=req_data, 
        headers={'Content-Type': 'application/json'}, 
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_body = json.loads(resp.read().decode('utf-8'))
            candidate = res_body.get('candidates', [{}])[0]
            text = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'Üzgüm, bir yanıt oluşturamadım.')
            return text
    except Exception as e:
        return f"ULeaderAI bağlantı hatası: {str(e)}"

@app.route('/uleader-api', methods=['POST'])
def uleader_api():
    data = request.get_json() or {}
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'response': 'Lütfen bir mesaj yazın.'})
    
    ai_response = ask_uleader_ai(user_message)
    return jsonify({'response': ai_response})


# --- INJECTED CLIENT-SIDE DEFENSE & ULEADER AI WIDGET ---
INJECTED_HEAD = '''
<div id="proxy-top-bar" style="position: fixed; top: 0; left: 0; width: 100%; background: #0f172a; color: white; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; z-index: 999999; font-family: Arial, sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.5); border-bottom: 2px solid #38bdf8;">
    <span style="font-weight: bold; font-size: 14px; color: #38bdf8;">🛡️ MEB Üniversal & ULeaderAI v6</span>
    <form action="/proxy" method="get" style="display: flex; gap: 8px; margin: 0; flex-grow: 1; max-width: 600px; margin-left: 20px; margin-right: 20px;">
        <input type="text" name="url" placeholder="Oyun, film veya site adresi yazın (örn: tr.y8.com)..." style="flex-grow: 1; padding: 7px 12px; border-radius: 6px; border: 1px solid #475569; background: #1e293b; color: white; font-size: 13px;" required>
        <button type="submit" style="background: #2563eb; color: white; border: none; padding: 7px 18px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px;">Git</button>
    </form>
    <a href="/" style="color: #f87171; text-decoration: none; font-size: 13px; font-weight: bold; background: rgba(248,113,113,0.1); padding: 5px 10px; border-radius: 4px;">Ana Sayfa</a>
</div>
<div style="height: 50px;"></div>

<!-- ULeaderAI Sol Alt Asistan Widget -->
<div id="uleader-ai-widget" style="position: fixed; bottom: 20px; left: 20px; z-index: 9999999; font-family: Arial, sans-serif;">
    <button id="uleader-toggle-btn" style="background: #2563eb; color: white; border: none; width: 55px; height: 55px; border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.4); cursor: pointer; font-size: 24px; display: flex; align-items: center; justify-content: center; transition: transform 0.2s;">🤖</button>
    <div id="uleader-chat-box" style="display: none; position: absolute; bottom: 70px; left: 0; width: 320px; height: 420px; background: #111827; border: 1px solid #374151; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.6); flex-direction: column; overflow: hidden;">
        <div style="background: #1f2937; color: #38bdf8; padding: 12px; font-weight: bold; font-size: 14px; display: flex; justify-content: space-between; align-items: center;">
            <span>✨ ULeaderAI Asistan</span>
            <button id="uleader-close-btn" style="background: none; border: none; color: #94a3b8; font-size: 16px; cursor: pointer;">✕</button>
        </div>
        <div id="uleader-messages" style="flex-grow: 1; padding: 12px; overflow-y: auto; font-size: 13px; color: #f1f5f9; display: flex; flex-direction: column; gap: 8px;">
            <div style="background: #1e293b; padding: 8px 12px; border-radius: 8px; max-width: 85%;">Merhaba! Ben ULeaderAI. Kurucum Ersan Ercan'dır. Sana nasıl yardımcı olabilirim?</div>
        </div>
        <div style="padding: 10px; background: #1f2937; display: flex; gap: 6px; border-top: 1px solid #374151;">
            <input type="text" id="uleader-input" placeholder="Bir şeyler yazın..." style="flex-grow: 1; background: #111827; border: 1px solid #475569; color: white; padding: 8px; border-radius: 6px; font-size: 13px; outline: none;">
            <button id="uleader-send-btn" style="background: #2563eb; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px;">Gönder</button>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('uleader-toggle-btn');
    const chatBox = document.getElementById('uleader-chat-box');
    const closeBtn = document.getElementById('uleader-close-btn');
    const sendBtn = document.getElementById('uleader-send-btn');
    const inputField = document.getElementById('uleader-input');
    const messagesContainer = document.getElementById('uleader-messages');

    if(toggleBtn && chatBox) {
        toggleBtn.onclick = () => {
            chatBox.style.display = chatBox.style.display === 'flex' ? 'none' : 'flex';
        };
        closeBtn.onclick = () => {
            chatBox.style.display = 'none';
        };

        async function sendMessage() {
            const text = inputField.value.trim();
            if(!text) return;

            messagesContainer.innerHTML += `<div style="background: #2563eb; color: white; padding: 8px 12px; border-radius: 8px; max-width: 85%; align-self: flex-end;">${text}</div>`;
            inputField.value = '';
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            messagesContainer.innerHTML += `<div id="${loadingId}" style="background: #1e293b; color: #94a3b8; padding: 8px 12px; border-radius: 8px; max-width: 85%;">Düşünüyor...</div>`;
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            try {
                const res = await fetch('/uleader-api', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                document.getElementById(loadingId).remove();
                messagesContainer.innerHTML += `<div style="background: #1e293b; color: #f1f5f9; padding: 8px 12px; border-radius: 8px; max-width: 85%;">${data.response}</div>`;
            } catch(err) {
                document.getElementById(loadingId).remove();
                messagesContainer.innerHTML += `<div style="background: #7f1d1d; color: #fca5a5; padding: 8px 12px; border-radius: 8px; max-width: 85%;">Bağlantı hatası oluştu.</div>`;
            }
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        sendBtn.onclick = sendMessage;
        inputField.onkeypress = (e) => { if(e.key === 'Enter') sendMessage(); };
    }
});

// Domain, Iframe ve Embed Kalkanı
try {
    Object.defineProperty(window, 'top', { get: function() { return window; }, configurable: true });
    Object.defineProperty(window, 'parent', { get: function() { return window; }, configurable: true });
    Object.defineProperty(window, 'frameElement', { get: function() { return null; }, configurable: true });
    Object.defineProperty(document, 'referrer', { get: function() { return 'https://tr.y8.com/'; }, configurable: true });
    
    const targetHost = window.location.hostname || 'tr.y8.com';
    const targetOrigin = window.location.origin || 'https://tr.y8.com';
    
    if (window.location) {
        window.location.__defineGetter__('hostname', function() { return targetHost; });
        window.location.__defineGetter__('host', function() { return targetHost; });
        window.location.__defineGetter__('origin', function() { return targetOrigin; });
    }
} catch(e) {}

// Fetch & XHR Proxy Interceptor
(function() {
    const originalFetch = window.fetch;
    window.fetch = function(input, init) {
        let url = input;
        if (input instanceof Request) {
            url = input.url;
        }
        if (typeof url === 'string' && !url.startsWith('data:') && !url.includes('/proxy?url=') && !url.includes('/uleader-api')) {
            if (url.startsWith('//')) url = 'https:' + url;
            let absUrl = new URL(url, window.location.href).href;
            let proxied = '/proxy?url=' + encodeURIComponent(absUrl);
            if (input instanceof Request) {
                input = new Request(proxied, init);
            } else {
                input = proxied;
            }
        }
        return originalFetch.call(this, input, init);
    };

    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        if (typeof url === 'string' && !url.startsWith('data:') && !url.includes('/proxy?url=') && !url.includes('/uleader-api')) {
            if (url.startsWith('//')) url = 'https:' + url;
            let absUrl = new URL(url, window.location.href).href;
            arguments[1] = '/proxy?url=' + encodeURIComponent(absUrl);
        }
        return originalOpen.apply(this, arguments);
    };
})();

// Tık Yönlendirme Kontrolü
document.addEventListener('click', function(e) {
    let target = e.target.closest('a');
    if (target && target.href) {
        let href = target.getAttribute('href');
        if (href && !href.startsWith('javascript:') && !href.startsWith('#') && !href.startsWith('mailto:') && !href.startsWith('tel:') && !href.includes('/uleader-api')) {
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

# --- HOME ROUTE ---
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>MEB Üniversal Tam Korumalı Erişim Geçidi</title>
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
            <div class="badge">🚀 ULeaderAI & Üniversal Oyun Koruması Aktif</div>
            <h2>Erişim Geçidi</h2>
            <p>Y8, CrazyGames ve tüm siteler için adresi yazın.</p>
            <form action="/proxy" method="get">
                <input type="text" name="url" placeholder="https://tr.y8.com" required>
                <button type="submit">Bağlan</button>
            </form>
        </div>
    </body>
    </html>
    '''

# --- PROXY ENGINE ROUTE ---
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
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read()
            status_code = resp.status
            resp_headers = dict(resp.headers.items())
            
            content_type = resp_headers.get('Content-Type', '').lower()

            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'content-security-policy', 'connection', 'x-frame-options']
            headers_list = [(name, value) for name, value in resp_headers.items() if name.lower() not in excluded_headers]
            
            headers_list.append(('Access-Control-Allow-Origin', '*'))
            headers_list.append(('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE'))
            headers_list.append(('Access-Control-Allow-Headers', '*'))

            if 'text/html' in content_type:
                try:
                    html = body.decode('utf-8', errors='ignore')
                except:
                    html = body.decode('latin1', errors='ignore')
                
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

                pattern = re.compile(r'(href|src|action|srcset|data-src)=(["\'])(.*?)\2', re.IGNORECASE)
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
        return f"Bağlantı hatası veya engel: {str(e)}", 500
