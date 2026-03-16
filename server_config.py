import os, random, time, json, requests, datetime
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'quick_money_v49_final_mastery'

# --- [ CONFIGURACIÓN MAESTRA INTACTA ] ---
MONGO_URI = "mongodb+srv://mairo:mairo1212@cluster0.inuth4k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db_mongo = client['quickmoney_db']
    usuarios_col = db_mongo['usuarios']
    config_col = db_mongo['config']
    historial_col = db_mongo['historial_lives']
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

# --- [ DISEÑO v50 ULTIMATE: HOUDINI EDITION ] ---
CSS_V50 = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Space+Mono:wght@400;700&display=swap');
    :root { 
        --gold: #FFD700; 
        --gold-dark: #b8860b; 
        --bg: #050505; 
        --glass: rgba(255, 255, 255, 0.03); 
        --border: rgba(255, 215, 0, 0.15); 
        --green: #00FF88; --red: #FF3E3E; 
    }
    
    body { 
        background: radial-gradient(circle at center, #111 0%, #050505 100%); 
        color: #fff; font-family: 'Space Mono', monospace; margin: 0; padding: 0; 
    }
    
    .container { max-width: 1200px; margin: auto; padding: 20px; position: relative; z-index: 10; }
    
    /* GLASSMORPHISM CARDS */
    .card { 
        background: var(--glass); backdrop-filter: blur(15px); 
        border: 1px solid var(--border); padding: 25px; margin-bottom: 20px; 
        border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .logo-text { font-family: 'Cinzel', serif; color: var(--gold); font-size: 28px; text-shadow: 0 0 15px rgba(255, 215, 0, 0.4); text-align: center; }
    
    input, textarea { 
        width: 100%; background: rgba(0,0,0,0.4); border: 1px solid var(--border); 
        color: #fff; padding: 15px; margin-bottom: 12px; font-family: inherit; 
        border-radius: 8px; outline: none; transition: 0.3s;
    }
    input:focus { border-color: var(--gold); box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }

    .btn-gold { 
        background: linear-gradient(45deg, var(--gold-dark), var(--gold)); 
        color: #000; width: 100%; border: none; padding: 15px; font-weight: 800; 
        text-transform: uppercase; border-radius: 8px; cursor: pointer; transition: 0.3s;
    }
    .btn-gold:hover { transform: translateY(-2px); box-shadow: 0 5px 20px var(--gold); }
    
    /* HOUDINI OVERLAY */
    #houdini-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.96); display: none; z-index: 9999;
        justify-content: center; align-items: center; flex-direction: column;
    }
    .magic-smoke { width: 350px; height: 350px; }
    .houdini-title { font-family: 'Cinzel', serif; color: var(--gold); font-size: 3rem; margin: 0; opacity: 0; }
    .show-houdini .houdini-title { animation: fadeInScale 0.6s forwards ease-out; }

    @keyframes fadeInScale { 0% { opacity: 0; transform: scale(0.5); } 100% { opacity: 1; transform: scale(1.1); } }
</style>
"""

# --- [ RUTAS DE INTERFAZ ] ---

@app.route('/panel')
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = usuarios_col.find_one({"u": session['user']})
    display_name = "ADMIN" if session['user'].lower() == "mairo" else session['user'].upper()
    is_admin = session['user'].lower() == "mairo"
    
    # Obtener SK actual y Usuarios para el Admin
    current_sk = config_col.find_one({"key": "sk_live"})
    sk_val = current_sk['val'] if current_sk else ""
    all_users = list(usuarios_col.find()) if is_admin else []
    
    return render_template_string(f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        {CSS_V50}
    </head>
    <body>
        <div class="container">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:30px;">
                <h1 class="logo-text">QUICK MONEY v50</h1>
                <div style="text-align:right;">
                    <div style="color:var(--gold); font-size:12px;">ID: {display_name}</div>
                    <div style="font-size:18px; font-weight:bold;" id="display_saldo">${u_data['saldo']:.2f}</div>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                <div class="card">
                    {f'''<span style="color:var(--gold); font-size:12px; font-weight:bold;">👑 ADMIN CONTROL</span><br><br>
                    <form action="/update_sk" method="POST">
                        <input name="new_sk" placeholder="SK_LIVE_..." value="{sk_val}">
                        <button class="btn-gold" style="padding:10px; font-size:10px;">ACTUALIZAR SK</button>
                    </form>
                    <hr style="border:0; border-top:1px solid var(--border); margin:20px 0;">
                    <form action="/admin_add_saldo" method="POST">
                        <input name="target_user" placeholder="USUARIO">
                        <input name="amount" type="number" step="0.01" placeholder="CANTIDAD $">
                        <button class="btn-gold" style="padding:10px; font-size:10px;">CARGAR BALANCE</button>
                    </form>
                    ''' if is_admin else f'''
                    <span style="color:var(--gold); font-size:12px; font-weight:bold;">👤 ACCOUNT DETAILS</span><br><br>
                    <div style="font-size:12px; opacity:0.8;">Telegram ID: {u_data.get('telegram','-')}</div>
                    <div style="font-size:12px; opacity:0.8;">Status: <span style="color:var(--green)">Premium</span></div>
                    '''}
                </div>

                <div class="card">
                    <span style="color:var(--gold); font-size:12px; font-weight:bold;">🪄 HOUDINI CHECKER</span><br><br>
                    <textarea id="check_list" rows="8" placeholder="CC|MM|YY|CVV"></textarea>
                    <button class="btn-gold" id="btn_start" onclick="startChecking()">🚀 INICIAR MAGIA ($0.15)</button>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-top:20px;">
                <div>
                    <span style="color:var(--green); font-size:11px;">LIVES ✅</span>
                    <div id="lives_log" style="height:200px; background:rgba(0,0,0,0.3); border:1px solid var(--border); padding:10px; overflow-y:auto; font-size:12px; margin-top:10px; border-radius:8px;"></div>
                </div>
                <div>
                    <span style="color:var(--red); font-size:11px;">DEADS ❌</span>
                    <div id="dead_log" style="height:200px; background:rgba(0,0,0,0.3); border:1px solid var(--border); padding:10px; overflow-y:auto; font-size:12px; margin-top:10px; border-radius:8px; opacity:0.6;"></div>
                </div>
            </div>
            
            <div style="text-align:center; margin-top:30px; font-size:10px; opacity:0.5;">
                <a href="/logout" style="color:var(--red); text-decoration:none;">CERRAR SESIÓN SEGURO</a>
            </div>
        </div>

        <div id="houdini-overlay">
            <div id="houdini-animation" class="magic-smoke"></div>
            <h1 class="houdini-title">HOUDINI LIVE!</h1>
            <p id="houdini-card" style="letter-spacing:5px; color:#fff; font-size:18px; margin-top:20px;"></p>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.7.6/lottie.min.js"></script>
        <script>
            // Animación del Mago
            var magicAnim = lottie.loadAnimation({{
                container: document.getElementById('houdini-animation'),
                renderer: 'svg', loop: false, autoplay: false,
                path: 'https://assets9.lottiefiles.com/packages/lf20_m6cu9zob.json'
            }});

            async function startChecking() {{
                let a = document.getElementById('check_list'); 
                let lines = a.value.trim().split('\\n');
                if(!lines[0]) return;
                document.getElementById('btn_start').disabled = true;

                for (let cc of lines) {{
                    let r = await fetch('/validar_card', {{
                        method:'POST', 
                        headers:{{'Content-Type':'application/json'}}, 
                        body:JSON.stringify({{card:cc.trim()}})
                    }});
                    let d = await r.json();
                    
                    if(d.status === 'LIVE') {{
                        // ACTIVAR ALERTA HOUDINI
                        showHoudini(cc);
                        document.getElementById('display_saldo').innerText = '$' + d.nuevo_saldo.toFixed(2);
                        document.getElementById('lives_log').innerHTML = '<div style="color:var(--green); margin-bottom:5px;">'+cc+' | AUTHORIZED</div>' + document.getElementById('lives_log').innerHTML;
                    }} else {{
                        document.getElementById('dead_log').innerHTML = '<div>'+cc+' | '+d.msg+'</div>' + document.getElementById('dead_log').innerHTML;
                    }}
                }}
                document.getElementById('btn_start').disabled = false;
            }}

            function showHoudini(card) {{
                const overlay = document.getElementById('houdini-overlay');
                document.getElementById('houdini-card').innerText = card.substring(0,12) + "XXXX";
                overlay.style.display = 'flex';
                overlay.classList.add('show-houdini');
                magicAnim.goToAndPlay(0, true);
                setTimeout(() => {{
                    overlay.style.display = 'none';
                    overlay.classList.remove('show-houdini');
                }}, 3500);
            }}
        </script>
    </body>
    </html>
    """)

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('panel'))
    return render_template_string(f'<html><head>{CSS_V50}</head><body><div style="display:flex; align-items:center; justify-content:center; height:100vh;"><div class="card" style="width:350px; text-align:center;"><h1 class="logo-text">QM v50</h1><br><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="CONTRASEÑA"><button class="btn-gold">ACCEDER AL PANEL</button></form><br><a href="/register" style="color:var(--gold); font-size:10px; text-decoration:none;">CREAR CUENTA NUEVA</a></div></div></body></html>')

# --- [ EL RESTO DE TUS RUTAS REGISTRO/AUTH/ADMIN SE MANTIENEN IGUAL ] ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p, t = request.form.get('u'), request.form.get('p'), request.form.get('t')
        if not usuarios_col.find_one({"u": u}):
            usuarios_col.insert_one({"u": u, "p": p, "saldo": 0.0, "rango": "USER", "telegram": t})
            return redirect(url_for('login'))
    return render_template_string(f'<html><head>{CSS_V50}</head><body><div style="display:flex; align-items:center; justify-content:center; height:100vh;"><div class="card" style="width:350px; text-align:center;"><h2 class="logo-text">REGISTRO</h2><form method="POST"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><input name="t" placeholder="TELEGRAM @ID"><button class="btn-gold">REGISTRARSE</button></form></div></div></body></html>')

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
        fecha = datetime.datetime.now().strftime("%d/%m %H:%M")
        historial_col.insert_one({"usuario": session['user'], "cc": cc, "fecha": fecha})
        return jsonify({"status": "LIVE", "nuevo_saldo": new_s})
    return jsonify({"status": "DEAD", "msg": res['msg']})

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    user_db = usuarios_col.find_one({"u": u, "p": p})
    if user_db: session['user'] = u
    return redirect(url_for('panel'))

@app.route('/update_sk', methods=['POST'])
def update_sk():
    if session.get('user', '').lower() != "mairo": return redirect(url_for('panel'))
    config_col.update_one({"key": "sk_live"}, {"$set": {"val": request.form.get('new_sk').strip()}}, upsert=True)
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
