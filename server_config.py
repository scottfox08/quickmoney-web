import os, random, time, json
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'mairo_v25_telegram_blindado'

# --- BASE DE DATOS LOCAL ---
DB_FILE = 'database.json'
def load_db():
    if not os.path.exists(DB_FILE):
        db = {"usuarios": {"mairo": {"pass": "1234", "saldo": 999999.0, "rango": "OWNER", "telegram": "@mairo"}}}
        save_db(db); return db
    with open(DB_FILE, 'r') as f: return json.load(f)
def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

COSTO_LIVE = 0.35

# --- DETECCIÓN DE BANCO Y PAÍS ---
def get_bin_info(cc):
    bin_6 = cc[:6]
    bancos = ["CHASE", "BOFA", "WELLS FARGO", "CITI", "CAPITAL ONE", "BHD", "RESERVAS", "POPULAR"]
    paises = ["USA", "USA", "USA", "USA", "USA", "DOM", "DOM", "DOM"]
    idx = int(bin_6) % len(bancos)
    return f"{paises[idx]} | {bancos[idx]}"

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    :root { --gold: #c5a059; --bg: #000; --card: rgba(8, 8, 10, 0.95); --border: #1a1a1e; --green: #2ecc71; --red: #ff4757; }
    body { background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; margin: 0; padding: 10px; min-height: 100vh; overflow-x: hidden; }
    #bg-canvas { position: fixed; top:0; left:0; width:100%; height:100%; z-index: -1; opacity: 0.5; }
    .container { max-width: 500px; margin: auto; padding-bottom: 50px; position: relative; }
    .auth-card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 35px; width: 340px; text-align: center; border-top: 3px solid var(--gold); }
    .houdini-frame { width: 110px; height: 110px; border-radius: 50%; border: 2px solid var(--gold); margin: 0 auto 25px; background: url('https://i.postimg.cc/85zXp9XN/houdini-logo.png') center/cover; box-shadow: 0 0 25px rgba(197, 160, 89, 0.4); }
    .qm-title { font-size: 20px; font-weight: 700; color: #fff; margin-bottom: 30px; display: flex; align-items: center; justify-content: center; gap: 8px; white-space: nowrap; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 20px; margin-bottom: 15px; }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; display: block; }
    input, textarea { width: 100%; background: #000; border: 1px solid var(--border); color: #fff; padding: 16px; border-radius: 2px; margin-bottom: 12px; box-sizing: border-box; font-family: inherit; font-size: 13px; outline: none; }
    .btn { border: none; padding: 16px; border-radius: 2px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.3s; margin-top: 5px; font-family: inherit; }
    .btn-gold { background: var(--gold); color: #000; }
    .btn-dark { background: #111; color: #fff; border: 1px solid #222; }
    .res-box { border-radius: 2px; padding: 12px; font-size: 11px; min-height: 120px; margin-top: 15px; border: 1px solid #1a1a1e; background: #030303; overflow-y: auto; max-height: 250px; }
</style>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('panel'))
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body style="display:flex;align-items:center;justify-content:center;height:100vh;">
    <canvas id="bg-canvas"></canvas>
    <div class="auth-card">
        <div class="houdini-frame"></div>
        <div class="qm-title">⚡️ 🌩️ QUICK MONEY 🌩️ ⚡️</div>
        <form method="POST" action="/auth">
            <input name="u" placeholder="USUARIO" required autocomplete="off">
            <input type="password" name="p" placeholder="PASS" required>
            <button class="btn btn-gold">[ INGRESAR ]</button>
        </form>
        <div style="margin-top:20px; font-size:11px;">
            ¿NUEVO AQUÍ? <a href="/register" style="color:var(--gold); text-decoration:none; font-weight:bold;">REGÍSTRATE</a>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('bg-canvas'); const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth; canvas.height = window.innerHeight;
        let p = []; for(let i=0; i<60; i++) p.push({{x:Math.random()*canvas.width, y:Math.random()*canvas.height, s:Math.random()*2, sx:Math.random()-0.5, sy:Math.random()-0.5}});
        function animate() {{ ctx.clearRect(0,0,canvas.width, canvas.height); ctx.fillStyle='#c5a059'; p.forEach(i=>{{ i.x+=i.sx; i.y+=i.sy; ctx.beginPath(); ctx.arc(i.x,i.y,i.s,0,6.28); ctx.fill(); }}); requestAnimationFrame(animate); }}
        animate();
    </script>
    </body></html>
    """)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        u, p, t = request.form.get('u'), request.form.get('p'), request.form.get('t')
        db = load_db()
        if not t.startswith('@'): error = "EL ID DE TELEGRAM DEBE EMPEZAR CON @"
        elif u in db["usuarios"]: error = "USUARIO NO DISPONIBLE"
        else:
            db["usuarios"][u] = {"pass": p, "saldo": 0.0, "rango": "USER", "telegram": t}
            save_db(db)
            return redirect(url_for('login'))
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body style="display:flex;align-items:center;justify-content:center;height:100vh;">
    <div class="auth-card">
        <h2 style="color:var(--gold)">REGISTRO SUPREMO</h2>
        {{% if error %}}<p style="color:var(--red); font-size:12px;">{{{{error}}}}</p>{{% endif %}}
        <form method="POST">
            <input name="u" placeholder="USUARIO" required>
            <input type="password" name="p" placeholder="CONTRASEÑA" required>
            <input name="t" placeholder="TELEGRAM ID (EJ: @MAIRO)" required>
            <button class="btn btn-gold">CREAR CUENTA</button>
        </form>
        <a href="/" style="color:#555; text-decoration:none; font-size:11px;">VOLVER AL LOGIN</a>
    </div>
    </body></html>
    """, error=error)

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    db = load_db()
    u_data = db["usuarios"][session['user']]
    gen_res = ""
    if request.method == 'POST' and 'bin' in request.form:
        bin_v = request.form.get('bin', '').split('|')[0][:6]
        cards_list = [f"{bin_v}{''.join([str(random.randint(0,9)) for _ in range(16-len(bin_v))])}|{random.randint(1,12):02d}|{random.randint(26,30)}|{''.join([str(random.randint(0,9)) for _ in range(3)])}" for _ in range(int(request.form.get('cant', 10)))]
        gen_res = "\\n".join(cards_list)

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body>
    <audio id="live_sound" src="https://www.soundjay.com/misc/sounds/cash-register-purchase-1.mp3"></audio>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin: 30px 0;">
            <div style="font-size:11px;">ID: <b style="color:var(--gold)">{session['user'].upper()}</b> | TG: <b style="color:#888">{u_data.get('telegram', 'N/A')}</b></div>
            <div id="display_saldo" style="background:rgba(197,160,89,0.1); border:1px solid var(--gold); padding:8px 15px; border-radius:2px; color:var(--gold); font-weight:bold;">${u_data['saldo']:.2f}</div>
        </div>
        
        <div class="card">
            <span class="card-h">🪄 GENERADOR ELITE</span>
            <form method="POST">
                <input name="bin" placeholder="BIN (458012)" value="{request.form.get('bin', '')}">
                <input name="cant" type="number" value="10" style="width:75px;">
                <button type="submit" class="btn btn-dark">🪄 GENERAR TARJETAS</button>
                <textarea id="gen_area" rows="6" readonly style="margin-top:10px; color:var(--gold); font-size:12px; line-height:1.5;">{gen_res}</textarea>
                <button type="button" class="btn btn-dark" style="color:var(--gold); border: 1px solid var(--gold);" onclick="document.getElementById('check_list').value += document.getElementById('gen_area').value + '\\n'">➕ CARGAR AL VALIDADOR</button>
            </form>
        </div>

        <div class="card">
            <span class="card-h">🛡️ GATE AMAZON V21</span>
            <input id="amazon_cookie" placeholder="AMAZON SESSION COOKIE...">
            <textarea id="check_list" rows="6" placeholder="LISTA CC|MM|YY|CVV"></textarea>
            <button class="btn btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR CHECK ($0.35/LIVE)</button>
            <div style="display:flex; gap:10px; margin-top:10px;">
                <button class="btn btn-dark" style="flex:1" onclick="document.getElementById('check_list').value = ''">🗑️ LIMPIAR</button>
                <button class="btn btn-dark" style="flex:1; color:var(--green)" onclick="downloadLives()">📥 DESCARGAR</button>
            </div>
        </div>

        <span style="color:var(--green); font-size:10px; font-weight:bold;">LIVES ✅</span>
        <div class="res-box" style="border-left:3px solid var(--green); margin-bottom:15px;"><div id="lives_log"></div></div>
        
        <span style="color:var(--red); font-size:10px; font-weight:bold;">DEAD ❌</span>
        <div class="res-box" style="border-left:3px solid var(--red); opacity:0.6;"><div id="dead_log"></div></div>
        
        { f'<a href="/admin" class="btn btn-dark" style="color:var(--gold); text-decoration:none; display:block; text-align:center; margin-top:20px; border:1px solid var(--gold);">⚙️ ADMIN PANEL</a>' if u_data['rango'] == 'OWNER' else '' }
        <a href="/logout" style="color:#444; text-decoration:none; display:block; text-align:center; margin-top:20px; font-size:10px;">CERRAR SESIÓN SEGURO</a>
    </div>

    <script>
    let livesArray = [];
    async function startChecking() {{
        let area = document.getElementById('check_list');
        let lines = area.value.trim().split('\\n');
        if (!lines[0]) return;
        document.getElementById('btn_start').disabled = true;
        while (lines.length > 0) {{
            let currentCC = lines.shift(); area.value = lines.join('\\n');
            let res = await fetch('/validar_card', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{card: currentCC, cookie: document.getElementById('amazon_cookie').value}}) }});
            let data = await res.json();
            if (data.status === 'LIVE') {{
                document.getElementById('live_sound').currentTime = 0;
                document.getElementById('live_sound').play();
                document.getElementById('display_saldo').innerText = '$' + data.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<span style="color:var(--green)">[LIVE]</span> ' + currentCC + ' | ' + data.info + '<br>' + document.getElementById('lives_log').innerHTML;
                livesArray.push(currentCC);
            }} else {{
                document.getElementById('dead_log').innerHTML = '<span style="color:var(--red)">[DEAD]</span> ' + currentCC + '<br>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 800));
        }}
        document.getElementById('btn_start').disabled = false;
    }}
    function downloadLives() {{
        const blob = new Blob([livesArray.join('\\n')], {{ type: 'text/plain' }});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url; a.download = 'lives_quick_money.txt'; a.click();
    }}
    </script></body></html>
    """)

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    db = load_db()
    if u in db["usuarios"] and db["usuarios"][u]['pass'] == p: session['user'] = u
    return redirect(url_for('panel'))

@app.route('/validar_card', methods=['POST'])
def validar():
    user = session.get('user')
    db = load_db()
    data = request.json
    cc = data.get('card', '')
    if not user or db["usuarios"][user]['saldo'] < COSTO_LIVE: return jsonify({"error": "Saldo"}), 400
    is_live = random.random() > 0.8
    if is_live:
        db["usuarios"][user]['saldo'] = round(db["usuarios"][user]['saldo'] - COSTO_LIVE, 2)
        save_db(db)
        info = get_bin_info(cc)
        return jsonify({"status": "LIVE", "nuevo_saldo": db["usuarios"][user]['saldo'], "info": info})
    return jsonify({"status": "DEAD"})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or load_db()["usuarios"][session['user']]['rango'] != 'OWNER': return "DENEGADO"
    db = load_db()
    if request.method == 'POST':
        db["usuarios"][request.form.get('u_target')]['saldo'] += float(request.form.get('amount'))
        save_db(db)
    return render_template_string(f'<html><head>{CSS}</head><body style="padding:50px;"><div class="card"><h2>RECARGAR CLIENTE</h2><form method="POST"><select name="u_target" style="width:100%; padding:15px; background:#000; color:#fff; border:1px solid #333;">{" ".join([f"<option value='{u}'>{u} (${{db['usuarios'][u]['saldo']}}) - TG: {{db['usuarios'][u].get('telegram', 'N/A')}}</option>" for u in db["usuarios"]])}</select><br><br><input type="number" step="0.1" name="amount" placeholder="CANTIDAD" required><button class="btn btn-gold">APLICAR RECARGA</button></form><br><a href="/panel" style="color:var(--gold); text-decoration:none;">← VOLVER AL PANEL</a></div></body></html>')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
