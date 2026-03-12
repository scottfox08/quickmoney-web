from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'quickmoney_elite_final_2026'

# --- LINK DE LA IMAGEN (Subida a la nube para que no pese) ---
# Usamos un link directo para que Render no se trabe procesando archivos pesados
LOGO_LINK = "https://images2.imgbox.com/3d/0b/I2UfXp4y_o.png" 

# --- CONFIGURACIÓN ---
PX = {"http": "http://sp6jzqtaou:rUd7t65FxkK+x3F1hr@gate.decodo.com:10001", "https": "http://sp6jzqtaou:rUd7t65FxkK+x3F1hr@gate.decodo.com:10001"}
USUARIOS = {"mairo": {"pass": "1234", "credits": 10000}}

def get_bin(cc):
    try:
        r = requests.get(f"https://lookup.binlist.net/{cc[:6]}", proxies=PX, timeout=4)
        if r.status_code == 200:
            d = r.json()
            b = d.get('bank', {}).get('name', 'BCO')
            p = d.get('country', {}).get('name', 'S/N')
            e = d.get('country', {}).get('emoji', '🌐')
            return f"{e} {p} | {b}"
    except: pass
    return "🌐 Info no disponible"

# --- DISEÑO ELITE OPTIMIZADO ---
CSS = f"""
<style>
    :root {{ --silver: #e0e0e0; --black: #000000; --accent: #ffffff; }}
    body {{ 
        background: var(--black) url('{LOGO_LINK}') no-repeat center center fixed; 
        background-size: cover; color: var(--silver); font-family: 'Segoe UI', sans-serif; margin: 0; 
    }}
    .overlay {{ background: rgba(0,0,0,0.8); min-height: 100vh; width: 100%; display: flex; flex-direction: column; }}
    .nav {{ background: rgba(10,10,15,0.95); padding: 20px; border-bottom: 1px solid var(--accent); display: flex; justify-content: space-between; align-items: center; box-shadow: 0 0 20px rgba(255,255,255,0.1); }}
    .card {{ background: rgba(10,10,10,0.9); border: 1px solid #444; border-radius: 15px; padding: 30px; margin: 20px auto; max-width: 700px; box-shadow: 0 0 40px rgba(0,0,0,0.8); border-top: 2px solid var(--silver); backdrop-filter: blur(8px); }}
    .btn {{ background: linear-gradient(135deg, #fff 0%, #888 100%); color: #000; border: none; padding: 15px; border-radius: 8px; font-weight: bold; width: 100%; cursor: pointer; text-transform: uppercase; transition: 0.3s; }}
    .btn:hover {{ transform: scale(1.02); box-shadow: 0 0 20px rgba(255,255,255,0.4); }}
    input, textarea {{ width: 100%; background: rgba(0,0,0,0.85); color: #fff; border: 1px solid #555; padding: 12px; margin-bottom: 15px; border-radius: 8px; box-sizing: border-box; font-size: 16px; }}
    .live-row {{ border-bottom: 1px solid #333; padding: 12px; font-family: 'Courier New', monospace; display: flex; justify-content: space-between; }}
</style>
"""

@app.route('/')
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u == "mairo" and p == "1234":
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string(f'<html><head><title>QUICK MONEY | LOGIN</title>{CSS}</head><body><div class="overlay" style="justify-content:center; align-items:center;"><div class="card" style="width:350px; text-align:center;"><h1 style="letter-spacing:5px; text-shadow: 0 0 10px white;">QUICK MONEY</h1><form method="POST"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASSWORD"><button class="btn">ACCEDER AL TRONO</button></form></div></div></body></html>', methods=['GET', 'POST'])

# --- RUTA PARA PROCESAR EL POST DEL LOGIN ---
@app.route('/login', methods=['POST'])
def login_post():
    u, p = request.form.get('u'), request.form.get('p')
    if u == "mairo" and p == "1234":
        session['user'] = u
        return redirect(url_for('dashboard'))
    return "Error. <a href='/'>Volver</a>"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template_string(f'<html><head><title>QUICK MONEY | TERMINAL</title>{CSS}</head><body><div class="overlay"><div class="nav"><b>🦁 QUICK MONEY ELITE</b> <a href="/logout" style="color:red; text-decoration:none;">SALIR</a></div><div class="card"><h3 style="text-align:center; letter-spacing:2px;">ESCAPE YOUR LIMITS</h3><form method="POST" action="/process"><textarea name="lista" rows="10" placeholder="CC|MM|YY|CVV"></textarea><button class="btn">INICIAR VALIDACIÓN</button></form></div></div></body></html>')

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
    lista = request.form.get('lista','').splitlines()
    res = "".join([f"<div class='live-row'><span style='color:#fff; font-weight:bold;'>✅ LIVE</span> <span>{cc}</span> <span>{get_bin(cc)}</span></div>" for cc in lista if len(cc)>10])
    return render_template_string(f'<html><head>{CSS}</head><body><div class="overlay"><div class="nav"><b>RESULTADOS</b><a href="/dashboard" style="color:white; text-decoration:none;">← VOLVER</a></div><div class="card">{res if res else "No hay resultados"}<br><a href="/dashboard" class="btn" style="display:block; text-align:center; text-decoration:none; margin-top:20px;">NUEVA CONSULTA</a></div></div></body></html>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
