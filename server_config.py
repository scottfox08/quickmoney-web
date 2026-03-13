import os
import random
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'mairo_king_owner_2026'

# --- BASE DE DATOS DE CLIENTES (Aquí agregas a tus compradores) ---
# Formato: "usuario": {"pass": "clave", "plan": "GOLD/VIP", "expira": "30 Dias"}
CLIENTES = {
    "mairo": {"pass": "1234", "plan": "OWNER", "status": "ACTIVO"},
    "cliente1": {"pass": "compra01", "plan": "VIP", "status": "ACTIVO"},
    "test": {"pass": "demo", "plan": "FREE", "status": "EXPIRADO"}
}

LOGO_LINK = "https://images2.imgbox.com/7d/5d/q9Hn5lP4_o.png"

CSS = f"""
<style>
    :root {{ --gold: #f39c12; --green: #2ecc71; --red: #e74c3c; --bg-card: #15181f; }}
    body {{ background: #000 url('{LOGO_LINK}') no-repeat center fixed; background-size: cover; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; }}
    .overlay {{ background: rgba(0,0,0,0.92); min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 20px; }}
    .main-card {{ background: var(--bg-card); border: 1px solid #334; border-radius: 12px; padding: 25px; width: 100%; max-width: 500px; box-shadow: 0 15px 50px #000; border-top: 3px solid var(--gold); }}
    .label {{ color: var(--gold); font-size: 10px; font-weight: bold; text-transform: uppercase; margin: 15px 0 5px; display: block; }}
    input, textarea, select {{ width: 100%; background: #080a0e; border: 1px solid #2a2e38; color: #fff; padding: 12px; border-radius: 6px; box-sizing: border-box; font-size: 13px; }}
    .btn-group {{ display: flex; gap: 10px; margin: 15px 0; }}
    .btn {{ flex: 1; border: none; padding: 14px; border-radius: 5px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; transition: 0.2s; }}
    .btn-gen {{ background: var(--green); color: #fff; }}
    .btn-check {{ background: var(--gold); color: #000; }}
    .status-active {{ color: var(--green); font-size: 10px; font-weight: bold; }}
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;justify-content:center;align-items:center;"><div class="main-card" style="max-width:320px;text-align:center;"><h2>🦁 QUICK MONEY LOGIN</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="CONTRASEÑA" required style="margin-top:10px;"><button class="btn btn-check" style="width:100%;margin-top:20px;">INGRESAR AL SISTEMA</button></form></div></body></html>')

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    if u in CLIENTES and CLIENTES[u]['pass'] == p:
        if CLIENTES[u]['status'] == "ACTIVO":
            session['user'] = u
            return redirect(url_for('dashboard'))
        else:
            return "<h1>TU LICENCIA HA EXPIRADO. CONTACTA A MAIRO.</h1>"
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    u_info = CLIENTES[session['user']]
    
    results = []
    if request.method == 'POST':
        action = request.form.get('action')
        if action == "gen":
            bin_p = request.form.get('bin')[:6]
            for _ in range(10):
                cc = bin_p + "".join([str(random.randint(0,9)) for _ in range(10)])
                results.append(f"{cc}|{random.randint(1,12):02d}|{random.randint(25,30)}|{random.randint(100,999)}")
    
    return render_template_string(f"""
    <html><head><title>PANEL MASTER | QM</title>{CSS}</head>
    <body><div class="overlay">
        <div class="main-card">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #2a2e38; padding-bottom:10px;">
                <span>USUARIO: <b>{session['user'].upper()}</b></span>
                <span class="status-active">PLAN: {u_info['plan']}</span>
            </div>

            <form method="POST">
                <span class="label">AMAZON COOKIE SESSION</span>
                <input name="cookie" placeholder="Paste Amazon Cookie here..." required>
                
                <span class="label">BINS / GENERADOR</span>
                <div style="display:flex; gap:5px;">
                    <input name="bin" placeholder="414720" style="flex:2;">
                    <button name="action" value="gen" class="btn btn-gen" style="flex:1;">AUTOGEN</button>
                </div>

                <span class="label">LISTA DE TARJETAS (1 POR LÍNEA)</span>
                <textarea name="lista" rows="6" placeholder="CC|MM|YY|CVV">{"\\n".join(results)}</textarea>

                <div class="btn-group">
                    <button name="action" value="check" class="btn btn-check" onclick="alert('Iniciando Motor de Validación...')">🚀 VALIDAR EN AMAZON</button>
                    <a href="/logout" class="btn" style="background:#444; text-decoration:none; text-align:center; padding-top:14px;">SALIR</a>
                </div>
            </form>
            <p style="text-align:center; font-size:9px; color:#555;">&copy; 2026 QUICK MONEY ELITE - PROPIEDAD DE MAIRO</p>
        </div>
    </div></body></html>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
