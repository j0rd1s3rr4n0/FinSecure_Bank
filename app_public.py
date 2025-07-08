from flask import Flask, request, redirect, render_template, session, url_for, g
import sqlite3
import os
import random
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret-key'  # Insecure for demo
DB_NAME = 'bank.db'
UPLOAD_FOLDER = 'docs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.template_filter('money')
def money(value):
    """Format numbers using '.' for thousands and ',' for decimals."""
    try:
        return '{:,.2f}'.format(float(value)).replace(',', 'X').replace('.', ',').replace('X', '.')
    except (TypeError, ValueError):
        return value

# ---- Database helpers ----

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db

def valid_dni(dni: str) -> bool:
    """Check Spanish DNI control letter."""
    letters = "TRWAGMYFPDXBNJZSQVHLCKE"
    if len(dni) != 9 or not dni[:-1].isdigit() or not dni[-1].isalpha():
        return False
    num = int(dni[:-1])
    return dni[-1].upper() == letters[num % 23]


def generate_iban() -> str:
    digits = ''.join(str(random.randint(0, 9)) for _ in range(22))
    return 'ES' + digits

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ---- Authentication ----

def current_user():
    if 'user_id' not in session:
        return None
    db = get_db()
    c = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],))
    return c.fetchone()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        dni = request.form['dni'].upper()
        fullname = request.form['fullname']
        password = request.form['password']
        doc = request.files.get('document')
        if not valid_dni(dni):
            return render_template('register.html', error='DNI inválido')
        if not doc or not doc.filename.lower().endswith('.pdf'):
            return render_template('register.html', error='Debes subir un PDF')
        data = doc.read()
        if len(data) == 0:
            return render_template('register.html', error='El PDF no puede estar vacío')
        filename = secure_filename(dni + '_' + doc.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(data)
        db = get_db()
        iban = generate_iban()
        try:
            db.execute(
                'INSERT INTO users (dni, iban, full_name, password, doc_path, balance) '
                'VALUES (?, ?, ?, ?, ?, 100)',
                (dni, iban, fullname, password, filepath))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='DNI ya registrado')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dni = request.form['dni'].upper()
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE dni=? AND password=?',
                          (dni, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    db = get_db()
    transfers = db.execute(
        'SELECT from_iban, to_iban, amount, created FROM transfers '
        'WHERE from_iban=? OR to_iban=? ORDER BY id DESC LIMIT 300',
        (user['iban'], user['iban'])
    ).fetchall()
    error = request.args.get('error')
    msg = request.args.get('msg')
    return render_template('dashboard.html', user=user, transfers=transfers,
                           error=error, msg=msg)


@app.route('/transfer', methods=['POST'])
def make_transfer():
    """Allow logged-in users to transfer money using IBAN."""
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    to_iban = request.form.get('to_iban')
    amount = request.form.get('amount')
    if not to_iban or not amount:
        return redirect(url_for('dashboard', error='Faltan campos'))
    try:
        float(amount)
    except ValueError:
        return redirect(url_for('dashboard', error='Importe inválido'))
    internal_url = 'http://127.0.0.1:443/transfer'
    try:
        resp = requests.get(
            internal_url,
            params={'from': user['iban'], 'to': to_iban, 'amount': amount},
            timeout=5,
        )
        if resp.status_code != 200:
            return redirect(url_for('dashboard', error='Error en la transferencia'))
    except Exception:
        return redirect(url_for('dashboard', error='Error en la transferencia'))

    msg = f'<script>console.log(\'Transferencia realizada mediante {internal_url}\')</script>Transferencia realizada'
    return redirect(url_for('dashboard', msg=msg))

@app.route('/verify_external', methods=['GET', 'POST'])
def verify_external():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    content = None
    url = None
    if request.method == 'POST':
        url = request.form['url']
        # SSRF vulnerability: no validation of the URL
        resp = requests.get(url)  # An attacker can reach internal services
        content = resp.text
    return render_template('verify_external.html', user=user, content=content, url=url)


@app.route('/withdraw', methods=['POST'])
def withdraw():
    """Allow privileged withdrawal to display flag and reset balances."""
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    if user['balance'] < 10_000_000:
        return redirect(url_for('dashboard', error='Saldo insuficiente'))

    db = get_db()
    # Redistribute money randomly among all users except the current one
    db.execute(
        'UPDATE users SET balance=(abs(random()) % 100000000)/100.0 WHERE id != ?',
        (user['id'],)
    )
    db.execute('UPDATE users SET balance=0 WHERE id=?', (user['id'],))
    db.commit()

    flag = 'flag{hasVulneradoElBancoConSSRF}'
    return render_template('withdraw.html', flag=flag)

if __name__ == '__main__':
    app.run('0.0.0.0', 80,debug=False)