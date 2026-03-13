import os, random, time, json
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'mairo_v22_1_houdini_storm_boss'

# --- BASE DE DATOS LOCAL (Volátil, pero funcional para diseño) ---
DB_FILE = 'database.json'
def load_db():
    if not os.path.exists(DB_FILE):
        db = {"usuarios": {"mairo": {"pass": "1234", "saldo": 999999.0, "rango": "OWNER", "telegram": "@mairo"}}}
        save_db(db); return db
    with open(DB_FILE, 'r') as f: return json.load(f)
def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

COSTO_LIVE = 0.35

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&display=swap'); /* Para el logo 3D */

    :root { --gold: #c5a059; --bg: #000; --card: rgba(8, 8, 10, 0.95); --border: #1a1a1e; --green: #2ecc71; --red: #ff4757; }
    
    body { background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; margin: 0; padding: 10px; min-height: 100vh; overflow-x: hidden; }

    /* VISUALIZER DE FONDO ANIMADO */
    #bg-canvas { position: fixed; top:0; left:0; width:100%; height:100%; z-index: -1; opacity: 0.6; }

    .container { max-width: 500px; margin: auto; padding-bottom: 50px; position: relative; }
    
    /* LOGIN & REGISTER CARDS */
    .auth-card { background: var(--card); border: 1px solid var(--border); border-radius: 2px; padding: 35px; width: 360px; text-align: center; backdrop-filter: blur(20px); box-shadow: 0 20px 50px rgba(0,0,0,0.8); border-top: 3px solid var(--gold); }
    
    /* LOGO HOUDINI REPARADO */
    .houdini-logo { width: 90px; height: 90px; border-radius: 50%; border: 2px solid var(--gold); padding: 5px; background: #000; margin-bottom: 25px; box-shadow: 0 0 20px rgba(197, 160, 89, 0.3); }
    
    /* LOGO "QUICK MONEY" TORMENTA EDICIÓN */
    .qm-brand-3d { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 28px; /* Un poco menos grande para que quepan los emojis */
        font-weight: 800; 
        color: #fff; 
        letter-spacing: -1.5px; 
        margin-bottom: 30px; 
        display: block; 
        text-shadow: 1px 1px 0px var(--gold), 2px 2px 0px #888, 3px 3px 0px #333; /* Efecto 3D menos intenso */
    }

    /* DASHBOARD ELEMENTS */
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 20px; margin-bottom: 15px; }
    .card-h { font-size: 10px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; display: block; letter-spacing: 1px; }
    
    input, textarea, select { width: 100%; background: #000; border: 1px solid var(--border); color: var(--gold); padding: 16px; border-radius: 2px; margin-bottom: 12px; box-sizing: border-box; font-family: inherit; font-size: 13px; outline: none; }
    input:focus, select:focus { border-color: var(--gold); }
    
    .btn { border: none; padding: 18px; border-radius: 2px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.3s; margin-top: 5px; font-family: inherit; letter-spacing: 1px; }
    .btn-gold { background: var(--gold); color: #000; }
    .btn-gold:hover { background: #b5942f; filter: brightness(1.2); }
    
    .badge-saldo { background: rgba(197, 160, 89, 0.1); padding: 10px 20px; border-radius: 2px; border: 1px solid var(--gold); color: var(--gold); font-weight: bold; font-size: 13px; }
    .res-box { border-radius: 2px; padding: 12px; font-size: 11px; min-height: 100px; margin-top: 15px; border: 1px solid #1a1a1e; background: #030303; }
</style>
"""

CANVAS_SCRIPT = """
<script>
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    let particles = [];
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2;
            this.speedX = Math.random() * 0.6 - 0.3;
            this.speedY = Math.random() * 0.6 - 0.3;
        }
        update() { this.x += this.speedX; this.y += this.speedY; }
        draw() { ctx.fillStyle = '#c5a059'; ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill(); }
    }
    for(let i=0; i<60; i++) particles.push(new Particle());
    function animate() { ctx.clearRect(0,0,canvas.width, canvas.height); particles.forEach(p => { p.update(); p.draw(); }); requestAnimationFrame(animate); }
    animate();
    window.addEventListener('resize', () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; });
</script>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body style="display:flex;align-items:center;justify-content:center;height:100vh;">
    <canvas id="bg-canvas"></canvas>
    <div class="auth-card">
        <img src="https://raw.githubusercontent.com/C4H-Houdini/houdini-checker/master/houdini-logo.png" class="houdini-logo">
        
        <div class="qm-brand-3d">⚡️🌩️ QUICK MONEY 🌩️⚡️</div>
        
        <form method="POST" action="/auth">
            <input name="u" placeholder="USUARIO" required autocomplete="off">
            <input type="password" name="p" placeholder="CONTRASEÑA" required>
            <button class="btn btn-gold">[ INGRESAR AL SISTEMA ]</button>
        </form>
        <div style="margin-top:25px; font-size:11px; color:#555; border-top: 1px solid #111; padding-top:15px;">
            ¿No tienes cuenta? <a href="/register" style="color:var(--gold); text-decoration:none; font-weight:bold;">REGÍSTRATE AQUÍ</a>
        </div>
    </div>
    {CANVAS_SCRIPT}
    </body></html>
    """)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        u, p, t = request.form.get('u'), request.form.get('p'), request.form.get('t')
        db = load_db()
        if u in db["usuarios"]: error = "EL USUARIO YA EXISTE"
        elif not t: error = "TELEGRAM ID ES OBLIGATORIO"
        else:
            db["usuarios"][u] = {"pass": p, "saldo": 0.0, "rango": "USER", "telegram": t}
            save_db(db)
            return redirect(url_for('login'))
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body style="display:flex;align-items:center;justify-content:center;height:100vh;">
    <canvas id="bg-canvas"></canvas>
    <div class="auth-card">
        <h2 style="color:var(--gold); letter-spacing:2px; margin-bottom:30px;">REGISTRO</h2>
        {{% if error %}}<p style="color:var(--red); font-size:11px; border:1px solid #ff4757; padding:5px; background:rgba(255,71,87,0.1);">{{{{ error }}}}</p>{{% endif %}}
        <form method="POST">
            <input name="u" placeholder="NUEVO USUARIO" required>
            <input type="password" name="p" placeholder="NUEVA CONTRASEÑA" required>
            
            <input name="t" placeholder="TELEGRAM ID (@usuario)" required>
            
            <button class="btn btn-gold">CREAR CUENTA SUPREMA</button>
        </form>
        <a href="/" style="color:#555; text-decoration:none; font-size:11px;">VOLVER AL LOGIN</a>
    </div>
    {CANVAS_SCRIPT}
    </body></html>
    """, error=error)

@app.route('/dashboard')
def dashboard():
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
    <body>
    <canvas id="bg-canvas"></canvas>
    <audio id="live_sound" src="https://www.soundjay.com/misc/sounds/cash-register-purchase-1.mp3"></audio>

    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin: 30px 0;">
            <div style="font-size:11px; letter-spacing:1px; color:#888;">ID: <b style="color:#fff;">{session['user'].upper()}</b> | TG: <b style="color:var(--gold)">{u_data.get('telegram', 'N/A')}</b></div>
            <div id="display_saldo" class="badge-saldo">${u_data['saldo']:.2f}</div>
        </div>
        
        <div class="card">
            <span class="card-h">🪄 GENERADOR ELITE</span>
            <form method="POST">
                <input name="bin" placeholder="BIN (458012)" value="{request.form.get('bin', '')}">
                <button type="submit" class="btn" style="background:#111; color:#fff; border:1px solid #222;">🪄 GENERAR</button>
                <textarea id="gen_area" rows="4" readonly style="margin-top:10px; font-size:11px;">{gen_res}</textarea>
                <button type="button" class="btn" style="background:#111;color:var(--gold); border:1px solid var(--gold);" onclick="document.getElementById('check_list').value += document.getElementById('gen_area').value + '\\n'">➕ CARGAR</button>
            </form>
        </div>

        <div class="card">
            <span class="card-h">🛡️ GATE AMAZON LIVE</span>
            <input id="amazon_cookie" placeholder="AMAZON SESSION COOKIE...">
            <textarea id="check_list" rows="6" placeholder="LISTA CC|MM|YY|CVV"></textarea>
            <button class="btn btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR CHECK ($0.35/LIVE)</button>
        </div>

        <div class="card res-box" style="border-left:3px solid var(--green);"><div id="lives_log"></div></div>
        <div class="card res-box" style="border-left:3px solid var(--red); opacity:0.6;"><div id="dead_log"></div></div>
        
        { f'<a href="/admin" class="btn" style="background:transparent; border:1px solid var(--gold); color:var(--gold); text-decoration:none; display:block; text-align:center;">⚙️ ADMIN PANEL</a>' if u_data['rango'] == 'OWNER' else '' }
        <button class="btn" style="background:transparent; color:#333; margin-top:20px;" onclick="location.href='/logout'">LOGOUT</button>
    </div>

    {CANVAS_SCRIPT}

    <script>
    let livesArray = [];
    async function startChecking() {{
        let area = document.getElementById('check_list');
        let lines = area.value.trim().split('\\n');
        if (!lines[0]) return;
        
        document.getElementById('btn_start').disabled = true;

        while (lines.length > 0) {{
            let currentCC = lines.shift(); area.value = lines.join('\\n');
            let res = await fetch('/validar_card', {{ 
                method: 'POST', 
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{card: currentCC, cookie: document.getElementById('amazon_cookie').value}})
            }});
            let data = await res.json();
            if (data.status === 'LIVE') {{
                document.getElementById('live_sound').currentTime = 0;
                document.getElementById('live_sound').play();
                document.getElementById('display_saldo').innerText = '$' + data.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<b style="color:var(--green)">[LIVE]</b> ' + currentCC + '<br>' + document.getElementById('lives_log').innerHTML;
                livesArray.push(currentCC);
            }} else {{
                document.getElementById('dead_log').innerHTML = '<b style="color:var(--red)">[DEAD]</b> ' + currentCC + '<br>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 800));
        }}
        document.getElementById('btn_start').disabled = false;
    }}
    </script></body></html>
    """)

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    db = load_db()
    if u in db["usuarios"] and db["usuarios"][u]['pass'] == p: session['user'] = u
    return redirect(url_for('dashboard'))

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
    if 'user' not in session or load_db()["usuarios"][session['user']]['rango'] != 'OWNER': return "DENEGADO"
    db = load_db()
    if request.method == 'POST':
        target = request.form.get('u_target')
        amount = float(request.form.get('amount', 0))
        if target in db["usuarios"]:
            db["usuarios"][target]['saldo'] += amount
            save_db(db)
    return render_template_string(f'<html><head>{CSS}</head><body style="padding:50px;"><div class="container card"><h2>⚙️ RECARGAR SALDO</h2><form method="POST"><select name="u_target">{" ".join([f"<option value='{u}'>{u} (${{db['usuarios'][u]['saldo']}}) - TG: {{db['usuarios'][u].get('telegram', 'N/A')}}</option>" for u in db["usuarios"]])}</select><br><br><input type="number" step="0.1" name="amount" placeholder="CANTIDAD A SUMAR" required><button class="btn btn-gold">APLICAR CARGA</button></form><br><a href="/dashboard" style="color:var(--gold); text-decoration:none;">← Volver</a></div></div></body></html>')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
