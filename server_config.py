import os, random, time, json
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'quick_money_v31_final_cloud'

# --- TU CONEXIÓN A MONGODB ATLAS ---
# Pon tu contraseña real aquí:
MONGO_URI = "mongodb+srv://mairo:mairo1212@cluster0.inuth4k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db_mongo = client['quickmoney_db']
    usuarios_col = db_mongo['usuarios']
    # Verificar conexión
    client.admin.command('ping')
    print("Conexión Exitosa a MongoDB")
except Exception as e:
    print(f"Error de conexión: {e}")

# Crear admin por defecto en la nube
if not usuarios_col.find_one({"u": "mairo"}):
    usuarios_col.insert_one({"u": "mairo", "p": "1234", "saldo": 999999.0, "rango": "OWNER", "telegram": "@mairo"})

COSTO_LIVE = 0.15

def get_full_bin_info(cc):
    b = cc[:6]
    if b.startswith(('414740', '4737', '4013', '4226', '4365', '4852', '4120')): return "JPMORGAN CHASE BANK N.A. | UNITED STATES 🇺🇸"
    elif b.startswith(('4802', '4400', '4444', '4000', '4026', '4147', '4266')): return "BANK OF AMERICA N.A. | UNITED STATES 🇺🇸"
    elif b.startswith(('5312', '5434', '4343', '4615', '5166', '4736')): return "WELLS FARGO BANK N.A. | UNITED STATES 🇺🇸"
    elif b.startswith(('4539', '4342', '4031', '4052')): return "BANRESERVAS | DOMINICAN REPUBLIC 🇩🇴"
    elif b.startswith(('4152', '4015', '4214', '5498')): return "BANCO POPULAR | DOMINICAN REPUBLIC 🇩🇴"
    elif b.startswith(('4913', '4213', '5230', '5160')): return "BANCO BHD | DOMINICAN REPUBLIC 🇩🇴"
    else: return "VISA/MC INTERNATIONAL | UNITED STATES 🇺🇸"

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    :root { --gold: #c5a059; --bg: #000; --card: rgba(8, 8, 10, 0.95); --border: #1a1a1e; --green: #2ecc71; --red: #ff4757; }
    body { background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; margin: 0; padding: 10px; min-height: 100vh; overflow-x: hidden; }
    #bg-canvas { position: fixed; top:0; left:0; width:100%; height:100%; z-index: -1; opacity: 0.6; }
    .container { max-width: 500px; margin: auto; padding-bottom: 50px; position: relative; z-index: 10; }
    .auth-card { background: var(--card); border: 1px solid var(--border); padding: 50px 35px; width: 340px; text-align: center; border-top: 3px solid var(--gold); border-radius: 4px; }
    .chk-tag { font-size: 11px; color: var(--gold); letter-spacing: 4px; font-weight: 300; margin-top: -15px; margin-bottom: 40px; display: block; opacity: 0.8; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 20px; margin-bottom: 15px; backdrop-filter: blur(5px); }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; display: block; letter-spacing: 1.5px; }
    .live-item { border-bottom: 1px solid #111; padding: 10px 0; margin-bottom: 5px; }
    .live-cc { font-size: 14px; font-weight: 700; color: #fff; display: block; }
    .live-info { font-size: 10px; color: var(--gold); text-transform: uppercase; margin-top: 3px; display: block; }
    input, textarea { width: 100%; background: #000; border: 1px solid var(--border); color: #fff; padding: 16px; border-radius: 2px; margin-bottom: 12px; box-sizing: border-box; font-family: inherit; font-size: 13px; outline: none; }
    .btn { border: none; padding: 18px; border-radius: 2px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.3s; margin-top: 5px; font-family: inherit; }
    .btn-gold { background: var(--gold); color: #000; }
    .btn-dark { background: #111; color: #fff; border: 1px solid #222; }
    .res-box { border-radius: 2px; padding: 12px; font-size: 11px; min-height: 120px; border: 1px solid #1a1a1e; background: #030303; overflow-y: auto; max-height: 280px; }
</style>
"""

CANVAS_SCRIPT = """
<script>
    const canvas = document.getElementById('bg-canvas'); const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    let p = [];
    class Particle {
        constructor() { this.x = Math.random()*canvas.width; this.y = Math.random()*canvas.height; this.s = Math.random()*2.5; this.sx = Math.random()*0.6-0.3; this.sy = Math.random()*0.6-0.3; this.c = Math.random()>0.4?'#c5a059':'#333'; }
        u() { this.x += this.sx; this.y += this.sy; if(this.s>0.2) this.s-=0.005; }
        d() { ctx.fillStyle = this.c; ctx.beginPath(); ctx.arc(this.x,this.y,this.s,0,6.28); ctx.fill(); }
    }
    function a() { ctx.clearRect(0,0,canvas.width,canvas.height); p.push(new Particle()); for(let i=0;i<p.length;i++){ p[i].u(); p[i].d(); if(p[i].s<=0.3){p.splice(i,1); i--;} } requestAnimationFrame(a); } a();
</script>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('panel'))
    return render_template_string(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><canvas id="bg-canvas"></canvas><div class="auth-card"><div style="font-size:22px; font-weight:700; color:#fff; margin-bottom:25px;">⚡️ 🌩️ QUICK MONEY 🌩️ ⚡️</div><span class="chk-tag">{{{{CHK}}}}</span><form method="POST" action="/auth"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required><button class="btn btn-gold">[ INGRESAR ]</button></form><div style="margin-top:25px; font-size:11px;">¿NUEVO AQUÍ? <a href="/register" style="color:var(--gold); font-weight:bold; text-decoration:none;">REGÍSTRATE</a></div></div>{CANVAS_SCRIPT}</body></html>')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        u, p, t = request.form.get('u'), request.form.get('p'), request.form.get('t')
        if not t.startswith('@'): error = "ID DE TELEGRAM CON @"
        elif usuarios_col.find_one({"u": u}): error = "USUARIO OCUPADO"
        else:
            usuarios_col.insert_one({"u": u, "p": p, "saldo": 0.0, "rango": "USER", "telegram": t})
            return redirect(url_for('login'))
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><canvas id="bg-canvas"></canvas><div class="auth-card"><h2>REGISTRO</h2>{{% if error %}}<p style="color:var(--red)">{{{{error}}}}</p>{{% endif %}}<form method="POST"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required><input name="t" placeholder="TELEGRAM @ID" required><button class="btn btn-gold">CREAR CUENTA</button></form></div>{CANVAS_SCRIPT}</body></html>', error=error)

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = usuarios_col.find_one({"u": session['user']})
    gen_res = ""
    if request.method == 'POST' and 'bin' in request.form:
        raw_bin = request.form.get('bin', '').replace(' ', '')
        parts = raw_bin.split('|')
        cards = []
        for _ in range(int(request.form.get('cant', 10))):
            cc = parts[0]
            while len(cc) < 16: cc += str(random.randint(0, 9))
            cards.append(f"{cc}|{parts[1] if len(parts)>1 else '12'}|{parts[2] if len(parts)>2 else '2028'}|{random.randint(100,999)}")
        gen_res = "\\n".join(cards)
    
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body><canvas id="bg-canvas"></canvas>
    <audio id="live_sound" src="https://www.soundjay.com/misc/sounds/cash-register-purchase-1.mp3"></audio>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin: 30px 0;">
            <div style="font-size:11px;">ID: <b style="color:var(--gold)">ADMIN</b></div>
            <div id="display_saldo" style="background:rgba(197,160,89,0.1); border:1px solid var(--gold); padding:8px 15px; border-radius:2px; color:var(--gold); font-weight:bold;">${u_data['saldo']:.2f}</div>
        </div>
        <div class="card"><span class="card-h">🪄 GENERADOR ELITE</span>
            <form method="POST">
                <input name="bin" placeholder="BIN|MM|YYYY" value="{request.form.get('bin', '')}">
                <input name="cant" type="number" value="10" style="width:70px;">
                <button type="submit" class="btn btn-dark">🪄 GENERAR</button>
                <textarea id="gen_area" rows="6" readonly style="margin-top:10px; color:var(--gold);">{gen_res}</textarea>
                <button type="button" class="btn btn-dark" style="color:var(--gold)" onclick="cargarAlValidator()">➕ CARGAR AL VALIDADOR</button>
            </form>
        </div>
        <div class="card"><span class="card-h">🛡️ VALIDADOR SUPREMO</span>
            <input id="amazon_cookie" placeholder="PASTE AMAZON SESSION COOKIE..." required>
            <textarea id="check_list" rows="6" placeholder="LISTA CC|MM|YY|CVV"></textarea>
            <button class="btn btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR CHECK ($0.15/LIVE)</button>
        </div>
        <span style="color:var(--green); font-size:10px; font-weight:bold;">APROBADAS ✅</span><div class="res-box" id="lives_log"></div>
        <span style="color:var(--red); font-size:10px; font-weight:bold; margin-top:15px; display:block;">RECHAZADAS ❌</span><div class="res-box" id="dead_log" style="opacity:0.5; min-height:80px;"></div>
        { f'<a href="/admin" class="btn btn-dark" style="color:var(--gold); text-decoration:none; display:block; text-align:center; margin-top:20px; border:1px solid var(--gold);">⚙️ ADMIN PANEL</a>' if u_data['rango'] == 'OWNER' else '' }
        <a href="/logout" style="color:#444; text-decoration:none; display:block; text-align:center; margin-top:30px; font-size:10px;">[ CERRAR SESIÓN ]</a>
    </div>{CANVAS_SCRIPT}
    <script>
    window.onload = function() {{ let area = document.getElementById('gen_area'); if(area.value) area.value = area.value.replace(/\\\\n/g, '\\n'); }};
    function cargarAlValidator() {{ let gen = document.getElementById('gen_area').value.replace(/\\\\n/g, '\\n'); document.getElementById('check_list').value += gen + '\\n'; }}
    async function startChecking() {{
        let area = document.getElementById('check_list'); let lines = area.value.trim().split('\\n');
        let saldoActual = parseFloat(document.getElementById('display_saldo').innerText.replace('$', ''));
        if (!lines[0]) return;
        if (!document.getElementById('amazon_cookie').value) return alert("Amazon Cookie Required!");
        if (saldoActual < 0.15) return alert("FOUND INSUFFICIENT - Solo puedes validar si tiene saldo.");
        
        document.getElementById('btn_start').disabled = true;
        while (lines.length > 0) {{
            let cc = lines.shift(); area.value = lines.join('\\n');
            let res = await fetch('/validar_card', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{card: cc}}) }});
            let data = await res.json();
            if (data.status === 'insufficient') {{ alert("FOUND INSUFFICIENT"); break; }}
            if (data.status === 'LIVE') {{
                document.getElementById('live_sound').currentTime = 0; document.getElementById('live_sound').play();
                document.getElementById('display_saldo').innerText = '$' + data.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<div class="live-item"><span class="live-cc">'+cc+'</span><span class="live-info">'+data.info+'</span></div>' + document.getElementById('lives_log').innerHTML;
            }} else {{ document.getElementById('dead_log').innerHTML = cc + '<br>' + document.getElementById('dead_log').innerHTML; }}
            await new Promise(r => setTimeout(r, 800));
        }}
        document.getElementById('btn_start').disabled = false;
    }}
    </script></body></html>
    """)

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    user = usuarios_col.find_one({"u": u, "p": p})
    if user: session['user'] = u
    return redirect(url_for('panel'))

@app.route('/validar_card', methods=['POST'])
def validar():
    user = session.get('user')
    if not user: return jsonify({"status": "error"})
    u_data = usuarios_col.find_one({"u": user})
    if u_data['saldo'] < COSTO_LIVE: return jsonify({"status": "insufficient"})
    cc = request.json.get('card', '')
    if random.random() > 0.8:
        nuevo_saldo = round(u_data['saldo'] - COSTO_LIVE, 2)
        usuarios_col.update_one({"u": user}, {"$set": {"saldo": nuevo_saldo}})
        return jsonify({"status": "LIVE", "nuevo_saldo": nuevo_saldo, "info": get_full_bin_info(cc)})
    return jsonify({"status": "DEAD"})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    u_admin = usuarios_col.find_one({"u": session.get('user')})
    if not u_admin or u_admin['rango'] != 'OWNER': return "DENEGADO"
    if request.method == 'POST':
        usuarios_col.update_one({"u": request.form.get('u_target')}, {"$inc": {"saldo": float(request.form.get('amount'))}})
    todos = usuarios_col.find()
    return render_template_string(f'<html><head>{CSS}</head><body style="padding:50px;"><div class="card"><h2>ADMIN</h2><form method="POST"><select name="u_target" style="width:100%; padding:15px; background:#000; color:#fff; border:1px solid #333;">' + "".join([f"<option value='{u['u']}'>{u['u']} (${u['saldo']:.2f}) - TG: {u.get('telegram', 'N/A')}</option>" for u in todos]) + '</select><br><br><input type="number" step="0.1" name="amount" required><button class="btn btn-gold">CARGAR</button></form><br><a href="/panel" style="color:var(--gold)">← VOLVER</a></div></body></html>')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
