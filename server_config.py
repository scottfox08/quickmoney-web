import os
import random
import requests
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'quickmoney_real_checker_2026'

USUARIOS = {"mairo": "1234"}
LOGO_LINK = "https://images2.imgbox.com/7d/5d/q9Hn5lP4_o.png"

# --- FUNCIÓN DE VALIDACIÓN REAL (SIMULADA HASTA TENER API) ---
def validar_con_amazon(cc, cookie):
    # Aquí es donde el script "ataca" a Amazon usando la cookie.
    # Por ahora, para que veas cómo funciona, daremos resultados aleatorios.
    status = random.choice(["LIVE ✅", "DEAD ❌", "CC ERROR ⚠️"])
    return f"{cc} -> {status}"

CSS = f"""
<style>
    :root {{ --gold: #f39c12; --green: #2ecc71; --red: #e74c3c; }}
    body {{ background: #000 url('{LOGO_LINK}') no-repeat center fixed; background-size: cover; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; }}
    .overlay {{ background: rgba(0,0,0,0.9); min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 30px; }}
    .main-card {{ background: #1a1d24; border: 1px solid #334; border-radius: 10px; padding: 25px; width: 100%; max-width: 450px; border-top: 3px solid var(--gold); }}
    .label {{ color: var(--gold); font-size: 11px; font-weight: bold; display: block; margin: 10px 0 5px; }}
    input, select, textarea {{ width: 100%; background: #0a0c10; border: 1px solid #2a2e38; color: #fff; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-size: 13px; }}
    .btn-group {{ display: flex; gap: 10px; margin-top: 15px; }}
    .btn {{ flex: 1; border: none; padding: 12px; border-radius: 4px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; }}
    .btn-gen {{ background: var(--green); }}
    .btn-add {{ background: var(--gold); color: #000; }}
    .results {{ background: #000; border: 1px solid #2a2e38; color: var(--green); font-family: monospace; font-size: 12px; margin-top: 15px; }}
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;justify-content:center;align-items:center;"><div class="main-card" style="max-width:300px;text-align:center;"><h1>QUICK MONEY</h1><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn btn-gen" style="width:100%;">ENTRAR</button></form></div></body></html>')

@app.route('/auth', methods=['POST'])
def auth():
    if request.form.get('u') == "mairo" and request.form.get('p') == "1234":
        session['user'] = "mairo"
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    
    output = ""
    if request.method == 'POST':
        action = request.form.get('action')
        cookie = request.form.get('cookie')
        
        if action == "generar":
            bin_in = request.form.get('bin')[:6]
            res = []
            for _ in range(5):
                cc = bin_in + "".join([str(random.randint(0,9)) for _ in range(10)])
                res.append(f"{cc}|{random.randint(1,12):02d}|{random.randint(25,30)}|{random.randint(100,999)}")
            output = "\\n".join(res)
            
        elif action == "validar":
            lista = request.form.get('lista').splitlines()
            res = []
            for item in lista:
                res.append(validar_con_amazon(item, cookie))
            output = "\\n".join(res)

    return render_template_string(f"""
    <html><head><title>QUICK MONEY | REAL CHECKER</title>{CSS}</head>
    <body><div class="overlay">
        <div class="main-card">
            <form method="POST">
                <span class="label">COOKIE 1 (AMAZON USA)</span>
                <input name="cookie" placeholder="Paste Amazon Cookie here..." value="{request.form.get('cookie', '')}">
                
                <div style="background:rgba(0,0,0,0.3); padding:15px; border-radius:8px;">
                    <span class="label" style="margin-top:0;">BINS</span>
                    <input name="bin" placeholder="414720" value="{request.form.get('bin', '')}">
                    <button name="action" value="generar" class="btn btn-gen" style="width:100%;">🪄 AUTOGEN CC</button>
                </div>

                <span class="label">TARJETAS PARA VALIDAR</span>
                <textarea name="lista" rows="6" placeholder="CC|MM|YY|CVV">{output}</textarea>

                <div class="btn-group">
                    <button name="action" value="validar" class="btn btn-add">🚀 INICIAR VALIDACIÓN</button>
                    <button type="button" class="btn" style="background:#444;" onclick="window.location.href='/dashboard'">🗑️ LIMPIAR</button>
                </div>
            </form>
            <p style="text-align:center; font-size:10px; color:#555; margin-top:15px;">MAIRO ADMIN | SALDO: ∞ | <a href="/logout" style="color:var(--red)">SALIR</a></p>
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
