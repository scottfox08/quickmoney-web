from flask import Flask, render_template_string, request, redirect, url_for, session
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'quickmoney_ultra_safe_2026' # Cambia esto por algo aleatorio

# --- CONFIGURACIÓN DE ACCESO ---
USUARIO_ADMIN = "mairo"
CLAVE_ADMIN = "1234"
NOMBRE_WEB = "💸 Quick Money 💸"
# Crear carpeta de resultados si no existe
if not os.path.exists('resultados'):
    os.makedirs('resultados')

def luhn_check(card_number):
    card_number = card_number.replace(" ", "").strip()
    total_sum = 0
    is_second = False
    for i in range(len(card_number) - 1, -1, -1):
        try:
            d = int(card_number[i])
            if is_second:
                d = d * 2
                if d > 9: d -= 9
            total_sum += d
            is_second = not is_second
        except: continue
    return (total_sum % 10) == 0 and len(card_number) >= 15

# --- DISEÑO UI PREMIUM ---
ESTILOS = '''
<style>
    body { background: #0a0a0a; color: #e0e0e0; font-family: 'Inter', sans-serif; margin: 0; padding: 0; }
    .nav { background: #111; padding: 15px; border-bottom: 2px solid #00ff88; display: flex; justify-content: space-between; align-items: center; }
    .container { max-width: 900px; margin: 40px auto; padding: 25px; background: #161616; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    h1 { color: #00ff88; letter-spacing: 2px; }
    textarea { width: 100%; height: 200px; background: #000; color: #00ff88; border: 1px solid #333; padding: 15px; border-radius: 8px; font-family: 'Courier New', monospace; box-sizing: border-box; }
    .btn { background: #00ff88; color: #000; border: none; padding: 12px 30px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 15px; }
    .btn:hover { background: #00cc6e; transform: translateY(-2px); }
    .result-card { background: #000; padding: 15px; border-radius: 8px; border-left: 4px solid #00ff88; margin-top: 20px; text-align: left; font-family: monospace; }
    .live { color: #00ff88; }
    .dead { color: #ff4b4b; }
</style>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == USUARIO_ADMIN and request.form['p'] == CLAVE_ADMIN:
            session['auth'] = True
            return redirect(url_for('panel'))
    return render_template_string(f'''
    {ESTILOS}
    <div style="height:100vh; display:flex; align-items:center; justify-content:center;">
        <div class="container" style="width:400px; text-align:center;">
           <p style="color:#00ff88; font-size:1.2rem; margin-bottom:5px;">(Bienvenido)</p>
<h1>{NOMBRE_WEB}</h1>
            <h1>{NOMBRE_WEB}</h1>
            <form method="POST">
                <input type="text" name="u" placeholder="Usuario" style="width:100%; padding:10px; margin:10px 0; background:#222; border:1px solid #444; color:white; border-radius:5px;"><br>
                <input type="password" name="p" placeholder="Password" style="width:100%; padding:10px; margin:10px 0; background:#222; border:1px solid #444; color:white; border-radius:5px;"><br>
                <button type="submit" class="btn">ENTRAR AL SISTEMA</button>
            </form>
        </div>
    </div>
    ''')

@app.route('/panel')
def panel():
    if not session.get('auth'): return redirect(url_for('login'))
    return render_template_string(f'''
    {ESTILOS}
    <div class="nav">
        <span style="font-weight:bold; color:#00ff88;">{NOMBRE_WEB} // TERMINAL</span>
        <a href="/logout" style="color:#ff4b4b; text-decoration:none;">Cerrar Sesión</a>
    </div>
    <div class="container">
        <h2>Scanner de Algoritmos</h2>
        <form method="POST" action="/check">
            <textarea name="data" placeholder="Pega tu lista aquí..."></textarea>
            <button type="submit" class="btn">INICIAR VALIDACIÓN</button>
        </form>
    </div>
    ''')

@app.route('/check', methods=['POST'])
def check():
    if not session.get('auth'): return redirect(url_for('login'))
    raw_data = request.form.get('data').splitlines()
    lives = []
    results_html = []
    
    for line in raw_data:
        if not line.strip(): continue
        cc = line.split('|')[0].strip()
        if luhn_check(cc):
            lives.append(line)
            results_html.append(f'<div class="live">✅ [VALIDA] {line}</div>')
        else:
            results_html.append(f'<div class="dead">❌ [INVALIDA] {line}</div>')
    
    # Guardar LOG en el servidor
    if lives:
        filename = f"resultados/lives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write("\n".join(lives))

    return render_template_string(f'''
    {ESTILOS}
    <div class="container">
        <h1>Resultados del Proceso</h1>
        <div class="result-card">
            {''.join(results_html)}
        </div>
        <p style="margin-top:20px;">Se han detectado {len(lives)} registros válidos.</p>
        <button class="btn" onclick="window.history.back()">VOLVER</button>
    </div>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=80)
