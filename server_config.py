from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'quickmoney_recovery_2026'

# --- CONFIGURACIÓN DE ACCESO ---
USUARIOS = {"mairo": {"pass": "1234", "credits": 10000}}

# --- DISEÑO PROFESIONAL SIN IMAGENES (PARA EVITAR ERRORES) ---
CSS = """
<style>
    body { 
        background-color: #0a0a0a; 
        color: #e0e0e0; 
        font-family: 'Segoe UI', Arial, sans-serif; 
        margin: 0; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        height: 100vh;
    }
    .card { 
        background: #151515; 
        border: 1px solid #333; 
        padding: 40px; 
        border-radius: 15px; 
        text-align: center; 
        box-shadow: 0 0 20px rgba(255,255,255,0.05);
        width: 320px;
    }
    h1 { letter-spacing: 5px; color: #fff; margin-bottom: 30px; }
    input { 
        width: 100%; 
        padding: 12px; 
        margin-bottom: 15px; 
        background: #000; 
        border: 1px solid #444; 
        color: #fff; 
        border-radius: 5px;
        box-sizing: border-box;
    }
    .btn { 
        width: 100%; 
        padding: 12px; 
        background: #fff; 
        color: #000; 
        border: none; 
        font-weight: bold; 
        cursor: pointer; 
        border-radius: 5px;
        text-transform: uppercase;
    }
</style>
"""

@app.route('/')
def login():
    if request.method == 'POST':
        u = request.form.get('u')
        p = request.form.get('p')
        if u in USUARIOS and USUARIOS[u]['pass'] == p:
            session['user'] = u
            return "LOGUEADO CORRECTAMENTE - EL DASHBOARD CARGARA AQUI"
    
    return render_template_string(f'''
    <html>
        <head><title>QUICK MONEY</title>{CSS}</head>
        <body>
            <div class="card">
                <h1>QUICK MONEY</h1>
                <form method="POST" action="/login_check">
                    <input type="text" name="u" placeholder="USUARIO" required>
                    <input type="password" name="p" placeholder="CONTRASEÑA" required>
                    <button type="submit" class="btn">ENTRAR</button>
                </form>
            </div>
        </body>
    </html>
    ''')

@app.route('/login_check', methods=['POST'])
def login_check():
    u = request.form.get('u')
    p = request.form.get('p')
    if u == "mairo" and p == "1234":
        return "<h1>✅ LOGIN EXITOSO. EL SERVIDOR ESTA VIVO.</h1><p>Mairo, si ves esto, el problema era la imagen. Avísame para arreglar el dashboard.</p>"
    return "Credenciales incorrectas. <a href='/'>Volver</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
