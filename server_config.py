from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests
import time

app = Flask(__name__)
app.secret_key = 'quickmoney_ultra_safe_2026'

# --- CONFIGURACIÓN DE PROXIES (DECODO) ---
PROXY_USER = "sp6jzqtaou"
PROXY_PASS = "rUd7t65FxkK+x3F1hr" 
PROXY_HOST = "gate.decodo.com"
PROXY_PORT = "10001"

PROXIES = {
    "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}",
    "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
}

# --- BASE DE DATOS DE USUARIOS ---
# Aquí se guardarán los usuarios que cree tu bot
USUARIOS = {
    "mairo": {"pass": "1234", "credits": 10000, "role": "admin"},
}

# --- RUTA PARA QUE EL BOT DE TELEGRAM CREE USUARIOS ---
@app.route('/api/add_user', methods=['POST'])
def api_add_user():
    # Esta clave debe ser la misma en tu bot y en la web
    auth_key = request.headers.get('X-Bot-Key')
    if auth_key != "QUICK_SECRET_99":
        return jsonify({"status": "error", "message": "No autorizado"}), 403
    
    data = request.json
    u = data.get('username')
    p = data.get('password')
    c = data.get('credits', 50)
    
    if u and p:
        USUARIOS[u] = {"pass": p, "credits": int(c), "role": "user"}
        return jsonify({"status": "success", "message": f"Usuario {u} creado"})
    return jsonify({"status": "error", "message": "Faltan datos"}), 400

def get_bin_info(cc):
    bin_num = cc.strip()[:6]
    try:
        r = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=3)
        if r.status_code == 200:
            d = r.json()
            return f"{d.get('country', {}).get('emoji', '🌐')} {d.get('country', {}).get('name', 'PAIS')} | {d.get('bank', {}).get('name', 'BCO')}"
    except: pass
    return "🌐 Info no disponible"

ESTILOS = '''
<style>
    :root { --neon: #00ff88; --bg: #0a0a0a; --card: #151515; }
    body { background: var(--bg); color: white; font-family: sans-serif; margin: 0; }
    .nav { background: var(--card); padding: 15px 5%; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
    .container { padding: 40px 5%; max-width: 900px; margin: auto; }
    .card { background: var(--card); border: 1px solid #222; border-radius: 12px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .btn { background: var(--neon); color: black; border: none; padding: 12px 25px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; }
    textarea { width: 100%; background: #000; color: var(--neon); border: 1px solid #333; border-radius: 8px; padding: 15px; font-family: monospace; box-sizing: border-box; }
    .user-badge { background: #222; padding: 5px 12px; border-radius: 20px; font-size: 13px; border: 1px solid #444; margin-left: 5px; }
</style>
'''

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u in USUARIOS and USUARIOS[u]['pass'] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string(f'''{ESTILOS}<div style="height:100vh; display:flex; align-items:center; justify-content:center;"><div class="card" style="width:350px; text-align:center;"><h1 style="color:var(--neon);">QUICK MONEY</h1><form method="POST"><input name="u" placeholder="Usuario" style="width:100%; padding:12px; background:#000; border:1px solid #333; color:white; margin-bottom:10px;"><input type="password" name="p" placeholder="Contraseña" style="width:100%; padding:12px; background:#000; border:1px solid #333; color:white; margin-bottom:20px;"><button class="btn">ENTRAR</button></form></div></div>''')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    user_data = USUARIOS[user]
return render_template_string(f'''{ESTILOS}<div class="nav"><div style="font-weight:bold; color:var(--neon);">💸 QUICK MONEY</div><div><span class="user-badge">ID: {user}</span><span class="user-badge" style="color:var(--neon);">Créditos: {user_data['credits']}</span><a href="/logout" style="color:#ff4b4b; margin-left:15px; text-decoration:none;">Salir</a></div></div><div class="container">{f'<a href="/admin" style="display:block; border:1px solid var(--neon); color:var(--neon); padding:10px; text-align:center; text-decoration:none; margin-bottom:20px; border-radius:10px;">⚡ PANEL ADMIN ⚡</a>' if user_data['role'] == 'admin' else ''}<div class="card"><h3>Scanner de Algoritmos</h3><form method="POST" action="/process"><textarea name="lista" rows="10" placeholder="Pega tu lista aquí..."></textarea><button class="btn" style="margin-top:20px;">INICIAR VALIDACIÓN</button></form></div></div>''')

@app.route('/admin')
def admin():
    if 'user' not in session or USUARIOS[session['user']]['role'] != 'admin': return "Acceso denegado"
    return render_template_string(f'''{ESTILOS}<div class="container"><div class="card"><h2>Usuarios Registrados por el Bot</h2><table style="width:100%; text-align:left;"><tr><th>Usuario</th><th>Créditos</th><th>Rol</th></tr>{"".join([f"<tr><td>{u}</td><td style='color:var(--neon)'>{d['credits']}</td><td>{d['role']}</td></tr>" for u, d in USUARIOS.items()])}</table><br><a href="/dashboard" style="color:var(--neon);">← Volver</a></div></div>''')

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    lista = request.form.get('lista').splitlines()
    if USUARIOS[user]['credits'] < len(lista): return "Créditos insuficientes."
    USUARIOS[user]['credits'] -= len(lista)
    res = [f"<div style='border-bottom:1px solid #222; padding:10px;'>✅ LIVE: {cc} | <span style='color:#888;'>{get_bin_info(cc)}</span></div>" for cc in lista if len(cc.strip()) > 10]
    return render_template_string(f'''{ESTILOS}<div class="container"><div class="card"><h3>Resultados</h3><div style="background:#000; padding:15px; border-radius:8px; margin-bottom:20px;">{"".join(res)}</div><a href="/dashboard" class="btn" style="text-decoration:none; display:block; text-align:center;">NUEVO ESCANEO</a></div></div>''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if name == '__main__':
    app.run(host='0.0.0.0', port=80)
