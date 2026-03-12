from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'quickmoney_elite_black_2026'

# --- LINK DE LA IMAGEN (Subida a la nube para carga rápida) ---
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

# --- DISEÑO ELITE BLACK (Fusión de Imagen y Fondo Negro) ---
CSS = f"""
<style>
    :root {{ 
        --silver: #c0c0c0; 
        --black: #000000; 
        --dark-gray: #1a1a1a;
        --glow: rgba(255, 255, 255, 0.2);
    }}
    body {{ 
        background-color: var(--black); 
        /* Imagen de fondo suave y fusionada con negro */
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), url('{LOGO_LINK}');
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
        background-size: cover;
        color: var(--silver); 
        font-family: 'Montserrat', 'Segoe UI', sans-serif; 
        margin: 0; 
    }}
    .overlay {{ 
        min-height: 100vh; 
        width: 100%; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
    }}
    .nav {{ 
        background-color: rgba(10, 10, 10, 0.9); 
        padding: 15px 30px; 
        border-bottom: 2px solid var(--silver); 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        width: 100%; 
        position: absolute; 
        top: 0; 
        box-sizing: border-box; 
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }}
    .card {{ 
        background-color: rgba(20, 20, 20, 0.8); 
        border: 1px solid var(--dark-gray); 
        border-radius: 15px; 
        padding: 40px; 
        width: 90%; 
        max-width: 450px; 
        box-shadow: 0 0 30px rgba(0,0,0,0.7); 
        border-top: 3px solid var(--silver); 
        backdrop-filter: blur(5px); /* Efecto de cristal esmerilado */
    }}
    .btn {{ 
        background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%); 
        color: var(--black); 
        border: none; 
        padding: 15px; 
        border-radius: 8px; 
        font-weight: bold; 
        width: 100%; 
        cursor: pointer; 
        text-transform: uppercase; 
        letter-spacing: 2px;
        transition: 0.3s; 
        box-shadow: 0 5px 10px rgba(0,0,0,0.3);
    }}
    .btn:hover {{ 
        transform: translateY(-2px); 
        box-shadow: 0 8px 20px rgba(255,255,255,0.3); 
    }}
    input, textarea {{ 
        width: 100%; 
        background-color: rgba(0,0,0,0.6); 
        color: #ffffff; 
        border: 1px solid var(--dark-gray); 
        padding: 15px; 
        margin-bottom: 20px; 
        border-radius: 8px; 
        box-sizing: border-box; 
        font-size: 16px;
    }}
    input:focus, textarea:focus {{
        border-color: var(--silver);
        outline: none;
        box-shadow: 0 0 10px var(--glow);
    }}
    .live-row {{ 
        border-bottom: 1px solid var(--dark-gray); 
        padding: 15px; 
        font-family: 'Courier New', monospace; 
        display: flex; 
        justify-content: space-between; 
        align-items: center;
    }}
    .tag-live {{ 
        color: #ffffff; 
        font-weight: bold; 
        text-shadow: 0 0 8px #ffffff; 
        border: 1px solid #ffffff; 
        padding: 3px 10px; 
        border-radius: 4px; 
        font-size: 12px;
    }}
</style>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u == "mairo" and p == "1234":
            session['user'] = u
            return redirect(url_for('dashboard'))
        return render_template_string(f'<html><head>{CSS}</head><body><div class="overlay"><div class="card" style="text-align:center;"><h2>ACCESO DENEGADO</h2><p>Usuario o clave incorrecta.</p><a href="/" class="btn" style="text-decoration:none; display:block; text-align:center;">REINTENTAR</a></div></div></body></html>')
    
    return render_template_string(f"""
    <html>
        <head>
            <title>QUICK MONEY | ELITE ACCESS</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
            {CSS}
        </head>
        <body>
            <div class="overlay">
                <div class="card" style="text-align:center;">
                    <h1 style="letter-spacing:8px; text-shadow: 0 0 15px white; color:white; margin-bottom:40px;">QUICK MONEY</h1>
                    <form method="POST">
                        <input name="u" placeholder="USUARIO" required>
                        <input type="password" name="p" placeholder="PASSWORD" required>
                        <button type="submit" class="btn">ACCEDER AL TRONO</button>
                    </form>
                </div>
            </div>
        </body>
    </html>
    """)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    return render_template_string(f"""
    <html>
        <head>
            <title>QUICK MONEY | TERMINAL</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
            {CSS}
        </head>
        <body>
            <div class="overlay">
                <div class="nav">
                    <b style="font-size:1.2em; letter-spacing:2px; color:white;">🦁 QUICK MONEY ELITE</b> 
                    <div style="display:flex; align-items:center;">
                        <span style="margin-right:20px;">ID: {u} | Creds: {USUARIOS[u]["credits"]}</span>
                        <a href="/logout" style="color:#ff4d4d; text-decoration:none; font-weight:bold; border:1px solid #ff4d4d; padding:5px 15px; border-radius:5px;">SALIR</a>
                    </div>
                </div>
                <div class="card" style="max-width:800px; margin-top:100px;">
                    <h3 style="text-align:center; letter-spacing:3px; color:white; margin-bottom:30px;">ESCAPE YOUR LIMITS</h3>
                    <form method="POST" action="/process">
                        <textarea name="lista" rows="12" placeholder="FORMATO: CC|MM|YY|CVV"></textarea>
                        <button class="btn">INICIAR VALIDACIÓN</button>
                    </form>
                </div>
            </div>
        </body>
    </html>
    """)

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
    lista = request.form.get('lista','').splitlines()
    res = "".join([f"<div class='live-row'><span class='tag-live'>LIVE</span> <span>{cc}</span> <span>{get_bin(cc)}</span></div>" for cc in lista if len(cc)>10])
    return render_template_string(f"""
    <html>
        <head>
            <title>RESULTADOS</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
            {CSS}
        </head>
        <body>
            <div class="overlay">
                <div class="nav">
                    <b style="font-size:1.2em; letter-spacing:2px; color:white;">RESULTADOS</b>
                    <a href="/dashboard" style="color:white; text-decoration:none; border:1px solid white; padding:5px 15px; border-radius:5px;">← VOLVER</a>
                </div>
                <div class="card" style="max-width:800px; margin-top:100px;">
                    <div style="max-height:400px; overflow-y:auto; margin-bottom:20px;">
                        {res if res else '<p style="text-align:center;">No hay resultados válidos.</p>'}
                    </div>
                    <a href="/dashboard" class="btn" style="display:block; text-align:center; text-decoration:none;">NUEVA CONSULTA</a>
                </div>
            </div>
        </body>
    </html>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
