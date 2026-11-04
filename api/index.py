# ==============================================================================
# MODÜL: ULeader Ön Yüz ve Akademik Kamoflaj (index.py)
# ==============================================================================

from flask import Flask, request

app = Flask(__name__)

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
        <p>Bu akademik çalışma, MEB müfredat standartlarına uygun olarak performans ödevi amacıyla derlenmiştir.</p>
    </div>
</body>
</html>'''

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def index(path):
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
                <input type="text" name="url" placeholder="https://poki.com veya https://crazygames.com" required>
                <button type="submit">Sisteme Bağlan</button>
            </form>
            <div class="hint">Tam korumalı tünel ve bot engelleme katmanı aktiftir.</div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
