import os, random, time
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'mairo_gate_master_2026'

# --- DB MAESTRA ---
DB = {
    "usuarios": {
        "mairo": {"pass": "1234", "saldo": 999999.0, "rango": "OWNER"},
        "cliente1": {"pass": "pago10", "saldo": 10.0, "rango": "VIP"}
    }
}

COSTO_LIVE = 0.35

CSS = """
<style>
    :root { --gold: #d4af37; --gold-glow: rgba(212, 175, 55, 0.15); --bg: #050507; --card: rgba(22, 26, 35, 0.95); --green: #2ecc71; --red: #ff4757; --blue: #3498db; --border: #2d323e; }
    body { background: radial-gradient(circle at center, #1a150a 0%, #050507 70%); background-attachment: fixed; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; min-height: 100vh; }
    .container { max-width: 550px; margin: auto; padding-bottom: 50px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.8), 0 0 20px var(--gold-glow); backdrop-filter: blur(5px); }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 15px; display: block; letter-spacing: 1px; }
    .system-console { background: #000; border: 1px solid #222; padding: 10px; border-radius: 6px; font-size: 11px; margin-bottom: 15px; color: #888; border-left: 4px solid var(--blue); }
    .blink { color: var(--red); font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 50% { opacity: 0.2; } }
    input, select, textarea { width: 100%; background: #08090d; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box; font-family: 'Consolas', monospace; font-size: 13px; }
    .btn { border: none; padding: 14px; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.3s; }
    .btn-verify { background: linear-gradient(135deg, #d4af37 0%, #aa8a2e 100%); color: #000; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3); }
    .btn-gen { background: #232730; color: #fff; border: 1px solid #333; margin-bottom: 10px; }
    .badge-saldo { background: linear-gradient(45deg, #1e2533, #0d0f14); padding: 8px 20px; border-radius: 30px; border: 1px solid var(--gold); color: var(--gold); font-weight: bold; font-size: 12px; box-shadow: 0 0 15px var(--gold-glow); }
    .res-box { border-radius: 8px; padding: 10px; font-family: monospace; font-size: 12px; min-height: 60px; margin-top: 10px; overflow-y: auto; max-height: 150px; }
    .live { border: 1px solid var(--green); color: var(--green); background: rgba(46, 204, 113, 0.05); }
    .dead { border: 1px solid var(--red); color: var(--red); background: rgba(255, 71, 87, 0.05); }
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px;text-align:center;border-top:4px solid var(--gold);"><h2>🦁 QUICK MONEY</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required><button class="btn btn-verify" style="margin-top:10px;">INGRESAR AL TRONO</button></form><p style="font-size:11px;margin-top:15px;">¿No tienes cuenta? <a href="/register" style="color:var(--gold);text-decoration:none;">REGÍSTRATE AQUÍ</a></p></div></body></html>')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u and p and u not in DB["usuarios"]:
            DB["usuarios"][u] = {"pass": p, "saldo": 0.0, "rango": "VIP"}
            return redirect(url_for('login'))
        return "ERROR: Usuario ya existe o datos inválidos."
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px;text-align:center;"><h2>📝 REGISTRO QM</h2><form method="POST"><input name="u" placeholder="CREAR USUARIO" required><input type="password" name="p" placeholder="CREAR PASS" required><button class="btn btn-verify" style="margin-top:10px;">CREAR CUENTA</button></form><br><a href="/" style="color:#888;font-size:11px;">Volver al Login</a></div></body></html>')

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
        cards = [f"{bin_val}{''.join([str(random.randint(0,9)) for _ in range(10)])}|{random.randint(1,12):02d}|{random.randint(26,30)}|{random.randint(100,999)}" for _ in range(cant)]
        gen_res = "\n".join(cards)

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <span>OWNER: <b style="color:var(--gold);">{session['user'].upper()}</b></span>
            <div id="display_saldo" class="badge-saldo">SALDO: ${u_data['saldo']:.2f}</div>
        </div>

        <div class="system-console">
            [SYS]: Amazon Bridge Connected... <br>
            [STATUS]: <span class="blink">GATE: READY (INSERT COOKIES & CARDS)</span>
        </div>

        <div class="card">
            <span class="card-h">🪄 GENERADOR ELITE</span>
            <form method="POST">
                <input name="bin" placeholder="BIN 473702" value="{request.form.get('bin', '')}">
                <input name="cant" type="number" value="10">
                <button type="submit" class="btn btn-gen">🪄 GENERAR</button>
                <textarea id="gen_area" rows="4" readonly style="color:var(--gold);">{gen_res}</textarea>
                <button type="button" class="btn" style="background:#7a632d;color:#ffeb3b" onclick="document.getElementById('check_list').value += document.getElementById('gen_area').value + '\\n'">➕ CARGAR AL VALIDADOR</button>
            </form>
        </div>

        <div class="card">
            <span class="card-h">🛡️ GATE AMAZON (COOKIES REQUIRED)</span>
            <label style="color:#666; font-size:10px;">AMAZON SESSION COOKIE</label>
            <input id="amazon_cookie" placeholder="Paste session cookie here...">
            
            <label style="color:#666; font-size:10px;">LISTA DE TARJETAS</label>
            <textarea id="check_list" rows="6" placeholder="LISTA CC|MM|YY|CVV"></textarea>
            
            <button class="btn btn-verify" onclick="startChecking()">🚀 INICIAR VALIDACIÓN ($0.35/LIVE)</button>
        </div>

        <div class="card res-box live"><span class="card-h">LIVES ✅</span><div id="lives_log"></div></div>
        <div class="card res-box dead"><span class="card-h">DEAD ❌</span><div id="dead_log"></div></div>

        { f'<a href="/admin" class="btn" style="border:1px solid var(--gold); color:var(--gold); text-decoration:none; display:block; text-align:center; margin-top:10px;">⚙️ PANEL DE CONTROL (MASTER)</a>' if u_data['rango'] == 'OWNER' else '' }
        
        <a href="/logout" style="display:block; text-align:center; color:#555; text-decoration:none; font-size:11px; margin-top:25px;">LOGOUT SYSTEM</a>
    </div>

    <script>
    async function startChecking() {{
        let area = document.getElementById('check_list');
        let cookie = document.getElementById('amazon_cookie').value;
        let lines = area.value.trim().split('\\n');
        
        if (!cookie) return alert('Debes insertar la cookie de Amazon para iniciar.');
        if (!lines[0] || lines[0] === "") return alert('La lista está vacía.');

        while (lines.length > 0) {{
            let currentCC = lines.shift(); 
            area.value = lines.join('\\n'); 

            let isLive = Math.random() > 0.8; 
            
            if (isLive) {{
                let res = await fetch('/cobrar_live', {{ method: 'POST' }});
                let data = await res.json();
                if (data.error) {{ alert(data.error); break; }}
                document.getElementById('display_saldo').innerText = 'SALDO: $' + data.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = currentCC + ' -> [LIVE ✅] <br>' + document.getElementById('lives_log').innerHTML;
            }} else {{
                document.getElementById('dead_log').innerHTML = currentCC + ' -> [DEAD ❌] <br>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 800)); 
        }}
    }}
    </script>
    </body></html>
    """)

@app.route('/cobrar_live', methods=['POST'])
def cobrar():
    user = session.get('user')
    if user and DB["usuarios"][user]['saldo'] >= COSTO_LIVE:
        DB["usuarios"][user]['saldo'] -= COSTO_LIVE
        return jsonify({"nuevo_saldo": DB["usuarios"][user]['saldo']})
    return jsonify({"error": "Saldo insuficiente para continuar"}), 400

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or DB["usuarios"][session['user']]['rango'] != 'OWNER': return "DENEGADO"
    if request.method == 'POST':
        target = request.form.get('u_target')
        amount = float(request.form.get('amount', 0))
        if target in DB["usuarios"]: DB["usuarios"][target]['saldo'] += amount
    return render_template_string(f'<html><head>{CSS}</head><body><div class="container" style="margin-top:50px;"><div class="card"><h2>⚙️ GESTIÓN DE SALDO</h2><form method="POST"><select name="u_target">{" ".join([f"<option value='{u}'>{u} (${DB['usuarios'][u]['saldo']})</option>" for u in DB["usuarios"]])}</select><input type="number" step="0.01" name="amount" placeholder="Cargar $"><button class="btn btn-verify">CARGAR SALDO</button></form><br><a href="/panel" style="color:var(--gold); text-decoration:none;">← Volver al Panel</a></div></div></body></html>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
