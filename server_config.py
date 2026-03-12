from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'quickmoney_2026'

# --- CONFIGURACIÓN ---
PX = {"http": "http://sp6jzqtaou:rUd7t65FxkK+x3F1hr@gate.decodo.com:10001", "https": "http://sp6jzqtaou:rUd7t65FxkK+x3F1hr@gate.decodo.com:10001"}
USUARIOS = {"mairo": {"pass": "1234", "credits": 10000, "role": "admin"}}

def get_bin(cc):
    try:
        # Usamos una base de datos más completa y rápida
        bin_6 = cc[:6]
        r = requests.get(f"https://bin-ip-checker.p.rapidapi.com/?bin={bin_6}", 
            headers={"X-RapidAPI-Key": "TU_KEY_OPCIONAL"}, timeout=5)
        
        # Como no tenemos Key de pago aún, usaremos este respaldo que es MUY bueno:
        r = requests.get(f"https://lookup.binlist.net/{bin_6}", timeout=5)
        
        if r.status_code == 200:
            d = r.json()
            banco = d.get('bank', {}).get('name', 'DESCONOCIDO')
            pais = d.get('country', {}).get('name', 'S/N')
            emoji = d.get('country', {}).get('emoji', '🌐')
            tipo = d.get('type', '').upper() # DEBIT o CREDIT
            
            return f"{emoji} {pais} | {banco} | {tipo}"
    except:
        pass
    return "🌐 Info no disponible"

@app.route('/api/add_user', methods=['POST'])
def api_add_user():
    if request.headers.get('X-Bot-Key') != "QUICK_SECRET_99": return jsonify({"status":"err"}), 403
    data = request.json
    u, p, c = data.get('username'), data.get('password'), data.get('credits', 50)
    if u and p:
        USUARIOS[u] = {"pass": p, "credits": int(c), "role": "user"}
        return jsonify({"status":"ok"})
    return jsonify({"status":"err"}), 400

@app.route('/')
def index(): return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u in USUARIOS and USUARIOS[u]['pass'] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string('<body style="background:#0a0a0a;color:white;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;"><div style="background:#151515;padding:30px;border-radius:10px;border:1px solid #00ff88;text-align:center;"><h2>QUICK MONEY</h2><form method="POST"><input name="u" placeholder="User" style="width:100%;margin-bottom:10px;padding:10px;"><input type="password" name="p" placeholder="Pass" style="width:100%;margin-bottom:20px;padding:10px;"><button style="width:100%;padding:10px;background:#00ff88;border:none;font-weight:bold;cursor:pointer;">ENTRAR</button></form></div></body>')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    creds = USUARIOS[u]['credits']
    btn = f'<a href="/admin" style="color:#00ff88;display:block;margin-bottom:20px;">⚡ ADMIN PANEL</a>' if USUARIOS[u]['role'] == 'admin' else ''
    return render_template_string(f'<body style="background:#0a0a0a;color:white;font-family:sans-serif;padding:20px;"><div style="max-width:600px;margin:auto;background:#151515;padding:20px;border-radius:10px;"><h3>💸 Terminal | {u} | Creds: {creds}</h3>{btn}<form method="POST" action="/process"><textarea name="lista" rows="10" style="width:100%;background:#000;color:#00ff88;padding:10px;" placeholder="CC|MM|YY|CVV"></textarea><button style="width:100%;padding:15px;background:#00ff88;margin-top:10px;font-weight:bold;cursor:pointer;">CHECKER START</button></form></div></body>')

@app.route('/admin')
def admin():
    if 'user' not in session or USUARIOS[session['user']]['role'] != 'admin': return "No"
    usrs = "".join([f"<li>{u}: {d['credits']}</li>" for u,d in USUARIOS.items()])
    return render_template_string(f'<body style="background:#0a0a0a;color:white;padding:20px;"><h2>Usuarios</h2><ul>{usrs}</ul><a href="/dashboard" style="color:#00ff88;">Volver</a></body>')

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    lista = request.form.get('lista','').splitlines()
    if USUARIOS[u]['credits'] < len(lista): return "Sin creditos"
    USUARIOS[u]['credits'] -= len(lista)
    res = "".join([f"<p style='border-bottom:1px solid #333;padding:5px;'>✅ {cc} | {get_bin(cc)}</p>" for cc in lista if len(cc)>10])
    return render_template_string(f'<body style="background:#0a0a0a;color:white;padding:20px;"><div style="background:#151515;padding:20px;border-radius:10px;"><h3>Resultados</h3>{res}<br><a href="/dashboard" style="color:#00ff88;">NUEVO CHECK</a></div></body>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)


