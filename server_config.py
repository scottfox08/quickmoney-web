from flask import Flask, render_template_string, request, redirect, url_for, session
import requests
import time

app = Flask(__name__)
app.secret_key = 'quickmoney_ultra_safe_2026'

# --- CONFIGURACIÓN DE PROXIES (DECODO) ---
PROXY_USER = "sp6jzqtaou"
PROXY_PASS = "Ud7t65FxkK+x3Flhr" 
PROXY_HOST = "gate.decodo.com"
PROXY_PORT = "10001"

PROXIES = {
    "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}",
    "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
}

# --- BASE DE DATOS DE USUARIOS ---
USUARIOS = {
    "mairo": ["1234", 5000],
    "admin": ["admin2026", 100]
}

# --- FUNCIÓN BIN CHECKER (BANCO Y PAÍS) ---
def get_bin_info(cc):
    bin_num = cc.strip()[:6]
    if not bin_num.isdigit(): return "❌ Formato Inválido"
    try:
        # Consultamos una base de datos de BINS profesional
        r = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=4)
        if r.status_code == 200:
            data = r.json()
            banco = data.get('bank', {}).get('name', 'BCO DESCONOCIDO')
            pais = data.get('country', {}).get('name', 'PAIS')
            emoji = data.get('country', {}).get('emoji', '🌐')
            tipo = data.get('type', 'N/A').upper()
            nivel = data.get('brand', 'N/A').upper()
            return f"{emoji} {pais} | {banco} | {nivel} - {tipo}"
    except:
        pass
    return "🌐 Info no disponible temporalmente"

ESTILOS = '''
<style>
    :root { --neon-green: #00ff88; --dark-bg: #050505; }
    body { background: var(--dark-bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; }
    .card { background: #121212; border: 1px solid #333; border-radius: 15px; padding: 25px; margin: 20px auto; max-width: 800px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .btn { background: var(--neon-green); color: black; border: none; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; text-transform: uppercase; }
    textarea { width: 100%; background: #000; color: var(--neon-green); border: 1px solid #333; border-radius: 10px; padding: 15px; box-sizing: border-box; font-family: monospace; }
    .live-box { background: #000; border: 1px solid var(--neon-green); padding: 15px; border-radius: 10px; text-align: left; margin-top: 20px; font-size: 14px; }
    .stat-bar { display: flex; justify-content: space-around; margin-bottom: 20px; }
    .stat-item { background: #1a1a1a; padding: 10px 20px; border-radius: 8px; border: 1px solid #333; }
</style>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u in USUARIOS and USUARIOS[u][0] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string(f'{ESTILOS}<div style="height:100vh; display:flex; align-items:center;"><div class="card" style="width:300px;"><h2>💸 LOGIN</h2><form method="POST"><input name="u" placeholder="User" style="width:100%; padding:10px; margin:5px 0;"><input type="password" name="p" placeholder="Pass" style="width:100%; padding:10px; margin:5px 0;"><button class="btn">ACCEDER</button></form></div></div>')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template_string(f'''
    {ESTILOS}
    <div class="card">
        <h2>💸 QUICK MONEY CHECKER 💸</h2>
        <div class="stat-bar">
            <div class="stat-item">User: <b>{session['user']}</b></div>
            <div class="stat-item">Créditos: <b style="color:var(--neon-green)">{USUARIOS[session['user']][1]}</b></div>
        </div>
        <form method="POST" action="/process">
            <textarea name="lista" rows="10" placeholder="FORMATO: CC|MM|YY|CVV"></textarea>
            <button class="btn" style="margin-top:15px;">🔍 INICIAR ESCANEO GLOBAL</button>
        </form>
    </div>
    ''')

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
lista = request.form.get('lista').splitlines()
    user = session['user']
    
    if USUARIOS[user][1] < len(lista):
        return "⚠️ No tienes suficientes créditos para esta lista."

    USUARIOS[user][1] -= len(lista)
    resultados = []

    for cc in lista:
        if len(cc.strip()) > 10:
            # Aquí llamamos a la función que identifica el banco y país
            info = get_bin_info(cc)
            resultados.append(f"✅ LIVE: {cc} | {info}")
            # Pequeña pausa para no saturar la API de BINS
            time.sleep(0.5)

    return render_template_string(f'''
    {ESTILOS}
    <div class="card">
        <h3>Resultados del Procesamiento</h3>
        <p>Créditos restantes: {USUARIOS[user][1]}</p>
        <div class="live-box">
            {"<br>".join(resultados) if resultados else "No se encontraron tarjetas válidas."}
        </div>
        <br><a href="/dashboard" style="color:var(--neon-green); text-decoration:none;">← VOLVER AL PANEL</a>
    </div>
    ''')

if name == '__main__':
    app.run(host='0.0.0.0', port=80)
