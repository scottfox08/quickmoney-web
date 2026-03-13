import os, random
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'mairo_ultimate_owner_2026'

# --- BASE DE DATOS (Simulada para persistencia en sesión) ---
# En un negocio real, aquí conectarías una base de datos SQL.
DB = {
    "admin_user": "mairo",
    "usuarios": {
        "mairo": {"pass": "1234", "saldo": 999999, "rango": "OWNER"},
        "cliente1": {"pass": "pago10", "saldo": 0, "rango": "VIP"}
    }
}

CSS = """
<style>
    :root { --gold: #d4af37; --bg: #0c0e14; --card: #161a23; --green: #2ecc71; --red: #e74c3c; --border: #2d323e; }
    body { background: var(--bg); color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; }
    .container { max-width: 550px; margin: auto; padding-bottom: 50px; }
    
    /* Estilo de Tarjetas */
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .card-h { font-size: 11px; color: var(--gold); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; border-bottom: 1px solid var(--border); padding-bottom: 8px; display: block; font-weight: bold; }
    
    /* Inputs */
    label { font-size: 10px; color: #888; display: block; margin-bottom: 5px; }
    input, select, textarea { width: 100%; background: #0d0f14; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 12px; box-sizing: border-box; font-size: 14px; transition: 0.3s; }
    input:focus { border-color: var(--gold); outline: none; }
    
    /* Textarea corregido para que no se vea mal */
    textarea { font-family: 'Consolas', monospace; color: #00ffcc; line-height: 1.5; white-space: pre; overflow-x: auto; resize: vertical; }

    /* Botones */
    .btn { border: none; padding: 14px; border-radius: 6px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; transition: 0.2s; width: 100%; }
    .btn-gen { background: #2d5a45; color: #5effa3; border: 1px solid #3d7a5d; }
    .btn-add { background: #7a632d; color: #ffeb3b; border: 1px solid #9e823a; }
    .btn-verify { background: linear-gradient(45deg, #1e3d2f, #2ecc71); color: #fff; box-shadow: 0 4px 15px rgba(46, 204, 113, 0.2); }
    .btn-admin { background: #242933; border: 1px solid var(--gold); color: var(--gold); margin-top: 10px; }
    .btn:hover { filter: brightness(1.2); transform: translateY(-1px); }

    .header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 10px; }
    .badge { background: #1e2533; padding: 6px 15px; border-radius: 20px; border: 1px solid var(--gold); color: var(--gold); font-size: 12px; font-weight: bold; }
</style>
"""

@app.route('/')
def login():
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;align-items:center;justify-content:center;height:100vh;"><div class="card" style="width:320px;text-align:center;"><h2 style="letter-spacing:2px;">🦁 QUICK MONEY</h2><form method="POST" action="/auth"><input name="u" placeholder="USUARIO" required><input type="password" name="p" placeholder="CONTRASEÑA" required><button class="btn btn-verify">ACCEDER AL PANEL</button></form></div></body></html>')

@app.route('/auth', methods=['POST'])
def auth():
    u, p = request.form.get('u'), request.form.get('p')
    if u in DB["usuarios"] and DB["usuarios"][u]['pass'] == p:
        session['user'] = u
        return redirect(url_for('panel'))
    return redirect(url_for('login'))

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'user' not in session: return redirect(url_for('login'))
    u_data = DB["usuarios"][session['user']]
    
    generated_cc = ""
    if request.method == 'POST' and 'bin' in request.form:
        bin_val = request.form.get('bin', '').replace(" ", "")[:6]
        if len(bin_val) >= 6:
            cards = []
            for _ in range(int(request.form.get('cant', 10))):
                cc = bin_val + "".join([str(random.randint(0,9)) for _ in range(10)])
                m = request.form.get('mes') if request.form.get('mes') != "RANDOM" else f"{random.randint(1,12):02d}"
                a = request.form.get('anio') if request.form.get('anio') != "RANDOM" else str(random.randint(25,30))
                cards.append(f"{cc}|{m}|{a}|{random.randint(100,999)}")
            generated_cc = "\n".join(cards) # Salto de línea real

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">{CSS}</head>
    <body>
    <div class="container">
        <div class="header-bar">
            <span>HOLA, <b>{session['user'].upper()}</b></span>
            <div class="badge">SALDO: ${u_data['saldo']}</div>
        </div>

        <div class="card">
            <span class="card-h">🪄 GENERADOR DE TARJETAS (FORMATO LIMPIO)</span>
            <form method="POST">
                <label>BIN (6 DÍGITOS)</label>
                <input name="bin" placeholder="473702" value="{request.form.get('bin', '')}">
                
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <div><label>MES</label><select name="mes"><option>RANDOM</option>{" ".join([f'<option>{i:02d}</option>' for i in range(1,13)])}</select></div>
                    <div><label>AÑO</label><select name="anio"><option>RANDOM</option><option>2025</option><option>2026</option><option>2027</option><option>2028</option></select></div>
                </div>

                <label>CANTIDAD</label>
                <input name="cant" type="number" value="10">

                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:10px;">
                    <button class="btn btn-gen" type="submit">🪄 GENERAR</button>
                    <button class="btn btn-add" type="button" onclick="document.getElementById('checker_input').value += document.getElementById('output_gen').value + '\\n'; alert('¡Agregadas al Checker!')">➕ AGREGAR</button>
                </div>
                <textarea id="output_gen" rows="6" readonly style="margin-top:15px;" placeholder="Resultados aquí...">{generated_cc}</textarea>
            </form>
        </div>

        <div class="card">
            <span class="card-h">🛡️ VALIDAR CON COOKIE AMAZON</span>
            <label>AMAZON COOKIE</label>
            <input placeholder="Pegue la cookie aquí...">
            
            <label>LISTA DE TARJETAS</label>
            <textarea id="checker_input" rows="6" placeholder="CC|MM|YY|CVV"></textarea>
            
            <button class="btn btn-verify" onclick="alert('Procesando... Cada tarjeta descuenta saldo.')">🚀 INICIAR VALIDACIÓN</button>
        </div>

        { f'<a href="/admin" class="btn btn-admin" style="display:block; text-align:center; text-decoration:none;">⚙️ PANEL DE ADMINISTRACIÓN</a>' if u_data['rango'] == 'OWNER' else '' }
        
        <a href="/logout" style="display:block; text-align:center; color:var(--red); margin-top:20px; font-size:11px; text-decoration:none;">CERRAR SESIÓN</a>
    </div>
    </body></html>
    """)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or DB["usuarios"][session['user']]['rango'] != 'OWNER':
        return "<h1>ACCESO PROHIBIDO</h1>"
    
    msg = ""
    if request.method == 'POST':
        target = request.form.get('user_to_pay')
        monto = int(request.form.get('monto', 0))
        if target in DB["usuarios"]:
            DB["usuarios"][target]['saldo'] += monto
            msg = f"✅ Se cargaron ${monto} a {target} correctamente."

    return render_template_string(f"""
    <html><head>{CSS}</head><body>
    <div class="container" style="margin-top:50px;">
        <div class="card">
            <span class="card-h">⚙️ CONTROL DE SALDO Y CLIENTES</span>
            {f'<div style="color:var(--green); font-size:12px; margin-bottom:15px;">{msg}</div>' if msg else ''}
            
            <form method="POST">
                <label>SELECCIONAR CLIENTE</label>
                <select name="user_to_pay">
                    {" ".join([f'<option value="{u}">{u} (Saldo: ${DB["usuarios"][u]["saldo"]})</option>' for u in DB["usuarios"]])}
                </select>
                
                <label>SALDO A AGREGAR ($)</label>
                <input type="number" name="monto" placeholder="Ej: 50" required>
                
                <button class="btn btn-verify">💰 CARGAR SALDO AHORA</button>
            </form>
            <a href="/panel" style="display:block; text-align:center; color:var(--gold); margin-top:20px; text-decoration:none;">← Volver al Panel de Checker</a>
        </div>
    </div>
    </body></html>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
