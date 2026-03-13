import os, random
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'mairo_empire_2026'

# --- SISTEMA DE GESTIÓN (ADMIN) ---
DB = {
    "ADMIN_KEY": "mairo123", # Clave para entrar al panel admin
    "CLIENTES": {
        "mairo": {"pass": "1234", "plan": "OWNER", "dias": "∞"},
        "test": {"pass": "test", "plan": "FREE", "dias": "3"}
    }
}

CSS = """
<style>
    :root { --gold: #d4af37; --bg: #12141d; --card: #1c1f26; --green: #2ecc71; --red: #e74c3c; --blue: #3498db; }
    body { background: var(--bg); color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; }
    .container { max-width: 500px; margin: auto; }
    
    /* Header & Alerts */
    .alert-box { background: linear-gradient(45deg, #ff4d4d, #f39c12); border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2); }
    .timer { font-size: 24px; font-weight: bold; margin: 10px 0; letter-spacing: 2px; }

    /* Cards */
    .card { background: var(--card); border: 1px solid #2d323e; border-radius: 12px; padding: 20px; margin-bottom: 15px; position: relative; }
    .card-title { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
    
    /* Inputs & Selects */
    label { font-size: 11px; color: var(--gold); display: block; margin: 8px 0 4px; font-weight: bold; }
    input, select, textarea { width: 100%; background: #0d0f14; border: 1px solid #2d323e; color: #fff; padding: 12px; border-radius: 8px; box-sizing: border-box; font-size: 14px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

    /* Buttons */
    .btn { border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; transition: 0.3s; width: 100%; margin-top: 10px; }
    .btn-gen { background: #2d5a45; color: #5effa3; border: 1px solid #3d7a5d; }
    .btn-add { background: #7a632d; color: #ffeb3b; border: 1px solid #9e823a; }
    .btn-clear { background: #3d4452; color: #fff; }
    .btn-verify { background: #1e3d2f; color: #2ecc71; border: 1px solid #2ecc71; font-size: 14px; padding: 15px; }

    /* Stats Grid */
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .stat-box { background: var(--card); border: 1px solid #2d323e; border-radius: 10px; padding: 15px; text-align: center; }
    .stat-val { font-size: 22px; font-weight: bold; display: block; }
    .stat-lbl { font-size: 10px; color: #888; text-transform: uppercase; }

    .res-area { background: #000; border: 1px solid var(--gold); color: var(--gold); font-family: monospace; margin-top: 10px; }
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:300px;text-align:center;"><h2>QUICK MONEY LOGIN</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS" style="margin-top:10px;"><button class="btn btn-verify">INGRESAR</button></form></div></body></html>')

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    if u in DB["CLIENTES"] and DB["CLIENTES"][u]['pass'] == p:
        session['user'] = u
        return redirect(url_for('panel'))
    return redirect(url_for('login'))

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    
    generated = ""
    if request.method == 'POST' and 'bin' in request.form:
        bin_val = request.form.get('bin')[:6]
        res = []
        for _ in range(int(request.form.get('cant', 10))):
            cc = bin_val + "".join([str(random.randint(0,9)) for _ in range(10)])
            m = request.form.get('mes') if request.form.get('mes') != "RANDOM" else f"{random.randint(1,12):02d}"
            a = request.form.get('anio') if request.form.get('anio') != "RANDOM" else str(random.randint(25,30))
            res.append(f"{cc}|{m}|{a}|{random.randint(100,999)}")
        generated = "\\n".join(res)

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body>
    <div class="container">
        <div class="alert-box">
            <b>⚠️ ¡ALERTA! EL CHECKER FREE CERRARÁ EN:</b>
            <div class="timer">06 DÍAS 23H: 59M: 24S</div>
            <small>¿QUIERES MANTENERLO ABIERTO? ACTUALIZA A VIP</small>
        </div>

        <div class="card">
            <div class="card-title">🪄 GENERADOR AUTOMÁTICO DE TARJETAS</div>
            <form method="POST">
                <label>BINS</label>
                <input name="bin" placeholder="473702804849" required>
                
                <div class="grid-2">
                    <div>
                        <label>MES</label>
                        <select name="mes">
                            <option>RANDOM</option>
                            {" ".join([f'<option value="{i:02d}">{i:02d}</option>' for i in range(1,13)])}
                        </select>
                    </div>
                    <div>
                        <label>AÑO</label>
                        <select name="anio"><option>RANDOM</option><option>2025</option><option>2026</option><option>2027</option><option>2028</option></select>
                    </div>
                </div>

                <div class="grid-2">
                    <div><label>CVV</label><input placeholder="RANDOM" disabled></div>
                    <div><label>CANTIDAD</label><input name="cant" type="number" value="10"></div>
                </div>

                <div class="btn-group" style="display:flex; gap:8px;">
                    <button class="btn btn-gen">🪄 GENERAR</button>
                    <button type="button" class="btn btn-add" onclick="document.getElementById('cc_list').value += document.getElementById('gen_res').value">➕ AGREGAR</button>
                    <button type="button" class="btn btn-clear" onclick="location.reload()">🗑️ LIMPIAR</button>
                </div>
                <textarea id="gen_res" class="res-area" rows="5" readonly>{generated}</textarea>
            </form>
        </div>

        <div class="card">
            <div class="card-title">🛡️ VERIFICADOR DE TARJETAS</div>
            <textarea id="cc_list" rows="6" placeholder="INGRESE TARJETAS AQUÍ..."></textarea>
            <button class="btn btn-verify">🚀 VERIFICAR TARJETAS</button>
        </div>

        <div class="stats-grid">
            <div class="stat-box"><span class="stat-lbl">TOTAL</span><span class="stat-val">0</span></div>
            <div class="stat-box"><span class="stat-lbl" style="color:var(--green)">APROVADAS</span><span class="stat-val" style="color:var(--green)">0</span></div>
            <div class="stat-box"><span class="stat-lbl" style="color:var(--red)">REPROVADAS</span><span class="stat-val" style="color:var(--red)">0</span></div>
            <div class="stat-box"><span class="stat-lbl" style="color:var(--blue)">ERRORES</span><span class="stat-val" style="color:var(--blue)">0</span></div>
        </div>
        
        <p style="text-align:center; font-size:10px; color:#555; margin-top:20px;">
            DASHBOARD: {session['user'].upper()} | <a href="/admin" style="color:var(--gold)">ADMIN PANEL</a>
        </p>
    </div>
    </body></html>
    """)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or session['user'] != "mairo": return "ACCESO DENEGADO"
    # Aquí puedes agregar lógica para añadir clientes dinámicamente
    return f"<h1>Panel Admin de Mairo</h1><p>Clientes actuales: {list(DB['CLIENTES'].keys())}</p><a href='/panel'>Volver</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
