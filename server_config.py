from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests
import random

app = Flask(__name__)
app.secret_key = 'quickmoney_ultra_admin_2026'

# --- CONFIG ---
LOGO_LINK = "https://images2.imgbox.com/7d/5d/q9Hn5lP4_o.png" 
USUARIOS = {"mairo": {"pass": "1234", "role": "GOLDEN ADMIN", "credits": "∞"}}

# --- LÓGICA DEL GENERADOR ---
def generar_cc(bin_code):
    cc_list = []
    for _ in range(10):
        num = str(bin_code)
        while len(num) < 16:
            num += str(random.randint(0, 9))
        mm = str(random.randint(1, 12)).zfill(2)
        yy = random.randint(25, 30)
        cvv = str(random.randint(100, 999))
        cc_list.append(f"{num}|{mm}|{yy}|{cvv}")
    return cc_list

# --- ESTILOS ---
CSS = f"""
<style>
    :root {{ --main: #ffffff; --bg: #000000; --accent: #00ffcc; --glass: rgba(20,20,20,0.85); }}
    body {{ 
        background: var(--bg) url('{LOGO_LINK}') no-repeat center center fixed; 
        background-size: cover; color: #fff; font-family: 'Montserrat', sans-serif; margin: 0; overflow: hidden;
    }}
    .overlay {{ background: rgba(0,0,0,0.8); height: 100vh; display: flex; flex-direction: column; }}
    
    /* Navbar */
    .nav {{ 
        background: rgba(10,10,10,0.95); padding: 15px 30px; border-bottom: 1px solid #333;
        display: flex; justify-content: space-between; align-items: center;
    }}
    
    /* Layout */
    .main-wrapper {{ display: flex; flex: 1; overflow: hidden; }}
    
    /* Sidebar */
    .sidebar {{ 
        width: 260px; background: rgba(5,5,5,0.9); border-right: 1px solid #222; 
        padding: 20px; display: flex; flex-direction: column; gap: 10px;
    }}
    .nav-btn {{ 
        background: transparent; border: 1px solid #333; color: #888; padding: 12px;
        text-align: left; border-radius: 8px; cursor: pointer; transition: 0.3s; font-weight: bold;
    }}
    .nav-btn:hover, .nav-btn.active {{ background: #fff; color: #000; box-shadow: 0 0 15px #fff; }}

    /* Content Area */
    .content {{ flex: 1; padding: 40px; overflow-y: auto; display: flex; justify-content: center; }}
    .panel {{ 
        background: var(--glass); border: 1px solid #333; border-radius: 20px; padding: 30px;
        width: 100%; max-width: 800px; backdrop-filter: blur(10px); display: none;
    }}
    .panel.active {{ display: block; animation: fadeIn 0.5s; }}

    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    .btn-main {{ 
        background: #fff; color: #000; border: none; padding: 15px; border-radius: 8px;
        width: 100%; font-weight: bold; cursor: pointer; text-transform: uppercase;
    }}
    textarea, input {{ 
        width: 100%; background: #000; border: 1px solid #444; color: #fff; 
        padding: 12px; border-radius: 8px; margin-bottom: 15px; box-sizing: border-box;
    }}
    .badge-admin {{ background: var(--accent); color: #000; padding: 3px 8px; border-radius: 4px; font-size: 10px; }}
</style>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u in USUARIOS and USUARIOS[u]['pass'] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex; align-items:center; justify-content:center;"><div class="panel" style="display:block; max-width:350px; text-align:center;"><h1>QUICK MONEY</h1><form method="POST"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS"><button class="btn-main">ENTRAR</button></form></div></body></html>')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    user_data = USUARIOS[u]
    return render_template_string(f"""
    <html><head><title>QUICK MONEY ELITE</title>{CSS}
    <script>
        function showPanel(id) {{
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
    </head>
    <body>
    <div class="overlay">
        <div class="nav">
            <b>🦁 QUICK MONEY SYSTEM</b>
            <span>{u} <span class="badge-admin">{user_data['role']}</span> | Creds: <b style="color:var(--accent)">{user_data['credits']}</b></span>
        </div>
        
        <div class="main-wrapper">
            <div class="sidebar">
                <button class="nav-btn active" onclick="showPanel('p-checker')">💎 CC CHECKER</button>
                <button class="nav-btn" onclick="showPanel('p-gen')">⚡ GENERADOR V2</button>
                <button class="nav-btn" onclick="showPanel('p-bin')">🔎 BIN LOOKUP</button>
                <button class="nav-btn" onclick="showPanel('p-proxy')">🛡️ PROXY TESTER</button>
                <br>
                <a href="/logout" style="color:red; text-decoration:none; font-size:12px; padding:10px;">CERRAR SESIÓN</a>
            </div>
            
            <div class="content">
                <div id="p-checker" class="panel active">
                    <h3>CC CHECKER ELITE</h3>
                    <textarea id="list-checker" rows="10" placeholder="CC|MM|YY|CVV"></textarea>
                    <button class="btn-main">INICIAR VALIDACIÓN</button>
                </div>

                <div id="p-gen" class="panel">
                    <h3>⚡ GENERADOR POR BIN</h3>
                    <input type="text" id="bin-input" placeholder="Introduce BIN (ej: 414720)">
                    <button class="btn-main" onclick="alert('Generando tarjetas...')">GENERAR CARDS</button>
                    <textarea id="gen-results" rows="8" style="margin-top:15px;" readonly></textarea>
                </div>

                <div id="p-bin" class="panel">
                    <h3>🔎 CONSULTA DE BIN</h3>
                    <input type="text" placeholder="BIN a consultar...">
                    <button class="btn-main">BUSCAR INFO</button>
                </div>

                <div id="p-proxy" class="panel">
                    <h3>🛡️ STATUS DE RED</h3>
                    <div style="background:#111; padding:15px; border-radius:8px;">
                        <p>Proxy Decodo: <span style="color:var(--accent)">CONECTADO ✅</span></p>
                        <p>Latencia: 120ms</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    </body></html>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
