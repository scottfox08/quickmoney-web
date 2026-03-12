from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests
import time

app = Flask(__name__)
app.secret_key = 'quickmoney_ultra_2026'

# --- CONFIGURACIÓN DE PROXIES (DECODO) ---
PROXY_USER = "sp6jzqtaou"
PROXY_PASS = "rUd7t65FxkK+x3F1hr" 
PROXIES = {
    "http": f"http://{PROXY_USER}:{PROXY_PASS}@gate.decodo.com:10001",
    "https": f"http://{PROXY_USER}:{PROXY_PASS}@gate.decodo.com:10001"
}

# --- BASE DE DATOS DE USUARIOS ---
USUARIOS = {
    "mairo": {"pass": "1234", "credits": 10000, "role": "admin"}
}

@app.route('/api/add_user', methods=['POST'])
def api_add_user():
    if request.headers.get('X-Bot-Key') != "QUICK_SECRET_99":
        return jsonify({"status": "error"}), 403
    data = request.json
    u, p, c = data.get('username'), data.get('password'), data.get('credits', 50)
    if u and p:
        USUARIOS[u] = {"pass": p, "credits": int(c), "role": "user"}
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

def get_bin_info(cc):
    try:
        # Aquí usamos los PROXIES para la consulta
        r = requests.get(f"https://lookup.binlist.net/{cc[:6]}", proxies=PROXIES, timeout=4)
        if r.status_code == 200:
            d = r.json()
            return f"{d.get('country',{}).get('emoji','🌐')} {d.get('bank',{}).get('name','BCO')}"
    except: pass
    return "🌐 Info no disponible"

ESTILOS = '''
<style>
    :root { --n: #00ff88; --b: #0a0a0a; }
    body { background: var(--b); color: white; font-family: sans-serif; margin: 0; }
    .nav { background: #151515; padding: 15px 5%; border-bottom: 1px solid #333; display: flex; justify-content: space-between; }
    .card { background: #151515; border: 1px solid #222; border-radius: 12px; padding: 25px; margin: 20px auto; max-width: 800px; }
    .btn { background: var(--n); color: black; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; }
    textarea { width: 100%; background: #000; color: var(--n); border: 1px solid #333; border-radius: 8px; padding: 15px; box-sizing: border-box; font-family: monospace; }
    .badge { background: #222; padding: 5px 10px; border-radius: 15px; font-size: 12px; border: 1px solid #444; }
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
    return render_template_string(f'{ESTILOS}<div style="height:100vh; display:flex; align-items:center; justify-content:center;"><div class="card" style="width:320px; text-align:center;"><h1 style="color:var(--n)">QUICK MONEY</h1><form method="POST"><input name="u" placeholder="Usuario" style="width:100%; padding:10px; margin-bottom:10px; background:#000; color:white; border:1px solid #333;"><input type="password" name="p" placeholder="Contraseña" style="width:100%; padding:10px; margin-bottom:20px; background:#000; color:white; border:1px solid #333;"><button class="btn">ENTRAR AL SISTEMA</button></form></div></div>')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    u = session['user']
    u_data = USUARIOS[u]
    return render_template_string(f'''{ESTILOS}
    <div class="nav">
        <b>💸 QUICK MONEY</b>
        <div><span class="badge">ID: {u}</span> <span class="badge" style="color:var(--n)">Créditos: {u_data['credits']}</span> <a href="/logout" style="color:#ff4b4b; text-decoration:none; margin-left:10px;">Salir</a></div>
    </div>
    <div class="container">
        {f'<div class="card" style="border-color:var(--n); text-align:center;"><a href="/admin" style="color:var(--n); text-decoration:none; font-weight:bold;">⚡ PANEL ADMINISTRADOR ⚡</a></div>' if u_data['role'] == 'admin' else ''}
        <div class="card">
            <h3 style="margin-top:0">Scanner de Algoritmos</h3>
            <form method="POST" action="/process">
                <textarea name="lista" rows="10" placeholder="Pega tu lista aquí..."></textarea>
                <button class="btn" style="margin-top:20px">INICIAR VALIDACIÓN GLOBAL</button>
            </form>
        </div>
    </div>''')

@app.route('/admin')
def admin():
    if 'user' not in session or USUARIOS[session['user']]['role'] != 'admin':
        return "Acceso Denegado"
    rows = "".join([f"<tr><td style='padding:10px; border-bottom:1px solid #222;'>{u}</td><td style='color:var(--n)'>{d['credits']}</td><td>{d['role']}</td></tr>" for u, d in USUARIOS.items()])
    return render_template_string(f'''{ESTILOS}<div class="card"><h2>Gestión de Usuarios</h2><table style="width:100%; text-align:left;"><tr><th>User</th><th>Creds</th><th>Rol</th></tr>{rows}</table><br><a href="/dashboard" style="color:var(--n)">← Volver</a></div>''')

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session:
        return redirect(url_for('login'))
    u = session['user']
    lista = request.form.get('lista', '').splitlines()
    if USUARIOS[u]['credits'] < len(lista):
        return "Créditos insuficientes."
    USUARIOS[u]['credits'] -= len(lista)
    res = [f"<div style='border-bottom:1px solid #222; padding:12px;'>✅ LIVE: {cc} | <span style='color:#888;'>{get_bin_info(cc)}</span></div>" for cc in lista if len(cc.strip()) > 10]
    return render_template_string(f'''{ESTILOS}<div class="card"><h3>Resultados</h3><div style="background:#000; padding:15px; border-radius:8px; margin-bottom:20px;">{"".join(res) if res else "No se encontraron resultados válidos."}</div><a href="/dashboard" class="btn" style="text-decoration:none; display:block; text-align:center;">NUEVO ESCANEO</a></div>''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
