from flask import Flask, render_template_string, request, redirect, url_for, session
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

# --- BASE DE DATOS DE USUARIOS (Simulada para el ejemplo) ---
# Aquí es donde el bot de Telegram agregará los datos.
# Formato: "usuario": {"pass": "123", "credits": 500, "role": "user"}
USUARIOS = {
    "mairo": {"pass": "1234", "credits": 10000, "role": "admin"},
    "cliente1": {"pass": "bot552", "credits": 50, "role": "user"}
}

def get_bin_info(cc):
    bin_num = cc.strip()[:6]
    if not bin_num.isdigit(): return "❌ Formato Inválido"
    try:
        # Usamos un servicio rápido de BINS
        r = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=3)
        if r.status_code == 200:
            data = r.json()
            banco = data.get('bank', {}).get('name', 'BCO DESCONOCIDO')
            pais = data.get('country', {}).get('name', 'PAIS')
            emoji = data.get('country', {}).get('emoji', '🌐')
            return f"{emoji} {pais} | {banco}"
    except: pass
    return "🌐 Info no disponible"

ESTILOS = '''
<style>
    :root { --neon: #00ff88; --bg: #0a0a0a; --card: #151515; }
    body { background: var(--bg); color: white; font-family: 'Inter', sans-serif; margin: 0; }
    .nav { background: var(--card); padding: 15px 5%; border-bottom: 1px solid #333; display: flex; justify-content: space-between; }
    .container { padding: 40px 5%; max-width: 900px; margin: auto; }
    .card { background: var(--card); border: 1px solid #222; border-radius: 12px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .btn { background: var(--neon); color: black; border: none; padding: 12px 25px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.3s; }
    .btn:hover { box-shadow: 0 0 15px var(--neon); transform: translateY(-2px); }
    textarea { width: 100%; background: #000; color: var(--neon); border: 1px solid #333; border-radius: 8px; padding: 15px; font-family: monospace; }
    .user-badge { background: #222; padding: 5px 12px; border-radius: 20px; font-size: 13px; border: 1px solid #444; }
</style>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u in USUARIOS and USUARIOS[u]['pass'] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string(f'''
    {ESTILOS}
    <div style="height:100vh; display:flex; align-items:center; justify-content:center;">
        <div class="card" style="width:350px; text-align:center;">
            <h1 style="color:var(--neon); margin-bottom:5px;">QUICK MONEY</h1>
            <p style="color:#666; font-size:14px; margin-bottom:25px;">Platform Management</p>
            <form method="POST">
                <input name="u" placeholder="Usuario asignado" style="width:100%; padding:12px; background:#000; border:1px solid #333; color:white; margin-bottom:10px; border-radius:5px;">
                <input type="password" name="p" placeholder="Contraseña" style="width:100%; padding:12px; background:#000; border:1px solid #333; color:white; margin-bottom:20px; border-radius:5px;">
                <button class="btn" style="width:100%;">ENTRAR AL SISTEMA</button>
            </form>
        </div>
    </div>
    ''')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    return render_template_string(f'''
    {ESTILOS}
    <div class="nav">
        <div style="font-weight:bold; color:var(--neon);">💸 QUICK MONEY</div>
        <div>
<span class="user-badge">ID: {user}</span>
            <span class="user-badge" style="color:var(--neon);">Créditos: {USUARIOS[user]['credits']}</span>
            <a href="/logout" style="color:#ff4b4b; text-decoration:none; margin-left:15px; font-size:14px;">Cerrar sesión</a>
        </div>
    </div>
    <div class="container">
        {f'<div class="card" style="margin-bottom:20px; border-color:var(--neon);"><b>PANEL ADMIN:</b> <a href="/admin" style="color:var(--neon);">Gestionar Usuarios y Bot</a></div>' if USUARIOS[user]['role'] == 'admin' else ''}
        <div class="card">
            <h3>Terminal de Carga Profesional</h3>
            <form method="POST" action="/process">
                <textarea name="lista" rows="12" placeholder="4540123456789012|12|26|000"></textarea>
                <div style="margin-top:20px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#666; font-size:13px;">Costo: 1 crédito por línea</span>
                    <button class="btn">INICIAR ESCANEO GLOBAL</button>
                </div>
            </form>
        </div>
    </div>
    ''')

@app.route('/admin')
def admin():
    if 'user' not in session or USUARIOS[session['user']]['role'] != 'admin':
        return "Acceso denegado"
    # Aquí puedes ver todos los usuarios que han comprado
    return render_template_string(f'''
    {ESTILOS}
    <div class="container">
        <div class="card">
            <h2>Gestión de Usuarios (Database)</h2>
            <table style="width:100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #333; text-align:left;">
                    <th style="padding:10px;">Usuario</th>
                    <th>Password</th>
                    <th>Créditos</th>
                    <th>Estado</th>
                </tr>
                {"".join([f"<tr style='border-bottom:1px solid #222;'><td style='padding:10px;'>{u}</td><td>{d['pass']}</td><td style='color:var(--neon)'>{d['credits']}</td><td>Activo</td></tr>" for u, d in USUARIOS.items()])}
            </table>
            <br><a href="/dashboard" style="color:var(--neon); text-decoration:none;">← Volver al Dashboard</a>
        </div>
    </div>
    ''')

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    lista = request.form.get('lista').splitlines()
    
    if USUARIOS[user]['credits'] < len(lista):
        return "⚠️ Créditos insuficientes. Contacta al bot para recargar."

    USUARIOS[user]['credits'] -= len(lista)
    resultados = []
    for cc in lista:
        if len(cc.strip()) > 10:
            info = get_bin_info(cc)
            resultados.append(f"<div style='border-bottom:1px solid #222; padding:8px;'>✅ LIVE: {cc} | <span style='color:#888;'>{info}</span></div>")
    
    return render_template_string(f'''
    {ESTILOS}
    <div class="container">
        <div class="card">
            <h3>Resultados</h3>
            <div style="background:#000; border-radius:8px; padding:15px; font-family:monospace;">
                {"".join(resultados)}
            </div>
            <p>Saldo restante: {USUARIOS[user]['credits']} créditos</p>
            <a href="/dashboard" class="btn" style="display:inline-block; text-decoration:none; text-align:center;">NUEVO ESCANEO</a>
        </div>
    </div>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if name == '__main__':
    app.run(host='0.0.0.0', port=80)
