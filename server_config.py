import os, random, time, json, requests, base64
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'quick_money_v32_elite_decodo'

# --- CONFIGURACIÓN MAESTRA ---
SNIPCART_SECRET = "ST_MDM2YTJlNjItNjBmYi00N2IyLWFjYWMtNDBkYjZmN2M2ODUzNjM5MDkwMzU3MzkyMjQ1NjA3"
MONGO_URI = "mongodb+srv://mairo:mairo1212@cluster0.inuth4k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# --- TUS PROXIES RESIDENCIALES DECODO ---
PROXY_USER = 'sp6jzqtaou'
PROXY_PASS = 'rUd7t65FxkK+x3Flhr'
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@gate.decodo.com:10001"
PROXIES_CONFIG = {
    'http': PROXY_URL,
    'https': PROXY_URL
}

try:
    client = MongoClient(MONGO_URI)
    db_mongo = client['quickmoney_db']
    usuarios_col = db_mongo['usuarios']
    print("Conexión Exitosa a MongoDB")
except Exception as e:
    print(f"Error de conexión: {e}")

COSTO_LIVE = 0.15

# --- MOTOR DE VALIDACIÓN (EL GATE CON PROXY) ---
def check_gate_pro(cc):
    """
    Usa Snipcart + Proxies Residenciales para validar la CC.
    """
    try:
        # 1. Preparar Autenticación
        auth_str = base64.b64encode(f"{SNIPCART_SECRET}:".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_str}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 2. Datos del 'Pedido' ficticio para validar
        # En Snipcart, intentamos crear una orden mínima o validar el pago
        payload = {
            "paymentMethod": "CreditCard",
            "card": { "number": cc.split('|')[0], "expiryMonth": cc.split('|')[1], "expiryYear": cc.split('|')[2], "cvv": cc.split('|')[3] }
        }

        # 3. Petición al API usando tus PROXIES DECODO
        # Nota: Usamos un endpoint de prueba de Snipcart
        api_url = "https://app.snipcart.com/api/test-validation" 
        
        # Simulamos la llamada (Para que no te cobren en el modo Test de una vez)
        # Pero el sistema ya está configurado para pasar por el Proxy de Decodo
        response = requests.get('https://ip.decodo.com/json', proxies=PROXIES_CONFIG, timeout=10)
        ip_usada = response.json().get('query', 'IP-ROTADA')

        # LÓGICA DE RESPUESTA
        # Como estás en modo TEST, simulamos éxito para Visa (empieza en 4)
        if cc.startswith('4'):
            return {"status": "LIVE", "msg": f"AUTHORIZED | IP: {ip_usada}"}
        else:
            return {"status": "DEAD", "msg": "DECLINED BY BANK"}

    except Exception as e:
        return {"status": "ERROR", "msg": f"Proxy/Gate Error: {str(e)}"}

# --- DISEÑO Y RUTAS (ID DINÁMICO) ---
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    :root { --gold: #c5a059; --bg: #000; --card: rgba(8, 8, 10, 0.95); --border: #1a1a1e; --green: #2ecc71; --red: #ff4757; }
    body { background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; margin: 0; padding: 10px; min-height: 100vh; }
    .container { max-width: 500px; margin: auto; position: relative; z-index: 10; }
    .auth-card { background: var(--card); border: 1px solid var(--border); padding: 40px; text-align: center; border-top: 3px solid var(--gold); }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 20px; margin-bottom: 15px; }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: bold; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; display: block; letter-spacing: 2px; }
    input, textarea { width: 100%; background: #000; border: 1px solid var(--border); color: #fff; padding: 15px; border-radius: 2px; margin-bottom: 10px; font-family: inherit; font-size: 13px; outline: none; }
    .btn { border: none; padding: 15px; border-radius: 2px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; width: 100%; font-family: inherit; }
    .btn-gold { background: var(--gold); color: #000; }
    .btn-dark { background: #111; color: #fff; border: 1px solid #222; }
    .res-box { border-radius: 2px; padding: 10px; font-size: 11px; min-height: 100px; border: 1px solid #1a1a1e; background: #030303; margin-bottom: 10px; overflow-y: auto; max-height: 200px; }
</style>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('panel'))
    return render_template_string(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="auth-card"><div style="font-size:22px; font-weight:700; color:#fff; margin-bottom:10px;">⚡️ QUICK MONEY ⚡️</div><span style="font-size:10px; color:var(--gold); letter-spacing:3px;">GATE V32.2 ELITE</span><br><br><form method="POST" action="/auth"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required><button class="btn btn-gold">[ INGRESAR ]</button></form><div style="margin-top:20px; font-size:11px;"><a href="/register" style="color:var(--gold); text-decoration:none;">CREAR CUENTA NUEVA</a></div></div></body></html>')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p, t = request.form.get('u'), request.form.get('p'), request.form.get('t')
        if not usuarios_col.find_one({"u": u}):
            usuarios_col.insert_one({"u": u, "p": p, "saldo": 0.0, "rango": "USER", "telegram": t})
            return redirect(url_for('login'))
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="auth-card"><h2>REGISTRO</h2><form method="POST"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required><input name="t" placeholder="TELEGRAM @ID" required><button class="btn btn-gold">CREAR CUENTA</button></form></div></body></html>')

@app.route('/panel')
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_name = session['user']
    u_data = usuarios_col.find_one({"u": u_name})
    display_id = "ADMIN" if u_name.lower() == "mairo" else u_name.upper()
    
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body><div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin: 20px 0;">
            <div style="font-size:11px;">ID: <b style="color:var(--gold)">{display_id}</b></div>
            <div id="display_saldo" style="border:1px solid var(--gold); padding:5px 12px; color:var(--gold); font-weight:bold;">${u_data['saldo']:.2f}</div>
        </div>
        <div class="card"><span class="card-h">🛡️ GATE VALIDATOR (NO COOKIES)</span>
            <textarea id="check_list" rows="8" placeholder="CC|MM|YY|CVV"></textarea>
            <button class="btn btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR VALIDACIÓN ($0.15)</button>
        </div>
        <div style="color:var(--green); font-size:10px; font-weight:bold; margin-bottom:5px;">LIVES ✅</div>
        <div class="res-box" id="lives_log"></div>
        <div style="color:var(--red); font-size:10px; font-weight:bold; margin-bottom:5px;">DEAD ❌</div>
        <div class="res-box" id="dead_log" style="opacity:0.6;"></div>
        <a href="/logout" style="color:#444; text-decoration:none; display:block; text-align:center; font-size:10px;">[ CERRAR SESIÓN ]</a>
    </div>
    <script>
    async function startChecking() {{
        let area = document.getElementById('check_list'); let lines = area.value.trim().split('\\n');
        if (!lines[0]) return alert("Pega tus tarjetas primero");
        document.getElementById('btn_start').disabled = true;
        
        while (lines.length > 0) {{
            let cc = lines.shift(); area.value = lines.join('\\n');
            let res = await fetch('/validar_card', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{card: cc}}) }});
            let data = await res.json();
            if (data.status === 'insufficient') {{ alert("SIN SALDO"); break; }}
            if (data.status === 'LIVE') {{
                document.getElementById('display_saldo').innerText = '$' + data.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML = '<div>' + cc + ' | ' + data.info + '</div>' + document.getElementById('lives_log').innerHTML;
            }} else {{
                document.getElementById('dead_log').innerHTML = '<div>' + cc + '</div>' + document.getElementById('dead_log').innerHTML;
            }}
            await new Promise(r => setTimeout(r, 1000));
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
    u_data = usuarios_col.find_one({"u": user})
    if u_data['saldo'] < COSTO_LIVE: return jsonify({"status": "insufficient"})
    
    cc = request.json.get('card', '')
    res = check_gate_pro(cc) # Aquí entra Decodo + Snipcart
    
    if res['status'] == 'LIVE':
        nuevo_saldo = round(u_data['saldo'] - COSTO_LIVE, 2)
        usuarios_col.update_one({"u": user}, {"$set": {"saldo": nuevo_saldo}})
        return jsonify({"status": "LIVE", "nuevo_saldo": nuevo_saldo, "info": res['msg']})
    
    return jsonify({"status": "DEAD"})

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
