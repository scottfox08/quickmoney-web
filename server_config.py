import os
import random
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = 'quickmoney_ultra_final_2026'

# --- CONFIGURACIÓN DE USUARIO ---
USUARIOS = {"mairo": {"pass": "1234", "role": "GOLDEN ADMIN", "credits": "∞"}}
LOGO_LINK = "https://images2.imgbox.com/7d/5d/q9Hn5lP4_o.png"

# --- LÓGICA DEL GENERADOR ---
def generar_cc(bin_input):
    bin_str = bin_input.replace(" ", "").replace("x", "")[:6]
    if not bin_str.isdigit() or len(bin_str) < 6: return ["BIN INVÁLIDO (Mínimo 6 dígitos)"]
    cards = []
    for _ in range(10):
        cc = bin_str
        while len(cc) < 16: cc += str(random.randint(0, 9))
        mes = str(random.randint(1, 12)).zfill(2)
        anio = str(random.randint(25, 30))
        cvv = str(random.randint(100, 999))
        cards.append(f"{cc}|{mes}|{anio}|{cvv}")
    return cards

# --- DISEÑO ÉLITE ---
CSS = f"""
<style>
    :root {{ --accent: #00ffcc; --silver: #e0e0e0; }}
    body {{ background: #000 url('{LOGO_LINK}') no-repeat center center fixed; background-size: cover; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; }}
    .overlay {{ background: rgba(0,0,0,0.85); height: 100vh; display: flex; flex-direction: column; }}
    .nav {{ background: rgba(10,10,10,0.9); padding: 15px 30px; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }}
    .main-wrapper {{ display: flex; flex: 1; }}
    .sidebar {{ width: 250px; background: rgba(5,5,5,0.9); border-right: 1px solid #222; padding: 20px; display: flex; flex-direction: column; gap: 10px; }}
    .nav-btn {{ background: #111; border: 1px solid #333; color: #888; padding: 12px; text-align: left; border-radius: 8px; cursor: pointer; transition: 0.3s; width: 100%; font-weight: bold; }}
    .nav-btn:hover, .nav-btn.active {{ background: #fff; color: #000; box-shadow: 0 0 15px #fff; }}
    .content {{ flex: 1; padding: 40px; display: flex; justify-content: center; }}
    .panel {{ background: rgba(15,15,15,0.95); border: 1px solid #333; border-radius: 20px; padding: 30px; width: 100%; max-width: 700px; display: none; backdrop-filter: blur(10px); }}
    .panel.active {{ display: block; animation: fadeIn 0.4s; }}
    .btn-main {{ background: #fff; color: #000; border: none; padding: 15px; border-radius: 8px; width: 100%; font-weight: bold; cursor: pointer; text-transform: uppercase; margin-top: 10px; }}
    textarea, input {{ width: 100%; background: #000; border: 1px solid #333; color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box; font-size: 16px; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; }} }}
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;"><div class="panel" style="display:block;max-width:320px;text-align:center;"><h1>QUICK MONEY</h1><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn-main">ENTRAR</button></form></div></body></html>')

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    if u in USUARIOS and USUARIOS[u]['pass'] == p:
        session['user'] = u
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    gen_results = ""
    active_panel = "checker"
    
    if request.method == 'POST' and 'bin' in request.form:
        gen_results = "\\n".join(generar_cc(request.form.get('bin')))
        active_panel = "gen"

    return render_template_string(f"""
    <html><head><title>QUICK MONEY ELITE</title>{CSS}
    <script>
        function openTool(name) {{
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.currentTarget.classList.add('active');
        }}
    </script>
    </head>
    <body>
    <div class="overlay">
        <div class="nav"><b>🦁 QUICK MONEY SYSTEM</b> <span>{u} [ADMIN] | Saldo: <b style="color:var(--accent)">{USUARIOS[u]['credits']}</b></span></div>
        <div class="main-wrapper">
            <div class="sidebar">
                <button class="nav-btn {'active' if active_panel == 'checker' else ''}" onclick="openTool('checker')">💎 CC CHECKER</button>
                <button class="nav-btn {'active' if active_panel == 'gen' else ''}" onclick="openTool('gen')">⚡ GENERADOR V2</button>
                <button class="nav-btn" onclick="openTool('proxy')">🛡️ PROXY STATUS</button>
                <a href="/logout" style="color:red; text-decoration:none; margin-top:20px; font-size:12px; text-align:center;">CERRAR SESIÓN</a>
            </div>
            <div class="content">
                <div id="checker" class="panel {'active' if active_panel == 'checker' else ''}">
                    <h3>CC CHECKER ELITE (GATE 1)</h3>
                    <textarea rows="8" placeholder="CC|MM|YY|CVV"></textarea>
                    <button class="btn-main" onclick="alert('Conectando con API de Pago...')">INICIAR CHECK</button>
                </div>
                <div id="gen" class="panel {'active' if active_panel == 'gen' else ''}">
                    <h3>⚡ GENERADOR PRO</h3>
                    <form method="POST">
                        <input name="bin" placeholder="Introduce BIN (6 dígitos)" value="{request.form.get('bin', '')}">
                        <button class="btn-main">GENERAR TARJETAS</button>
                    </form>
                    <textarea rows="8" readonly style="margin-top:20px;">{gen_results}</textarea>
                </div>
                <div id="proxy" class="panel">
                    <h3>🛡️ STATUS DE RED</h3>
                    <p>Proxy: <span style="color:var(--accent)">DECODO VIP ✅</span></p>
                    <p>Ubicación: <span style="color:var(--accent)">RESIDENCIAL USA</span></p>
                </div>
            </div>
        </div>
    </div>
    </body></html>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
