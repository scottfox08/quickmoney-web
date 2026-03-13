import os
import random
from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'quickmoney_ultra_gen_2026'

USUARIOS = {"mairo": "1234"}
LOGO_LINK = "https://images2.imgbox.com/7d/5d/q9Hn5lP4_o.png"

CSS = f"""
<style>
    :root {{ --accent: #00ffcc; --gold: #ffcc00; --red: #ff4d4d; --green: #2ecc71; }}
    body {{ background: #000 url('{LOGO_LINK}') no-repeat center fixed; background-size: cover; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; }}
    .overlay {{ background: rgba(0,0,0,0.85); min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding-top: 50px; }}
    
    .gen-card {{ 
        background: rgba(20, 25, 35, 0.95); border: 1px solid #334; border-radius: 15px; 
        padding: 25px; width: 90%; max-width: 500px; box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }}
    .gen-header {{ border-bottom: 1px solid #334; margin-bottom: 20px; padding-bottom: 10px; display: flex; align-items: center; gap: 10px; }}
    
    .grid-inputs {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }}
    
    label {{ display: block; font-size: 12px; color: var(--gold); margin-bottom: 5px; text-transform: uppercase; font-weight: bold; }}
    input, select, textarea {{ 
        width: 100%; background: #0a0a0c; border: 1px solid #334; color: #fff; 
        padding: 10px; border-radius: 5px; box-sizing: border-box; font-size: 14px;
    }}
    
    .btn-group {{ display: flex; gap: 10px; margin-top: 20px; }}
    .btn {{ flex: 1; border: none; padding: 12px; border-radius: 5px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 12px; transition: 0.3s; }}
    
    .btn-gen {{ background: var(--green); color: #fff; }}
    .btn-add {{ background: var(--gold); color: #000; }}
    .btn-clear {{ background: #555; color: #fff; }}
    .btn:hover {{ opacity: 0.8; transform: translateY(-2px); }}

    .results-area {{ margin-top: 20px; background: #000; border: 1px solid #334; color: var(--green); font-family: monospace; font-size: 13px; }}
</style>
"""

@app.route('/')
def login():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template_string(f'<html><head>{CSS}</head><body style="display:flex;justify-content:center;align-items:center;"><div class="gen-card" style="max-width:300px;text-align:center;"><h2>QUICK MONEY</h2><form method="POST" action="/login_check"><input name="u" placeholder="USUARIO"><input type="password" name="p" placeholder="PASS" style="margin-top:10px;"><button class="btn btn-gen" style="margin-top:20px;width:100%;">ENTRAR</button></form></div></body></html>')

@app.route('/login_check', methods=['POST'])
def login_check():
    if request.form.get('u') == "mairo" and request.form.get('p') == "1234":
        session['user'] = "mairo"
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    
    cards_generated = ""
    current_bin = ""
    
    if request.method == 'POST':
        bin_input = request.form.get('bin', '').replace(" ", "")[:6]
        mes = request.form.get('mes')
        anio = request.form.get('anio')
        cvv_input = request.form.get('cvv')
        cant = int(request.form.get('cant', 10))
        
        if len(bin_input) >= 6:
            res = []
            for _ in range(cant):
                cc = bin_input + "".join([str(random.randint(0,9)) for _ in range(10)])
                m = mes if mes != "RANDOM" else f"{random.randint(1,12):02d}"
                a = anio if anio != "RANDOM" else str(random.randint(25,30))
                c = cvv_input if cvv_input and cvv_input != "RANDOM" else str(random.randint(100,999))
                res.append(f"{cc}|{m}|{a}|{c}")
            cards_generated = "\\n".join(res)
            current_bin = bin_input

    return render_template_string(f"""
    <html><head><title>GENERADOR PRO</title>{CSS}</head>
    <body><div class="overlay">
        <div class="gen-card">
            <div class="gen-header">
                <span>🪄</span> <b>GENERADOR AUTOMÁTICO DE TARJETAS</b>
            </div>
            
            <form method="POST">
                <label>BINS</label>
                <input name="bin" placeholder="456789xxxxxxxxx" value="{current_bin}" required>
                
                <div class="grid-inputs">
                    <div>
                        <label>MES</label>
                        <select name="mes">
                            <option>RANDOM</option>
                            {" ".join([f'<option value="{i:02d}">{i:02d}</option>' for i in range(1,13)])}
                        </select>
                    </div>
                    <div>
                        <label>AÑO</label>
                        <select name="anio">
                            <option>RANDOM</option>
                            {" ".join([f'<option value="{i}">{i}</option>' for i in range(25,31)])}
                        </select>
                    </div>
                </div>
                
                <div class="grid-inputs">
                    <div>
                        <label>CVV</label>
                        <input name="cvv" placeholder="RANDOM">
                    </div>
                    <div>
                        <label>CANTIDAD</label>
                        <input name="cant" type="number" value="10">
                    </div>
                </div>
                
                <div class="btn-group">
                    <button type="submit" class="btn btn-gen">🪄 GENERAR</button>
                    <button type="button" class="btn btn-add" onclick="document.getElementById('res').select();document.execCommand('copy');alert('Copiado!')">➕ COPIAR</button>
                    <button type="button" class="btn btn-clear" onclick="window.location.href='/dashboard'">🗑️ LIMPIAR</button>
                </div>
            </form>
            
            <textarea id="res" class="results-area" rows="8" readonly>{cards_generated}</textarea>
            <p style="font-size:10px;text-align:center;color:#555;margin-top:10px;">MAIRO ADMIN | SALDO: ∞ | <a href="/logout" style="color:var(--red)">SALIR</a></p>
        </div>
    </div></body></html>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
