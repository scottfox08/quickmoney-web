from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests
import base64
import os

app = Flask(__name__)
app.secret_key = 'quickmoney_elite_2026'

# --- CARGA DEL LOGO (EL ILUSIONISTA) ---
def get_logo():
    try:
        if os.path.exists("image.png"):
            with open("image.png", "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    except: pass
    return ""

LOGO_BG = get_logo()

# --- CONFIGURACIÓN ---
PX = {"http": "http://sp6jzqtaou:rUd7t65FxkK+x3F1hr@gate.decodo.com:10001", "https": "http://sp6jzqtaou:rUd7t65FxkK+x3F1hr@gate.decodo.com:10001"}
USUARIOS = {"mairo": {"pass": "1234", "credits": 10000, "role": "admin"}}

def get_bin(cc):
    try:
        r = requests.get(f"https://lookup.binlist.net/{cc[:6]}", proxies=PX, timeout=4)
        if r.status_code == 200:
            d = r.json()
            b = d.get('bank', {}).get('name', 'BCO')
            p = d.get('country', {}).get('name', 'S/N')
            e = d.get('country', {}).get('emoji', '🌐')
            return f"{e} {p} | {b}"
    except: pass
    return "🌐 Info no disponible"

# --- DISEÑO ELITE (ESCAPE YOUR LIMITS) ---
CSS = f"""
<style>
    :root {{ --silver: #e0e0e0; --black: #050505; --accent: #ffffff; }}
    body {{ 
        background: var(--black) url('{LOGO_BG}') no-repeat center center fixed; 
        background-size: cover; color: var(--silver); font-family: 'Segoe UI', sans-serif; margin: 0; 
    }}
    .overlay {{ background: rgba(0,0,0,0.75); min-height: 100vh; width: 100%; display: flex; flex-direction: column; }}
    .nav {{ background: rgba(10,10,15,0.9); padding: 20px; border-bottom: 1px solid var(--accent); display: flex; justify-content: space-between; align-items: center; box-shadow: 0 0 25px rgba(255,255,255,0.2); }}
    .card {{ background: rgba(10,10,10,0.85); border: 1px solid #444; border-radius: 15px; padding: 30px; margin: 20px auto; max-width: 700px; box-shadow: 0 0 40px rgba(0,0,0,0.8); border-top: 2px solid var(--silver); backdrop-filter: blur(5px); }}
    .btn {{ background: linear-gradient(135deg, #fff 0%, #a0a0a0 100%); color: #000; border: none; padding: 15px; border-radius: 8px; font-weight: bold; width: 100%; cursor: pointer; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; }}
    .btn:hover {{ transform: scale(1.02); box-shadow: 0 0 20px rgba(255,255,255,0.4); }}
    input, textarea {{ width: 100%; background: rgba(0,0,0,0.8); color: #fff; border: 1px solid #555; padding: 12px; margin-bottom: 15px; border-radius: 8px; box-sizing: border-box; }}
    .live-row {{ border-bottom: 1px solid #333; padding: 12px; font-family: 'Courier New', monospace; display: flex; justify-content: space-between; align-items: center; }}
    .tag-live {{ color: #fff; text-shadow: 0 0 8px #fff; font-weight: bold; border: 1px solid #fff; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
</style>
"""

@app.route('/')
def index(): return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u in USUARIOS and USUARIOS[u]['pass'] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string(f'<html><head><title>QUICK MONEY | LOGIN</title>{CSS}</head><body><div class="overlay" style="justify-content:center; align-items:center;"><div class="card" style="width:350px; text-align:center;"><h1 style="letter-spacing:5px; margin-bottom:30px; text-shadow: 0 0 10px white;">QUICK MONEY</h1><form method="POST"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASSWORD"><button class="btn">ACCEDER AL TRONO</button></form></div></div></body></html>')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    return render_template_string(f'<html><head><title>QUICK MONEY | TERMINAL</title>{CSS}</head><body><div class="overlay"><div class="nav"><b>🦁 QUICK MONEY ELITE</b> <span>ID: {u} | Creds: {USUARIOS[u]["credits"]} | <a href="/logout" style="color:#ff4d4d; text-decoration:none; font-weight:bold;">SALIR</a></span></div><div class="card"><h3 style="text-align:center; letter-spacing:2px;">ESCAPE YOUR LIMITS</h3><form method="POST" action="/process"><textarea name="lista" rows="10" placeholder="FORMATO: CC|MM|YY|CVV"></textarea><button class="btn">INICIAR VALIDACIÓN</button></form></div></div></body></html>')

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    lista = request.form.get('lista','').splitlines()
    if USUARIOS[u]['credits'] < len(lista): return "Saldo insuficiente"
    USUARIOS[u]['credits'] -= len(lista)
    res = "".join([f"<div class='live-row'><span class='tag-live'>LIVE</span> <span>{cc}</span> <span>{get_bin(cc)}</span></div>" for cc in lista if len(cc)>10])
    return render_template_string(f'<html><head>{CSS}</head><body><div class="overlay"><div class="nav"><b>RESULTADOS</b><a href="/dashboard" style="color:white; text-decoration:none;">← VOLVER</a></div><div class="card">{res if res else "No hay resultados"}<br><a href="/dashboard" class="btn" style="display:block; text-align:center; text-decoration:none; margin-top:20px;">NUEVA CONSULTA</a></div></div></body></html>')

@app.route('/api/add_user', methods=['POST'])
def api_add_user():
    if request.headers.get('X-Bot-Key') != "QUICK_SECRET_99": return jsonify({"error":1}), 403
    data = request.json
    u, p, c = data.get('username'), data.get('password'), data.get('credits', 50)
    USUARIOS[u] = {"pass": p, "credits": int(c), "role": "user"}
    return jsonify({"status":"ok"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
