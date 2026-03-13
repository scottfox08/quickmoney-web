import os, random
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'mairo_emperor_ultimate_2026'

# --- BASE DE DATOS MAESTRA (Persistencia en Sesión para Admin) ---
DB = {
    "usuarios": {
        "mairo": {"pass": "1234", "saldo": 999999, "rango": "OWNER"},
        "cliente1": {"pass": "pago10", "saldo": 0, "rango": "VIP"}
    }
}

CSS = """
<style>
    :root { --gold: #d4af37; --bg: #0c0e14; --card: #161a23; --green: #2ecc71; --red: #e74c3c; --blue: #3498db; --border: #2d323e; }
    body { background: var(--bg); color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; }
    .container { max-width: 550px; margin: auto; padding-bottom: 50px; }
    
    /* Alerts & Console */
    .system-console { background: #000; border: 1px solid #222; padding: 10px; border-radius: 6px; font-size: 11px; margin-bottom: 15px; color: #888; border-left: 4px solid var(--blue); }
    .blink { color: var(--red); font-weight: bold; animation: pulse 1s infinite; }
    @keyframes pulse { 50% { opacity: 0.3; } }

    /* Cards */
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.6); }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 15px; display: block; }
    
    /* Inputs */
    label { font-size: 10px; color: #888; display: block; margin-bottom: 5px; }
    input, select, textarea { width: 100%; background: #0d0f14; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box; font-family: 'Consolas', monospace; font-size: 13px; }
    textarea { white-space: pre; overflow-x: auto; color: #00ffcc; line-height: 1.5; }

    /* Buttons */
    .btn { border: none; padding: 14px; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.3s; }
    .btn-verify { background: linear-gradient(45deg, #1e3d2f, #2ecc71); color: #fff; }
    .btn-gen { background: #2d4452; color: #fff; margin-bottom: 10px; }
    .btn-add { background: #7a632d; color: #ffeb3b; border: 1px solid #9e823a; margin-bottom: 10px; }
    .btn-admin { background: transparent; border: 1px solid var(--gold); color: var(--gold); margin-top: 10px; }

    /* Stats & Results */
    .grid-res { display: grid; grid-template-columns: 1fr; gap: 10px; }
    .box { border-radius: 8px; padding: 10px; font-family: monospace; font-size: 12px; min-height: 60px; }
    .live { border: 1px solid var(--green); background: rgba(46, 204, 113, 0.05); color: var(--green); }
    .dead { border: 1px solid var(--red); background: rgba(231, 76, 60, 0.05); color: var(--red); }
    
    .badge-saldo { background: #1e2533; padding: 6px 15px; border-radius: 20px; border: 1px solid var(--gold); color: var(--gold); font-weight: bold; font-size: 12px; }
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px;text-align:center;"><h2>🦁 QUICK MONEY</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required style="margin-top:10px;"><button class="btn btn-verify" style="margin-top:15px;">ACCEDER</button></form></div></body></html>')

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    if u in DB["usuarios"] and DB["usuarios"][u]['pass'] == p:
        session['user'] = u
    return redirect(url_for('panel'))

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = DB["usuarios"][session['user']]
    
    gen_res = ""
    if request.method == 'POST' and 'bin' in request.form:
        bin_val = request.form.get('bin')[:6]
        cant = int(request.form.get('cant', 10))
        cards = []
        for _ in range(cant):
            cc = bin_val + "".join([str(random.randint(0,9)) for _ in range(10)])
            m = request.form.get('mes') if request.form.get('mes') != "RANDOM" else f"{random.randint(1,12):02d}"
            a = request.form.get('anio') if request.form.get('anio') != "RANDOM" else str(random.randint(25,30))
            cards.append(f"{cc}|{m}|{a}|{random.randint(100,999)}")
        gen_res = "\n".join(cards)

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <span>OWNER: <b>{session['user'].upper()}</b></span>
            <div class="badge-saldo">SALDO: ${u_data['saldo']}</div>
        </div>

        <div class="system-console">
            [SYS]: Bridge Amazon AWS Connected... <br>
            [STATUS]: <span class="blink">ERROR: COOKIE EXPIRED (REPLACE NOW)</span>
        </div>

        <div class="card">
            <span class="card-h">🪄 GENERADOR DE TARJETAS</span>
            <form method="POST">
                <label>BIN</label>
                <input name="bin" placeholder="473702" value="{request.form.get('bin', '')}">
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <div><label>MES</label><select name="mes"><option>RANDOM</option>{" ".join([f'<option>{i:02d}</option>' for i in range(1,13)])}</select></div>
                    <div><label>AÑO</label><select name="anio"><option>RANDOM</option><option>2026</option><option>2027</option><option>2028</option></select></div>
                </div>
                <label>CANTIDAD</label>
                <input name="cant" type="number" value="10">
                <button name="action" value="gen" class="btn btn-gen">🪄 GENERAR</button>
                <button type="button" class="btn btn-add" onclick="document.getElementById('check_list').value += document.getElementById('gen_area').value + '\\n'; alert('¡Agregadas al Validador!')">➕ AGREGAR AL CHECKER</button>
                <textarea id="gen_area" rows="5" readonly>{gen_res}</textarea>
            </form>
        </div>

        <div class="card">
            <span class="card-h">🛡️ VERIFICADOR DE COOKIES</span>
            <label>AMAZON COOKIE</label>
            <input placeholder="Paste session cookie here...">
            <label>LISTA DE TARJETAS</label>
            <textarea id="check_list" rows="5" placeholder="CC|MM|YY|CVV"></textarea>
            <button class="btn btn-verify" onclick="alert('Validando... Cada tarjeta descuenta saldo.')">🚀 INICIAR VALIDACIÓN</button>
        </div>

        <div class="grid-res">
            <div class="card live">
                <span class="card-h" style="color:var(--green); border-color:var(--green);">LIVES ✅</span>
                <div id="lives_log">4147200000001234|08|2028|123 -> [LIVE] CHARGED $1.00</div>
            </div>
            <div class="card dead">
                <span class="card-h" style="color:var(--red); border-color:var(--red);">DEAD / REPROVADAS ❌</span>
                <div id="dead_log">Esperando validación...</div>
            </div>
        </div>

        { f'<a href="/admin" class="btn btn-admin" style="display:block; text-align:center; text-decoration:none;">⚙️ PANEL ADMINISTRAR SALDOS</a>' if u_data['rango'] == 'OWNER' else '' }
        
        <a href="/logout" style="display:block; text-align:center; color:var(--red); text-decoration:none; font-size:11px; margin-top:20px;">CERRAR SESIÓN</a>
    </div>
    </body></html>
    """)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or DB["usuarios"][session['user']]['rango'] != 'OWNER': return "DENEGADO"
    if request.method == 'POST':
        target = request.form.get('u_target')
        amount = int(request.form.get('amount', 0))
        if target in DB["usuarios"]: DB["usuarios"][target]['saldo'] += amount
    return render_template_string(f'<html><head>{CSS}</head><body><div class="container"><div class="card"><h2>⚙️ GESTIÓN DE SALDO</h2><form method="POST"><label>CLIENTE</label><select name="u_target">{" ".join([f"<option value='{u}'>{u} (${DB['usuarios'][u]['saldo']})</option>" for u in DB["usuarios"]])}</select><label>AGREGAR SALDO ($)</label><input type="number" name="amount" required><button class="btn btn-verify">CARGAR AHORA</button></form><br><a href="/panel" style="color:var(--gold); text-decoration:none;">← Volver al Panel</a></div></div></body></html>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
