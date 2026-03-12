from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests
import time

app = Flask(__name__)
app.secret_key = 'quickmoney_2026'

USUARIOS = {"mairo": {"pass": "1234", "credits": 10000, "role": "admin"}}

@app.route('/api/add_user', methods=['POST'])
def api_add_user():
    if request.headers.get('X-Bot-Key') != "QUICK_SECRET_99": return jsonify({"status": "error"}), 403
    data = request.json
    u, p, c = data.get('username'), data.get('password'), data.get('credits', 50)
    if u and p:
        USUARIOS[u] = {"pass": p, "credits": int(c), "role": "user"}
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

def get_bin_info(cc):
    try:
        r = requests.get(f"https://lookup.binlist.net/{cc[:6]}", timeout=3)
        if r.status_code == 200:
            d = r.json()
            return f"{d.get('country',{}).get('emoji','🌐')} {d.get('bank',{}).get('name','BCO')}"
    except: pass
    return "🌐 Info no disponible"

ESTILOS = '<style>:root{--n:#00ff88;--b:#0a0a0a}body{background:var(--b);color:white;font-family:sans-serif;margin:0}.nav{background:#151515;padding:15px;display:flex;justify-content:space-between}.card{background:#151515;border:1px solid #222;border-radius:12px;padding:25px;margin:20px}.btn{background:var(--n);color:black;border:none;padding:12px;border-radius:6px;font-weight:bold;width:100%;cursor:pointer}textarea{width:100%;background:#000;color:var(--n);border:1px solid #333;padding:15px;box-sizing:border-box}</style>'

@app.route('/')
def index(): return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if u in USUARIOS and USUARIOS[u]['pass'] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
    return render_template_string(f'{ESTILOS}<div style="height:100vh;display:flex;align-items:center;justify-content:center;"><div class="card" style="width:300px;text-align:center;"><h2>QUICK MONEY</h2><form method="POST"><input name="u" placeholder="User" style="width:100%;margin-bottom:10px;padding:10px;"><input type="password" name="p" placeholder="Pass" style="width:100%;margin-bottom:20px;padding:10px;"><button class="btn">ENTRAR</button></form></div></div>')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    return render_template_string(f'{ESTILOS}<div class="nav"><b>💸 QUICK MONEY</b> <span>ID: {u} | Creds: {USUARIOS[u]["credits"]} <a href="/logout" style="color:red">X</a></span></div><div class="card">{"<a href=\'/admin\' style=\'color:var(--n)\'>⚡ ADMIN</a>" if USUARIOS[u]["role"]=="admin" else ""}<h3>Scanner</h3><form method="POST" action="/process"><textarea name="lista" rows="10"></textarea><button class="btn" style="margin-top:20px">VALIDAR</button></form></div>')

@app.route('/admin')
def admin():
    if 'user' not in session or USUARIOS[session['user']]['role'] != 'admin': return "No"
    return render_template_string(f'{ESTILOS}<div class="card"><h2>Users</h2>{"".join([f"<p>{u} - {d['credits']}</p>" for u,d in USUARIOS.items()])}<br><a href="/dashboard" style="color:var(--n)">Volver</a></div>')

@app.route('/process', methods=['POST'])
def process():
    if 'user' not in session: return redirect(url_for('login'))
    u = session['user']
    lista = request.form.get('lista','').splitlines()
    if USUARIOS[u]['credits'] < len(lista): return "Saldo bajo"
    USUARIOS[u]['credits'] -= len(lista)
    res = [f"<div style='border-bottom:1px solid #222;padding:10px;'>✅ LIVE: {cc} | {get_bin_info(cc)}</div>" for cc in lista if len(cc)>10]
    return render_template_string(f'{ESTILOS}<div class="card"><h3>Resultados</h3>{"".join(res)}<br><a href="/dashboard" class="btn" style="display:block;text-align:center;text-decoration:none">NUEVO</a></div>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
