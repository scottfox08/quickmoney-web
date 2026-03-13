import os, random, time, requests
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'mairo_v16_final_shield'

# --- MONGODB ATLAS ---
MONGO_URI = "mongodb+srv://mairo:Mairo1212@cluster0.inuth4k.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client['QuickMoneyDB']
users_col = db['usuarios']

# Garantizar Owner
if not users_col.find_one({"u": "mairo"}):
    users_col.insert_one({"u": "mairo", "p": "1234", "saldo": 999999.0, "rango": "OWNER"})

COSTO_LIVE = 0.35

CSS = """
<style>
    :root { --gold: #d4af37; --bg: #050507; --card: rgba(22, 26, 35, 0.95); --green: #2ecc71; --red: #ff4757; --border: #2d323e; }
    body { background: radial-gradient(circle at center, #1a150a 0%, #050507 70%); background-attachment: fixed; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; min-height: 100vh; }
    .container { max-width: 550px; margin: auto; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); }
    input, textarea { width: 100%; background: #08090d; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box; }
    .btn { border: none; padding: 14px; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; width: 100%; }
    .btn-verify { background: linear-gradient(135deg, #d4af37 0%, #aa8a2e 100%); color: #000; }
    .badge-saldo { background: #1e2533; padding: 8px 20px; border-radius: 30px; border: 1px solid var(--gold); color: var(--gold); font-weight: bold; }
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px;text-align:center;border-top:4px solid var(--gold);"><h2>🦁 QM ELITE</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="PASS" required><button class="btn btn-verify">INGRESAR</button></form></div></body></html>')

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    user = users_col.find_one({"u": u, "p": p})
    if user: session['user'] = u
    return redirect(url_for('panel'))

@app.route('/panel')
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = users_col.find_one({"u": session['user']})
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body><div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:20px;">
            <span>OWNER: <b>{session['user'].upper()}</b></span>
            <div id="display_saldo" class="badge-saldo">${u_data['saldo']:.2f}</div>
        </div>
        <div class="card" style="margin-top:20px;">
            <textarea id="check_list" rows="8" placeholder="LISTA CC|MM|YY|CVV"></textarea>
            <button class="btn btn-verify" onclick="startChecking()">🚀 VALIDAR</button>
        </div>
        <div class="card" style="color:var(--green);"><div id="lives_log">LIVES:</div></div>
        <div class="card" style="color:var(--red);"><div id="dead_log">DEAD:</div></div>
        <button class="btn" style="background:#ff4757; color:#fff;" onclick="location.href='/logout'">SALIR</button>
    </div>
    <script>
    async function startChecking() {{
        let area = document.getElementById('check_list');
        let lines = area.value.trim().split('\\n');
        while (lines.length > 0) {{
            let currentCC = lines.shift(); area.value = lines.join('\\n');
            let res = await fetch('/validar_card', {{ 
                method: 'POST', 
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{card: currentCC}})
            }});
            let data = await res.json();
            if (data.status === 'LIVE') {{
                document.getElementById('display_saldo').innerText = '$' + data.nuevo_saldo.toFixed(2);
                document.getElementById('lives_log').innerHTML += '<br>' + currentCC;
            }} else {{
                document.getElementById('dead_log').innerHTML += '<br>' + currentCC;
            }}
            await new Promise(r => setTimeout(r, 1000));
        }}
    }}
    </script></body></html>
    """)

@app.route('/validar_card', methods=['POST'])
def validar():
    user = session.get('user')
    u_data = users_col.find_one({"u": user})
    if not u_data or u_data['saldo'] < COSTO_LIVE: return jsonify({{"error": "Sin saldo"}}), 400
    is_live = random.random() > 0.8
    if is_live:
        new_saldo = round(u_data['saldo'] - COSTO_LIVE, 2)
        users_col.update_one({{"u": user}}, {{"$set": {{"saldo": new_saldo}}}})
        return jsonify({{"status": "LIVE", "nuevo_saldo": new_saldo}})
    return jsonify({{"status": "DEAD"}})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
