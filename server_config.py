from flask import Flask, render_template_string, request, redirect, url_for, session
import requests
import random

app = Flask(__name__)
app.secret_key = 'quickmoney_ultra_safe_2026'

# --- CONFIGURACIÓN DE PROXIES (DECODO) ---
# Reemplaza 'TU_PASSWORD' con el que sale en tu foto
PROXY_USER = "sp6jzqtaou"
PROXY_PASS = "rUd7t65FxkK+x3Flhr"
PROXY_HOST = "gate.decodo.com"
PROXY_PORT = "10001"

PROXIES = {
    "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}",
    "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
}

# --- BASE DE DATOS DE USUARIOS Y CRÉDITOS ---
# Formato: "usuario": ["password", créditos]
USUARIOS = {
    "mairo": ["1234", 1000],
    "test": ["pago123", 50]
}

ESTILOS = '''
<style>
    :root { --neon-green: #00ff88; --dark-bg: #050505; }
    body { background: var(--dark-bg); color: white; font-family: sans-serif; text-align: center; }
    .card { background: #121212; border: 1px solid #333; border-radius: 15px; padding: 25px; margin: 20px auto; max-width: 600px; }
    input, textarea { width: 90%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #444; color: var(--neon-green); border-radius: 8px; }
    .btn { background: var(--neon-green); color: black; border: none; padding: 15px 30px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 95%; }
    .stat { display: inline-block; margin: 10px; padding: 15px; background: #1a1a1a; border-radius: 10px; border: 1px solid #333; }
</style>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u in USUARIOS and USUARIOS[u][0] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string(f'{ESTILOS}<div class="card"><h2>💸 QUICK MONEY</h2><form method="POST"><input name="u" placeholder="Usuario"><input type="password" name="p" placeholder="Password"><button class="btn">ENTRAR</button></form></div>')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user_data = USUARIOS[session['user']]
    return render_template_string(f'''
    {ESTILOS}
    <div class="card">
        <h1>💸 Quick Money 💸</h1>
        <p>(Bienvenido {session['user']})</p>
        <div class="stat">Créditos: <span style="color:var(--neon-green)">{user_data[1]}</span></div>
        <form method="POST" action="/process">
            <textarea name="lista" placeholder="CC|MM|YY|CVV" rows="10"></textarea>
            <button class="btn">INICIAR CHECKER (1 CRÉDITO X CC)</button>
        </form>
    </div>
    ''')

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
    
    user = session['user']
    lista = request.form.get('lista').splitlines()
    
    # Verificar si tiene créditos suficientes
    if USUARIOS[user][1] < len(lista):
        return "Créditos insuficientes. Recarga tu cuenta."

    lives = []
    # Descontar créditos
    USUARIOS[user][1] -= len(lista)

    # Aquí simulamos el check pasando por el proxy
    # En el siguiente paso conectaremos la API del Gateway real
    for cc in lista:
        try:
            # Esta línea hace que la petición pase por tus proxies de Decodo
            # r = requests.get("https://api.ipify.org", proxies=PROXIES, timeout=5)
            # Simulación de respuesta
            if len(cc) > 15: lives.append(cc)
        except:
            pass

    return render_template_string(f'''
    {ESTILOS}
    <div class="card">
        <h3>Resultados</h3>
        <p>Créditos restantes: {USUARIOS[user][1]}</p>
        <div style="text-align:left; background:#000; padding:10px; border-radius:10px; color:var(--neon-green)">
            {"<br>".join([f"✅ LIVE: {l}" for l in lives])}
        </div>
        <br><a href="/dashboard" style="color:white; text-decoration:none;">← Volver</a>
    </div>
    ''')

if name == '__main__':
    app.run(host='0.0.0.0', port=80)
