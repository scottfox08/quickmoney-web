import os, random, time, json
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'mairo_v20_final_elite'

# --- BASE DE DATOS LOCAL ---
DB_FILE = 'database.json'

def load_db():
    if not os.path.exists(DB_FILE):
        db = {"usuarios": {"mairo": {"pass": "1234", "saldo": 999999.0, "rango": "OWNER"}}}
        save_db(db)
        return db
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

COSTO_LIVE = 0.35

CSS = """
<style>
    :root { --gold: #d4af37; --bg: #050507; --card: rgba(22, 26, 35, 0.95); --green: #2ecc71; --red: #ff4757; --border: #2d323e; }
    body { background: radial-gradient(circle at center, #1a150a 0%, #050507 70%); background-attachment: fixed; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; min-height: 100vh; }
    .container { max-width: 550px; margin: auto; padding-bottom: 50px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); backdrop-filter: blur(5px); }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 15px; display: block; }
    input, select, textarea { width: 100%; background: #08090d; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box; font-family: 'Consolas', monospace; font-size: 13px; }
    .btn { border: none; padding: 14px; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.3s; margin-top: 5px; }
    .btn-verify { background: linear-gradient(135deg, #d4af37 0%, #aa8a2e 100%); color: #000; }
    .badge-saldo { background: #1e2533; padding: 8px 20px; border-radius: 30px; border: 1px solid var(--gold); color: var(--gold); font-weight: bold; font-size: 12px; }
    .res-box { border-radius: 8px; padding: 10px; font-family: monospace; font-size: 12px; min-height: 80px; margin-top: 10px; overflow-y: auto; max-height: 200px; border: 1px solid #333; }
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px;text-align:center;border-top:4px solid var(--gold);"><h2>🦁 QUICK MONEY</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required><button class="btn btn-verify" style="width:100%">INGRESAR</button></form><p style="font-size:11px;margin-top:15px;"><a href="/register" style="color:var(--gold);text-decoration:none;">REGÍSTRATE</a></p></div></body></html>')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        db = load_db()
        if u and p and u not in db["usuarios"]:
            db["usuarios"][u] = {"pass": p, "saldo": 0.0, "rango": "VIP"}
            save_db(db)
            return redirect(url_for('login'))
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px;text-align:center;"><h2>📝 REGISTRO QM</h2><form method="POST"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required><button class="btn btn-verify" style="width:100%">CREAR CUENTA</button></form></div></body></html>')

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    db = load_db()
    if u in db["usuarios"] and db["usuarios"][u]['pass'] == p:
        session['user'] = u
    return redirect(url_for('panel'))

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    db = load_db()
    u_data = db["usuarios"][session['user']]
    gen_res = ""
    
    if request.method == 'POST' and 'bin' in request.form:
        raw = request.form.get('bin', '').strip().split('|')
        bin_v = raw[0][:6]
        m_f = raw[1] if len(raw) > 1 else None
        a_f = raw[2] if len(raw) > 2 else None
        cards = [f"{bin_v}{''.join([str(random.randint(0,9)) for _ in range(16-len(bin_v))])}|{m_f if m_f else f'{random.randint(1,12):02d}'}|{a_f if a_f else str(random.randint(26,30))}|{''.join([str(random.randint(0,9)) for _ in range(3)])}" for _ in range(int(request.form.get('cant', 10)))]
        gen_res = "\n".join(cards)

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body><div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:20px;">
            <span>OWNER: <b>{session['user'].upper()}</b></span>
            <div id="display_saldo" class="badge-saldo">SALDO: ${u_data['saldo']:.2f}</div>
        </div>
        <div class="card">
            <span class="card-h">🪄 GENERADOR ELITE</span>
            <form method="POST">
                <input name="bin" placeholder="BIN o BIN|MM|YYYY" value="{request.form.get('bin', '')}">
                <input name="cant" type="number" value="10">
                <button type="submit" class="btn" style="background:#232730; color:#fff;">🪄 GENERAR</button>
                <textarea id="gen_area" rows="6" readonly style="color:var(--gold); white-space: pre;">{gen_res}</textarea>
                <button type="button" class="btn" style="background:#7a632d;color:#ffeb3b" onclick="document.getElementById('check_list').value += document.getElementById('gen_area').value + '\\n'">➕ CARGAR AL VALIDADOR</button>
            </form>
        </div>
        <div class="card">
            <span class="card-h">🛡️ GATE AMAZON</span>
            <textarea id="check_list" rows="6" placeholder="LISTA CC|MM|YY|CVV"></textarea>
            <button class="btn btn-verify" onclick="startChecking()">🚀 INICIAR VALIDACIÓN ($0.35/LIVE)</button>
            <div style="display:flex; gap:10px;">
                <button class="btn" style="background:#3d4452; color:#fff; flex:1;" onclick="location.reload()">🗑️ LIMPIAR</button>
                <button class="btn" style="background:#2ecc71; color:#000; flex:1;" onclick="downloadLives()">📥 DESCARGAR</button>
            </div>
        </div>
        <div class="card res-box" style="border-color:var(--green);"><span class="card-h" style="color:var(--green)">LIVES ✅</span><div id="lives_log"></div></div>
        <div class="card res-box" style="border-color:var(--red);"><span class="card-h" style="color:var(--red)">DEAD ❌</span><div id="dead_log"></div></div>
        { f'<a href="/admin" class="btn" style="border:1px solid var(--gold); color:var(--gold); text-decoration:none; display:block; text-align:center;">⚙️ ADMIN</a>' if u_data['rango'] == 'OWNER' else '' }
        <button class="btn" style="background:transparent; border:1px solid #ff4757; color:#ff4757; margin-top:10px;" onclick="location.href='/logout'">🚪 CERRAR SESIÓN</button>
    </div>
    <script>
    let livesArray = [];
    async function startChecking() {{
        let area = document.getElementById('check_list');
        let lines = area.value.trim().split('\\n');
        if (!lines[0]) return;
        while (lines.length > 0) {{
            let currentCC = lines.shift(); area.value = lines.join('\\n');
            let res = await fetch('/validar_card', {{ 
                method: 'POST', 
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{card: currentCC}})
            }});
            let data = await res.json();
            if (data.status === 'LIVE') {{
                document.getElementById('display_saldo').innerText = 'SALDO: $' + data.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = currentCC + ' [LIVE] <br>' + document.getElementById('lives_log').innerHTML;
                livesArray.push(currentCC);
            }} else {{
                document.getElementById('dead_log').innerHTML = currentCC + ' [DEAD] <br>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 800));
        }}
    }}
    function downloadLives() {{
        const blob = new Blob([livesArray.join('\\n')], {{ type: 'text/plain' }});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url; a.download = 'lives.txt'; a.click();
    }}
    </script></body></html>
    """)

@app.route('/validar_card', methods=['POST'])
def validar():
    user = session.get('user')
    db = load_db()
    if not user or db["usuarios"][user]['saldo'] < COSTO_LIVE:
        return jsonify({"error": "Saldo insuficiente"}), 400
    is_live = random.random() > 0.8
    if is_live:
        db["usuarios"][user]['saldo'] = round(db["usuarios"][user]['saldo'] - COSTO_LIVE, 2)
        save_db(db)
        return jsonify({"status": "LIVE", "nuevo_saldo": db["usuarios"][user]['saldo']})
    return jsonify({"status": "DEAD"})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session: return redirect(url_for('login'))
    db = load_db()
    if db["usuarios"][session['user']]['rango'] != 'OWNER': return "DENEGADO"
    if request.method == 'POST':
        target = request.form.get('u_target')
        amount = float(request.form.get('amount', 0))
        if target in db["usuarios"]:
            db["usuarios"][target]['saldo'] += amount
            save_db(db)
    return render_template_string(f'<html><head>{CSS}</head><body><div class="container" style="margin-top:50px;"><div class="card"><h2>⚙️ RECARGAR SALDO</h2><form method="POST"><select name="u_target">{" ".join([f"<option value='{u}'>{u} (${db['usuarios'][u]['saldo']})</option>" for u in db["usuarios"]])}</select><input type="number" step="0.01" name="amount" required><button class="btn btn-verify">CARGAR</button></form><br><a href="/panel" style="color:var(--gold)">Volver</a></div></div></body></html>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
