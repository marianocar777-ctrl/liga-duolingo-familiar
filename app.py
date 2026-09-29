from flask import Flask, jsonify, request, send_from_directory, session
import sqlite3, os, secrets
from datetime import datetime
from zoneinfo import ZoneInfo
from functools import wraps

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
DB = os.path.join(os.path.dirname(__file__), 'liga.db')
PRIZES = [50000, 40000, 30000, 20000, 10000]
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'cambiar-esta-clave')

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    c = db()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS participants(id INTEGER PRIMARY KEY,name TEXT,username TEXT UNIQUE,points INTEGER DEFAULT 0,xp INTEGER DEFAULT 0,fine INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY,closed_at TEXT,name TEXT,username TEXT,xp INTEGER,fine INTEGER,effective INTEGER,position INTEGER,prize INTEGER);
    ''')
    c.commit(); c.close()

def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            return jsonify(ok=False, message='Acceso de administrador requerido.'), 401
        return fn(*args, **kwargs)
    return wrapped

@app.get('/')
def home(): return send_from_directory('static', 'index.html')

@app.get('/api/auth')
def auth_status(): return jsonify(admin=bool(session.get('admin')))

@app.post('/api/login')
def login():
    supplied = str((request.json or {}).get('password', ''))
    if secrets.compare_digest(supplied, ADMIN_PASSWORD):
        session['admin'] = True
        return jsonify(ok=True)
    return jsonify(ok=False, message='Contraseña incorrecta.'), 401

@app.post('/api/logout')
def logout():
    session.clear()
    return jsonify(ok=True)

@app.get('/api/ranking')
def ranking():
    c = db(); rows = [dict(x) for x in c.execute('SELECT * FROM participants')]; c.close()
    rows.sort(key=lambda r: max(0, r['xp'] - r['fine']), reverse=True)
    for i, r in enumerate(rows):
        r['effective'] = max(0, r['xp'] - r['fine']); r['position'] = i + 1; r['prize'] = PRIZES[i] if i < 5 else 0
    return jsonify(rows)

@app.post('/api/participant/<int:pid>')
@admin_required
def update(pid):
    d = request.json or {}
    try:
        xp = max(0, int(d.get('xp', 0))); fine = max(0, int(d.get('fine', 0)))
    except (TypeError, ValueError):
        return jsonify(ok=False, message='XP y multa deben ser números enteros.'), 400
    c = db(); c.execute('UPDATE participants SET xp=?, fine=? WHERE id=?', (xp, fine, pid)); c.commit(); c.close()
    return jsonify(ok=True)

@app.post('/api/close-week')
@admin_required
def close_week():
    now = datetime.now(ZoneInfo('America/Bogota'))
    c = db(); rows = [dict(x) for x in c.execute('SELECT * FROM participants')]
    rows.sort(key=lambda r: max(0, r['xp'] - r['fine']), reverse=True)
    for i, r in enumerate(rows):
        eff = max(0, r['xp'] - r['fine']); prize = PRIZES[i] if i < 5 else 0
        c.execute('INSERT INTO history(closed_at,name,username,xp,fine,effective,position,prize) VALUES(?,?,?,?,?,?,?,?)', (now.isoformat(), r['name'], r['username'], r['xp'], r['fine'], eff, i + 1, prize))
        c.execute('UPDATE participants SET points=points+?, xp=0, fine=0 WHERE id=?', (prize, r['id']))
    c.commit(); c.close()
    return jsonify(ok=True, closed_at=now.isoformat())

@app.get('/api/history')
def history():
    c = db(); x = [dict(r) for r in c.execute('SELECT * FROM history ORDER BY id DESC')]; c.close()
    return jsonify(x)

if __name__ == '__main__':
    init(); app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8000')))
