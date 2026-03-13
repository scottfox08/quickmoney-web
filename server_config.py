import os, random
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'mairo_gold_emperor_2026'

# --- BASE DE DATOS MAESTRA ---
DB = {
    "usuarios": {
        "mairo": {"pass": "1234", "saldo": 999999, "rango": "OWNER"},
        "cliente1": {"pass": "pago10", "saldo": 0, "rango": "VIP"}
    }
}

CSS = """
<style>
    :root { 
        --gold: #d4af37; 
        --gold-glow: rgba(212, 175, 55, 0.15);
        --bg: #050507; 
        --card: rgba(22, 26, 35, 0.95); 
        --green: #2ecc71; 
        --red: #ff4757; 
        --blue: #3498db; 
        --border: #2d323e; 
    }

    /* EL FONDO DE AURA DORADA */
    body { 
        background: radial-gradient(circle at center, #1a150a 0%, #050507 70%);
        background-attachment: fixed;
        color: #fff; 
        font-family: 'Segoe UI', sans-serif; 
        margin: 0; 
        padding: 10px; 
        min-height: 100vh;
    }

    .container { max-width: 550px; margin: auto; padding-bottom: 50px; }
    
    /* Efecto Glow en las Cards */
    .card { 
        background: var(--card); 
        border: 1px solid var(--border); 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 15px; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.8), 0 0 20px var(--gold-glow);
        backdrop-filter: blur(5px);
    }

    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 15px; display: block; letter-spacing: 1px; }
    
    .system-console { background: #000; border: 1px solid #222; padding: 10px; border-radius: 6px; font-size: 11px; margin-bottom: 15px; color: #888; border-left: 4px solid var(--blue); box-shadow: inset 0 0 10px rgba(52, 152, 219, 0.1); }
    .blink { color: var(--red); font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 50% { opacity: 0.2; } }

    input, select, textarea { width: 100%; background: #08090d; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box; font-family: 'Consolas', monospace; font-size: 13px; transition: 0.3s; }
    input:focus { border-color: var(--gold); box-shadow: 0 0 10px var(--gold-glow); outline: none; }

    .btn { border: none; padding: 14px; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.3s; }
    .btn-verify { background: linear-gradient(135deg, #d4af37 0%, #aa8a2e 100%); color: #000; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3); }
    .btn-gen { background: #232730; color: #fff; border: 1px solid #333; margin-bottom: 10px; }
    .btn-add { background: rgba(122, 99, 45, 0.2); color: #ffeb3b; border: 1px solid #7a632d; margin-bottom: 10px; }
    .btn-admin { background: transparent; border: 1px solid var(--gold); color: var(--gold); margin-top: 10px; }
    .btn:hover { transform: scale(1.02); filter: brightness(1.1); }

    .grid-res { display: grid; grid-template-columns: 1fr; gap: 10px; }
    .box { border-radius: 8px; padding: 10px; font-family: monospace; font-size: 12px; min-height: 60px; }
    .live { border: 1px solid var(--green); background: rgba(46, 204, 113, 0.05); color: var(--green); }
    .dead { border: 1px solid var(--red); background: rgba(255, 71, 87, 0.05); color: var(--red); }
    
    .badge-saldo { background: linear-gradient(45deg, #1e2533, #0d0f14); padding: 8px 20px; border-radius: 30px; border: 1px solid var(--gold); color: var(--gold); font-weight: bold; font-size: 12px; box-shadow: 0 0 15px var(--gold-glow); }
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px;text-align:center; border-top: 4px solid var(--gold);"> <h2 style="letter-spacing:3px; margin-bottom:20px;">🦁 QUICK MONEY</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required style="margin-top:10px;"><button class="btn btn-verify" style="margin-top:15px;">INGRESAR AL TRONO</button></form></div></body></html>')

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
            a = request.form.get('anio') if request.form.get('anio') != "RANDOM" else str(random.randint(26,30))
            cards.append(f"{cc}|{m}|{a}|{random.randint(100,999)}")
        gen_res = "\n".join(cards)

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <span style="letter-spacing:1px; color:#aaa;">OWNER: <b style="color:#fff;">{session['user'].upper()}</b></span>
            <div class="badge-saldo">BALANCE: ${u_data['saldo']}</div>
        </div>

        <div class="system-console">
            [SYS]: Bridge Amazon AWS Connected... <br>
            [STATUS]: <span class="blink">ERROR: COOKIE EXPIRED (REPLACE NOW)</span>
        </div>

        <div class="card">
            <span class="card-h">🪄 GENERADOR ELITE</span>
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
                <textarea id="gen_area" rows="5" readonly style="color:var(--gold); border-color:#443a1e;">{gen_res}</textarea>
            </form>
        </div>

        <div class="card">
            <span class="card-h">🛡️ VERIFICADOR (COOKIE GATE)</span>
            <label>AMAZON COOKIE</label>
            <input placeholder="Paste session cookie here...">
            <label>LISTA DE TARJETAS</label>
            <textarea id="check_list" rows="5" placeholder="CC|MM|YY|CVV"></textarea>
            <button class="btn btn-verify">🚀 INICIAR VALIDACIÓN</button>
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

        { f'<a href="/admin" class="btn btn-admin" style="display:block; text-align:center; text-decoration:none;">⚙️ PANEL DE CONTROL MASTER</a>' if u_data['rango'] == 'OWNER' else '' }
        
        <a href="/logout" style="display:block; text-align:center; color:#555; text-decoration:none; font-size:11px; margin-top:25px;">LOGOUT SYSTEM</a>
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
    return render_template_string(f'<html><head>{CSS}</head><body><div class="container" style="margin-top:50px;"><div class="card" style="border-top: 4px solid var(--gold);"><h2>⚙️ GESTIÓN DE SALDO</h2><form method="POST"><label>CLIENTE</label><select name="u_target">{" ".join([f"<option value='{u}'>{u} (${DB['usuarios'][u]['saldo']})</option>" for u in DB["usuarios"]])}</select><label>AGREGAR CRÉDITOS ($)</label><input type="number" name="amount" required><button class="btn btn-verify">CARGAR SALDO</button></form><br><a href="/panel" style="color:var(--gold); text-decoration:none;">← Volver al Panel</a></div></div></body></html>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
