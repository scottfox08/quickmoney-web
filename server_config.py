import os
import random
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'quickmoney_king_ultra_v5'

# --- CONFIGURACIÓN ---
USUARIOS = {"mairo": "1234"}
LOGO_LINK = "https://images2.imgbox.com/7d/5d/q9Hn5lP4_o.png"

# --- DISEÑO ---
CSS = f"""
<style>
    body {{ background: #000 url('{LOGO_LINK}') no-repeat center fixed; background-size: cover; color: #fff; font-family: sans-serif; margin: 0; }}
    .overlay {{ background: rgba(0,0,0,0.85); min-height: 100vh; display: flex; flex-direction: column; }}
    .nav {{ background: #0a0a0a; padding: 15px 30px; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }}
    .main-wrapper {{ display: flex; flex: 1; }}
    .sidebar {{ width: 250px; background: rgba(5,5,5,0.9); border-right: 1px solid #222; padding: 20px; }}
    .nav-btn {{ background: #111; border: 1px solid #333; color: #888; padding: 12px; border-radius: 8px; cursor: pointer; width: 100%; margin-bottom: 10px; font-weight: bold; text-align: left; }}
    .nav-btn.active {{ background: #fff; color: #000; }}
    .content {{ flex: 1; padding: 40px; }}
    .panel {{ background: rgba(15,15,15,0.95); border: 1px solid #333; border-radius: 20px; padding: 30px; max-width: 700px; margin: auto; }}
    .btn-main {{ background: #fff; color: #000; border: none; padding: 15px; border-radius: 8px; width: 100%; font-weight: bold; cursor: pointer; text-transform: uppercase; }}
    textarea, input {{ width: 100%; background: #000; border: 1px solid #333; color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 15px; box-sizing: border-box; }}
</style>
"""

@app.route('/')
def index():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;"><div class="panel" style="max-width:320px;text-align:center;"><h1>QUICK MONEY</h1><form method="POST" action="/login_check"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn-main">ENTRAR</button></form></div></body></html>')

@app.route('/login_check', methods=['POST'])
def login_check():
    u, p = request.form.get('u'), request.form.get('p')
    if u == "mairo" and p == "1234":
        session['user'] = u
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('index'))
    
    gen_results = ""
    if request.method == 'POST' and 'bin' in request.form:
        bin_str = request.form.get('bin')[:6]
        res = []
        for _ in range(10):
            cc = bin_str + "".join([str(random.randint(0,9)) for _ in range(10)])
            res.append(f"{cc}|{random.randint(1,12):02d}|{random.randint(25,30)}|{random.randint(100,999)}")
        gen_results = "\\n".join(res)

    return render_template_string(f"""
    <html><head><title>DASHBOARD</title>{CSS}</head>
    <body><div class="overlay">
        <div class="nav"><b>🦁 QUICK MONEY SYSTEM</b> <span>MAIRO [ADMIN] | Saldo: <b>∞</b></span></div>
        <div class="main-wrapper">
            <div class="sidebar">
                <button class="nav-btn active">💎 CC CHECKER</button>
                <button class="nav-btn">⚡ GENERADOR V2</button>
                <a href="/logout" style="color:red;text-decoration:none;padding:10px;display:block;">SALIR</a>
            </div>
            <div class="content">
                <div class="panel">
                    <h3>⚡ GENERADOR & CHECKER</h3>
                    <form method="POST">
                        <input name="bin" placeholder="BIN (6 dígitos)">
                        <button class="btn-main">GENERAR TARJETAS</button>
                    </form>
                    <textarea rows="10" readonly style="margin-top:20px;">{gen_results}</textarea>
                </div>
            </div>
        </div>
    </div></body></html>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
