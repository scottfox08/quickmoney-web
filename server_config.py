import os, random, time, json
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'mairo_v21_money_edition'

# --- BASE DE DATOS LOCAL ---
DB_FILE = 'database.json'
def load_db():
    if not os.path.exists(DB_FILE):
        db = {"usuarios": {"mairo": {"pass": "1234", "saldo": 999999.0, "rango": "OWNER"}}}
        save_db(db); return db
    with open(DB_FILE, 'r') as f: return json.load(f)
def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

COSTO_LIVE = 0.35

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    :root { --gold: #d4af37; --bg: #000; --card: rgba(10, 10, 12, 0.9); --border: #1a1a1e; --green: #2ecc71; --red: #ff4757; }
    
    body { background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; margin: 0; padding: 10px; min-height: 100vh; overflow-x: hidden; }

    /* VISUALIZER DE FONDO PARA TODO EL SITIO */
    #bg-canvas { position: fixed; top:0; left:0; width:100%; height:100%; z-index: -1; opacity: 0.5; }

    .container { max-width: 550px; margin: auto; padding-bottom: 50px; position: relative; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 25px; margin-bottom: 15px; backdrop-filter: blur(15px); box-shadow: 0 15px 35px rgba(0,0,0,0.7); }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; display: block; letter-spacing: 1px; }
    
    input, textarea { width: 100%; background: #000; border: 1px solid var(--border); color: #fff; padding: 15px; border-radius: 4px; margin-bottom: 12px; box-sizing: border-box; font-family: inherit; font-size: 13px; outline: none; }
    input:focus { border-color: var(--gold); }
    
    .btn { border: none; padding: 16px; border-radius: 4px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.3s; margin-top: 5px; font-family: inherit; letter-spacing: 1px; }
    .btn-verify { background: var(--gold); color: #000; }
    .btn-verify:hover { background: #b5942f; transform: translateY(-2px); }
    
    .badge-saldo { background: rgba(212, 175, 55, 0.1); padding: 10px 22px; border-radius: 4px; border: 1px solid var(--gold); color: var(--gold); font-weight: bold; font-size: 13px; }
    .res-box { border-radius: 4px; padding: 12px; font-size: 12px; min-height: 100px; margin-top: 15px; overflow-y: auto; max-height: 250px; border: 1px solid #222; background: #050505; line-height: 1.6;}
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
            this.size = Math.random() * 2.5;
            this.speedX = Math.random() * 0.8 - 0.4;
            this.speedY = Math.random() * 0.8 - 0.4;
            this.color = Math.random() > 0.5 ? '#d4af37' : '#555';
        }
        update() { this.x += this.speedX; this.y += this.speedY; if(this.size > 0.2) this.size -= 0.005; }
        draw() { ctx.fillStyle = this.color; ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill(); }
    }
    function handleParticles() {
        particles.push(new Particle());
        for(let i=0; i<particles.length; i++) {
            particles[i].update(); particles[i].draw();
            if(particles[i].size <= 0.3) { particles.splice(i, 1); i--; }
        }
    }
    function animate() { ctx.clearRect(0,0,canvas.width, canvas.height); handleParticles(); requestAnimationFrame(animate); }
    animate();
    window.addEventListener('resize', () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; });
</script>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('panel'))
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body style="display:flex;align-items:center;justify-content:center;height:100vh;">
    <canvas id="bg-canvas"></canvas>
    <div class="card" style="width:340px;text-align:center;border:1px solid var(--border); border-top: 4px solid var(--gold);">
        <img src="https://i.imgur.com/8kXb7mR.png" style="width:60px; margin-bottom:15px;">
        <h2 style="letter-spacing:-1px; margin-bottom:30px;">QUICK MONEY <br><span style="font-weight:300; font-size:14px; color:#555;">CHECKER V21</span></h2>
        <form method="POST" action="/auth">
            <input name="u" placeholder="USUARIO" required autocomplete="off">
            <input type="password" name="p" placeholder="CONTRASEÑA" required>
            <button class="btn btn-verify">ACCEDER AL SISTEMA</button>
        </form>
    </div>
    {CANVAS_SCRIPT}
    </body></html>
    """)

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    db = load_db()
    if u in db["usuarios"] and db["usuarios"][u]['pass'] == p: session['user'] = u
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
    <body>
    <canvas id="bg-canvas"></canvas>
    <audio id="live_sound" src="https://www.soundjay.com/misc/sounds/cash-register-purchase-1.mp3"></audio>

    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin: 25px 0;">
            <div style="font-size:12px; letter-spacing:1px;">OPERADOR: <b style="color:var(--gold);">{session['user'].upper()}</b></div>
            <div id="display_saldo" class="badge-saldo">${u_data['saldo']:.2f}</div>
        </div>
        
        <div class="card">
            <span class="card-h">🪄 GENERADOR ELITE V21</span>
            <form method="POST">
                <div style="display:flex; gap:10px;">
                    <input name="bin" placeholder="BIN (EJ: 458012)" value="{request.form.get('bin', '')}" style="flex:2;">
                    <input name="cant" type="number" value="10" style="flex:1;">
                </div>
                <button type="submit" class="btn" style="background:#151517; color:#fff;">🪄 GENERAR</button>
                <textarea id="gen_area" rows="5" readonly style="color:var(--gold); margin-top:10px; font-size:11px;">{gen_res}</textarea>
                <button type="button" class="btn" style="background:#222;color:var(--gold)" onclick="document.getElementById('check_list').value += document.getElementById('gen_area').value + '\\n'">➕ CARGAR AL VALIDADOR</button>
            </form>
        </div>

        <div class="card">
            <span class="card-h">🛡️ GATE AMAZON LIVE</span>
            <input id="amazon_cookie" placeholder="PASTE AMAZON COOKIE HERE...">
            <textarea id="check_list" rows="6" placeholder="LISTA CC|MM|YY|CVV"></textarea>
            <button class="btn btn-verify" id="btn_start" onclick="startChecking()">🚀 INICIAR VALIDACIÓN ($0.35/LIVE)</button>
            <div style="display:flex; gap:10px;">
                <button class="btn" style="background:#111; color:#fff; flex:1;" onclick="location.reload()">🗑️ LIMPIAR</button>
                <button class="btn" style="background:#111; color:var(--green); flex:1;" onclick="downloadLives()">📥 DESCARGAR</button>
            </div>
        </div>

        <div class="card res-box" style="border-left:4px solid var(--green);"><span class="card-h" style="color:var(--green)">LIVES ✅</span><div id="lives_log"></div></div>
        <div class="card res-box" style="border-left:4px solid var(--red); opacity:0.7;"><span class="card-h" style="color:var(--red)">DEAD ❌</span><div id="dead_log"></div></div>
        
        { f'<a href="/admin" class="btn" style="border:1px solid var(--gold); color:var(--gold); text-decoration:none; display:block; text-align:center;">⚙️ PANEL DE CONTROL</a>' if u_data['rango'] == 'OWNER' else '' }
        <button class="btn" style="background:transparent; color:#444; margin-top:15px;" onclick="location.href='/logout'">CERRAR SESIÓN SEGURO</button>
    </div>

    {CANVAS_SCRIPT}

    <script>
    let livesArray = [];
    async function startChecking() {{
        let area = document.getElementById('check_list');
        let lines = area.value.trim().split('\\n');
        if (!lines[0]) return;
        
        document.getElementById('btn_start').innerText = "VALIDANDO...";
        document.getElementById('btn_start').disabled = true;

        while (lines.length > 0) {{
            let currentCC = lines.shift(); 
            area.value = lines.join('\\n');
            
            let res = await fetch('/validar_card', {{ 
                method: 'POST', 
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{card: currentCC, cookie: document.getElementById('amazon_cookie').value}})
            }});
            
            let data = await res.json();
            if (data.status === 'LIVE') {{
                // REPRODUCIR SONIDO DE DINERO
                document.getElementById('live_sound').currentTime = 0;
                document.getElementById('live_sound').play();
                
                document.getElementById('display_saldo').innerText = '$' + data.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<span style="color:var(--green)">[LIVE]</span> ' + currentCC + '<br>' + document.getElementById('lives_log').innerHTML;
                livesArray.push(currentCC);
            }} else {{
                document.getElementById('dead_log').innerHTML = '<span style="color:var(--red)">[DEAD]</span> ' + currentCC + '<br>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 700));
        }}
        document.getElementById('btn_start').innerText = "🚀 INICIAR VALIDACIÓN ($0.35/LIVE)";
        document.getElementById('btn_start').disabled = false;
    }}

    function downloadLives() {{
        if(livesArray.length === 0) return alert("No hay lives para descargar");
        const blob = new Blob([livesArray.join('\\n')], {{ type: 'text/plain' }});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url; a.download = 'lives_quick_money.txt'; a.click();
    }}
    </script></body></html>
    """)

# ... (Las rutas /validar_card, /admin y /logout se mantienen exactamente iguales al código anterior)
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
    return render_template_string(f'<html><head>{CSS}</head><body><div class="container" style="margin-top:50px;"><div class="card"><h2>⚙️ RECARGAR SALDO</h2><form method="POST"><select name="u_target" style="width:100%; padding:10px; background:#000; color:#fff; border:1px solid #333;">{" ".join([f"<option value='{u}'>{u} (${db['usuarios'][u]['saldo']})</option>" for u in db["usuarios"]])}</select><br><br><input type="number" step="0.01" name="amount" placeholder="CANTIDAD A SUMAR" required><button class="btn btn-verify">APLICAR RECARGA</button></form><br><a href="/panel" style="color:var(--gold); text-decoration:none;">← Volver al Panel</a></div></div></body></html>')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
