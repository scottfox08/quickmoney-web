import os, random, time, json, requests, datetime
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'quick_money_v50_houdini_mastery'

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

# --- [ DISEÑO v50 ULTIMATE: HOUDINI GHOST EDITION ] ---
CSS_V50 = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    :root { 
        --green: #00FF41; /* Verde Matrix/Hacker */
        --white: #FFFFFF;
        --bg: #000000;
        --glass: rgba(255, 255, 255, 0.05);
        --border: rgba(0, 255, 65, 0.2);
    }
    
    body { 
        background-color: var(--bg);
        color: var(--white);
        font-family: 'JetBrains Mono', monospace;
        margin: 0; padding: 0;
        overflow-x: hidden;
    }

    /* FONDO ANIMADO DE HOUDINI FLOTANDO */
    #floating-ghost {
        position: fixed;
        top: 10%;
        left: 50%;
        transform: translateX(-50%);
        width: 300px;
        height: 300px;
        z-index: 1;
        opacity: 0.15;
        pointer-events: none;
        animation: float 6s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translate(-50%, 0px); }
        50% { transform: translate(-50%, -30px); }
    }

    .container { max-width: 1200px; margin: auto; padding: 20px; position: relative; z-index: 10; }
    
    .card { 
        background: var(--glass); backdrop-filter: blur(10px); 
        border: 1px solid var(--border); padding: 20px; margin-bottom: 20px; 
        border-radius: 4px; box-shadow: 0 0 20px rgba(0,255,65,0.05);
    }
    
    .logo-text { color: var(--green); font-size: 24px; font-weight: bold; letter-spacing: 5px; text-align: center; }
    
    input, textarea { 
        width: 100%; background: #000; border: 1px solid var(--border); 
        color: var(--green); padding: 12px; margin-bottom: 10px; font-family: inherit; 
        border-radius: 2px; outline: none;
    }

    .btn-green { 
        background: var(--green); color: #000; width: 100%; border: none; 
        padding: 12px; font-weight: bold; text-transform: uppercase; cursor: pointer;
    }
    .btn-dark { background: #111; color: var(--white); border: 1px solid var(--border); padding: 8px; cursor: pointer; }

    .res-box { height: 180px; background: #000; border: 1px solid var(--border); padding: 10px; overflow-y: auto; font-size: 11px; border-radius: 2px; }
</style>
"""

@app.route('/panel')
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = usuarios_col.find_one({"u": session['user']})
    is_admin = session['user'].lower() == "mairo"
    
    current_sk = config_col.find_one({"key": "sk_live"})
    sk_val = current_sk['val'] if current_sk else ""
    all_users = list(usuarios_col.find()) if is_admin else []
    
    return render_template_string(f"""
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS_V50}</head>
    <body>
        <div id="floating-ghost">
            <img src="https://cdn-icons-png.flaticon.com/512/2833/2833757.png" width="100%" style="filter: invert(1) sepia(1) saturate(5) hue-rotate(90deg);">
        </div>

        <div class="container">
            <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                <h1 class="logo-text">QUICK MONEY v50</h1>
                <div style="text-align:right; color:var(--green);">
                    BALANCE: <span id="display_saldo">${u_data['saldo']:.2f}</span>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                <div class="card">
                    {f'''<span style="color:var(--green); font-size:10px;">👑 ADMIN CONTROL</span><br><br>
                    <input id="new_sk" placeholder="SK_LIVE_..." value="{sk_val}">
                    <button class="btn-green" onclick="updateSK()" style="font-size:10px;">ACTUALIZAR MOTOR</button>
                    ''' if is_admin else '<span>USER PANEL ACTIVE</span>'}
                    
                    <br><br><span style="color:var(--white); font-size:10px;">⚡ GENERADOR</span>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <input id="bin_val" value="473702" style="margin-bottom:0;">
                        <button class="btn-dark" onclick="generar()">GENERAR</button>
                    </div>
                </div>

                <div class="card">
                    <span style="color:var(--green); font-size:10px;">🔮 CHECKER</span><br><br>
                    <textarea id="check_list" rows="8" placeholder="CC|MM|YY|CVV"></textarea>
                    <button class="btn-green" id="btn_start" onclick="startChecking()">EJECUTAR HECHIZO ($0.15)</button>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px; margin-top:20px;">
                <div>
                    <span style="color:var(--green); font-size:10px;">LIVES ✅</span>
                    <div id="lives_log" class="res-box" style="border-color: var(--green);"></div>
                </div>
                <div>
                    <span style="color:var(--white); font-size:10px;">DEADS ❌</span>
                    <div id="dead_log" class="res-box" style="opacity:0.5;"></div>
                </div>
                <div>
                    <span style="color:#FFCC00; font-size:10px;">⚠️ ERRORES</span>
                    <div id="error_log" class="res-box" style="border-color: #FFCC00; color: #FFCC00;"></div>
                </div>
            </div>
            
            <div style="text-align:center; margin-top:20px;"><a href="/logout" style="color:red; font-size:10px; text-decoration:none;">DISCONNECT</a></div>
        </div>

        <script>
            function generar() {{
                let bin = document.getElementById('bin_val').value;
                let out = "";
                for(let i=0; i<10; i++) {{
                    let n = bin; while(n.length < 16) n += Math.floor(Math.random()*10);
                    let m = String(Math.floor(Math.random()*12)+1).padStart(2,'0');
                    let y = 2025 + Math.floor(Math.random()*6);
                    let c = Math.floor(Math.random()*899)+100;
                    out += n+"|"+m+"|"+y+"|"+c+"\\n";
                }}
                document.getElementById('check_list').value = out;
            }}

            async function startChecking() {{
                let lines = document.getElementById('check_list').value.trim().split('\\n');
                if(!lines[0]) return;
                document.getElementById('btn_start').disabled = true;

                for (let cc of lines) {{
                    try {{
                        let r = await fetch('/validar_card', {{
                            method:'POST', 
                            headers:{{'Content-Type':'application/json'}}, 
                            body:JSON.stringify({{card:cc.trim()}})
                        }});
                        let d = await r.json();
                        
                        if(d.status === 'LIVE') {{
                            document.getElementById('lives_log').innerHTML = '<div>'+cc+'</div>' + document.getElementById('lives_log').innerHTML;
                            document.getElementById('display_saldo').innerText = '$' + d.nuevo_saldo.toFixed(2);
                        }} else if(d.msg.includes('ERROR') || d.msg.includes('SK')) {{
                            document.getElementById('error_log').innerHTML = '<div>'+cc+' | '+d.msg+'</div>' + document.getElementById('error_log').innerHTML;
                        }} else {{
                            document.getElementById('dead_log').innerHTML = '<div>'+cc+'</div>' + document.getElementById('dead_log').innerHTML;
                        }}
                    }} catch(e) {{
                        document.getElementById('error_log').innerHTML = '<div>SYSTEM TIMEOUT</div>' + document.getElementById('error_log').innerHTML;
                    }}
                }}
                document.getElementById('btn_start').disabled = false;
            }}
        </script>
    </body>
    </html>
    """)

# --- [ EL RESTO DE TUS RUTAS REGISTRO/AUTH/ADMIN SIGUEN IGUAL ] ---
@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS_V50}</head><body><div style="display:flex; align-items:center; justify-content:center; height:100vh;"><div class="card" style="width:300px; text-align:center;"><h1 class="logo-text">QM v50</h1><form method="POST" action="/auth"><input name="u" placeholder="USER"><input type="password" name="p" placeholder="PASS"><button class="btn-green">ENTER</button></form></div></div></body></html>')

@app.route('/validar_card', methods=['POST'])
def validar():
    u_data = usuarios_col.find_one({"u": session['user']})
    if u_data['saldo'] < COSTO_LIVE: return jsonify({"status":"DEAD", "msg": "SIN SALDO"})
    cc = request.json.get('card', '')
    # Por ahora simula live para que pruebes el diseño
    new_s = round(u_data['saldo'] - COSTO_LIVE, 2)
    usuarios_col.update_one({"u": session['user']}, {"$set": {"saldo": new_s}})
    return jsonify({"status": "LIVE", "nuevo_saldo": new_s})

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    user_db = usuarios_col.find_one({"u": u, "p": p})
    if user_db: session['user'] = u
    return redirect(url_for('panel'))

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
