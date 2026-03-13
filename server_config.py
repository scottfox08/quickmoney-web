from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'quickmoney_admin_ultra_2026'

# --- CONFIGURACIÓN ---
# He subido una recreación optimizada del ilusionista a un servidor externo para carga instantánea.
LOGO_LINK = "https://images2.imgbox.com/7d/5d/q9Hn5lP4_o.png" 
PX = {"http": "http://sp6jzqtaou:rUd7t65FxkK+x3F1hr@gate.decodo.com:10001", "https": "http://sp6jzqtaou:rUd7t65FxkK+x3F1hr@gate.decodo.com:10001"}

# Sistema de Usuarios con Rango y Saldo
USUARIOS = {
    "mairo": {"pass": "1234", "credits": "ILIMITADO", "role": "ADMIN"},
    "test": {"pass": "4321", "credits": 50, "role": "USER"}
}

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

# --- DISEÑO BLACK & SILVER PREMIUM CON FUSIÓN DE IMAGEN ---
CSS = f"""
<style>
    :root {{ --silver: #e0e0e0; --black: #000000; --accent: #ffffff; --admin: #00ffcc; }}
    body {{ 
        background-color: var(--black); 
        /* Imagen de fondo sutil y fusionada con negro */
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), url('{LOGO_LINK}');
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
        background-size: cover;
        color: var(--silver); 
        font-family: 'Montserrat', 'Segoe UI', sans-serif; 
        margin: 0; 
    }}
    .overlay {{ 
        min-height: 100vh; 
        width: 100%; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
    }}
    .nav {{ 
        background-color: rgba(10, 10, 15, 0.95); 
        padding: 15px 30px; 
        border-bottom: 2px solid var(--accent); 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        width: 100%; 
        position: absolute; 
        top: 0; 
        box-sizing: border-box; 
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }}
    .container {{ display: flex; flex-wrap: wrap; justify-content: center; padding: 20px; gap: 20px; margin-top: 60px; }}
    .card {{ 
        background-color: rgba(10, 10, 10, 0.9); 
        border: 1px solid #444; 
        border-radius: 15px; 
        padding: 40px; 
        width: 90%; 
        max-width: 500px; 
        box-shadow: 0 0 30px rgba(0,0,0,0.8); 
        border-top: 3px solid var(--silver); 
        backdrop-filter: blur(8px); /* Efecto de cristal esmerilado */
    }}
    .tools-sidebar {{ 
        background: rgba(10,10,10,0.95); border: 1px solid #222; border-radius: 12px; padding: 20px; 
        width: 250px; border-left: 3px solid var(--admin); 
    }}
    .btn {{ 
        background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%); 
        color: var(--black); 
        border: none; 
        padding: 15px; 
        border-radius: 8px; 
        font-weight: bold; 
        width: 100%; 
        cursor: pointer; 
        text-transform: uppercase; 
        letter-spacing: 2px;
        transition: 0.3s; 
        box-shadow: 0 5px 10px rgba(0,0,0,0.3);
    }}
    .btn:hover {{ 
        transform: scale(1.03); 
        box-shadow: 0 8px 20px rgba(255,255,255,0.3); 
    }}
    .btn-tool {{ background: #1a1a1a; color: #eee; border: 1px solid #333; margin-bottom: 10px; text-align: left; padding: 10px; font-size: 13px; }}
    .btn-tool:hover {{ background: #333; border-color: var(--admin); }}
    input, textarea {{ width: 100%; background-color: rgba(0,0,0,0.85); color: #ffffff; border: 1px solid #555; padding: 15px; margin-bottom: 20px; border-radius: 8px; box-sizing: border-box; font-size: 16px;}}
    .badge {{ background: var(--admin); color: #000; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; vertical-align: middle; }}
    .live-row {{ 
        border-bottom: 1px solid #333; 
        padding: 15px; 
        font-family: 'Courier New', monospace; 
        display: flex; 
        justify-content: space-between; 
        align-items: center;
    }}
    .tag-live {{ 
        color: #ffffff; 
        font-weight: bold; 
        text-shadow: 0 0 8px #ffffff; 
        border: 1px solid #ffffff; 
        padding: 3px 10px; 
        border-radius: 4px; 
        font-size: 12px;
    }}
</style>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u in USUARIOS and USUARIOS[u]['pass'] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string(f'<html><head><title>QUICK MONEY | LOGIN</title>{CSS}</head><body><div class="overlay" style="justify-content:center; align-items:center;"><div class="card" style="max-width:350px; text-align:center;"><h1 style="letter-spacing:5px;">QUICK MONEY</h1><form method="POST"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASSWORD"><button class="btn">ACCEDER AL SISTEMA</button></form></div></div></body></html>')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    data = USUARIOS[u]
    return render_template_string(f"""
    <html><head><title>QUICK MONEY | PANEL</title>{CSS}</head>
    <body><div class="overlay"><div class="nav"><b>🦁 QUICK MONEY ELITE</b> <span>RANK: <span class="badge">{data['role']}</span> | SALDO: <b style="color:#fff;">{data['credits']}</b> | <a href="/logout" style="color:red; text-decoration:none;">SALIR</a></span></div>
    <div class="container">
        <div class="tools-sidebar">
            <h4 style="margin-top:0; color:white;">🛠️ HERRAMIENTAS</h4>
            <button class="btn btn-tool">💎 CC CHECKER (ACTIVO)</button>
            <button class="btn btn-tool">🔎 BIN LOOKUP</button>
            <button class="btn btn-tool">🛡️ PROXY TESTER</button>
            <button class="btn btn-tool">⚡ GEN V2 (PRÓXIMAMENTE)</button>
            <button class="btn btn-tool">👤 ADMIN PANEL</button>
        </div>
        <div class="card">
            <h3 style="text-align:center; letter-spacing:2px;">ESCAPE YOUR LIMITS</h3>
            <form method="POST" action="/process">
                <textarea name="lista" rows="10" placeholder="CC|MM|YY|CVV"></textarea>
                <button class="btn">INICIAR ESCANEO ÉLITE</button>
            </form>
        </div>
    </div></div></body></html>
    """)

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
    lista = request.form.get('lista','').splitlines()
    res = "".join([f"<div class='live-row'><span class='tag-live'>LIVE</span> <span>{cc}</span> <span>{get_bin(cc)}</span></div>" for cc in lista if len(cc)>10])
    return render_template_string(f'<html><head>{CSS}</head><body><div class="overlay"><div class="nav"><b>RESULTADOS</b> <a href="/dashboard" style="color:white; text-decoration:none;">← VOLVER</a></div><div class="card" style="max-width:700px; margin-top:100px;">{res if res else "No hay resultados"}<br><a href="/dashboard" class="btn" style="display:block; text-align:center; text-decoration:none; margin-top:20px;">NUEVA CONSULTA</a></div></div></body></html>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
