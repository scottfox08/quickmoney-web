import os, random
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'mairo_final_boss_2026'

# --- DB DE USUARIOS ---
DB = {"usuarios": {"mairo": {"pass": "1234", "saldo": 999999, "rango": "OWNER"}}}

CSS = """
<style>
    :root { --gold: #d4af37; --bg: #0c0e14; --card: #161a23; --green: #2ecc71; --red: #e74c3c; --blue: #3498db; --border: #2d323e; }
    body { background: var(--bg); color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; }
    .container { max-width: 550px; margin: auto; padding-bottom: 50px; }
    
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 15px; display: block; }
    
    input, textarea { width: 100%; background: #0d0f14; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box; font-family: 'Consolas', monospace; font-size: 13px; }
    
    /* Consola de Sistema (Cookie Status) */
    .system-log { background: #000; border: 1px solid #222; padding: 10px; border-radius: 6px; font-size: 11px; margin-bottom: 15px; color: #888; border-left: 4px solid var(--blue); }
    .status-error { color: var(--red); font-weight: bold; animation: blink 1s infinite; }
    @keyframes blink { 50% { opacity: 0.5; } }

    /* Contenedores de Resultados */
    .res-container { display: grid; grid-template-columns: 1fr; gap: 10px; }
    .res-box { border-radius: 8px; padding: 10px; font-family: monospace; font-size: 12px; min-height: 80px; }
    .box-live { border: 1px solid var(--green); background: rgba(46, 204, 113, 0.05); color: var(--green); }
    .box-dead { border: 1px solid var(--red); background: rgba(231, 76, 60, 0.05); color: var(--red); }

    .btn { border: none; padding: 14px; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; width: 100%; transition: 0.3s; }
    .btn-verify { background: linear-gradient(45deg, #1e3d2f, #2ecc71); color: #fff; margin-top: 10px; }
    .badge { background: #1e2533; padding: 6px 15px; border-radius: 20px; border: 1px solid var(--gold); color: var(--gold); font-weight: bold; font-size: 12px; }
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:300px;text-align:center;"><h2>🦁 QUICK MONEY</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn btn-verify">LOGIN</button></form></div></body></html>')

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    if u in DB["usuarios"] and DB["usuarios"][u]['pass'] == p:
        session['user'] = u
    return redirect(url_for('panel'))

@app.route('/panel')
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = DB["usuarios"][session['user']]
    
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <span>OWNER: <b>{session['user'].upper()}</b></span>
            <div class="badge">SALDO: ${u_data['saldo']}</div>
        </div>

        <div class="system-log">
            [SISTEMA]: Conectado a Gate Amazon... <br>
            [STATUS]: <span class="status-error">ERROR: COOKIE EXPIRED OR INVALID</span>
        </div>

        <div class="card">
            <span class="card-h">🪄 GENERADOR PRO</span>
            <input id="bin" placeholder="BIN (414720)">
            <button class="btn" style="background:#2d4452; color:#fff;" onclick="alert('Generando...')">GENERAR CC</button>
        </div>

        <div class="card">
            <span class="card-h">🛡️ VERIFICADOR (COOKIE METHOD)</span>
            <textarea id="lista" rows="5" placeholder="Pega tu lista aquí..."></textarea>
            <button class="btn btn-verify" onclick="alert('Validando tarjetas con la sesión de Amazon...')">🚀 INICIAR VERIFICACIÓN</button>
        </div>

        <div class="res-container">
            <div class="card box-live">
                <span class="card-h" style="color:var(--green); border-color:var(--green);">LIVES ✅</span>
                <div id="lives_out">4147200012345678|08|28|999 -> [CHARGED $1.00]</div>
            </div>

            <div class="card box-dead">
                <span class="card-h" style="color:var(--red); border-color:var(--red);">REPROVADAS / DEAD ❌</span>
                <div id="dead_out">4737021122334455|12|25|111 -> [DECLINED]</div>
            </div>
        </div>

        <a href="/logout" style="display:block; text-align:center; color:var(--red); text-decoration:none; font-size:11px; margin-top:20px;">CERRAR SESIÓN DEL SISTEMA</a>
    </div>
    </body></html>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
