from flask import Flask, request, redirect, render_template, session, url_for, g
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = 'secret-key'  # Insecure for demo
DB_NAME = 'bank.db'

# ---- Database helpers ----

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db

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
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password, balance) VALUES (?, ?, 0)',
                       (username, password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username exists')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username=? AND password=?',
                          (username, password)).fetchone()
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
        'SELECT from_user, to_user, amount, created FROM transfers '
        'WHERE from_user=? OR to_user=? ORDER BY id DESC',
        (user['username'], user['username'])
    ).fetchall()
    return render_template('dashboard.html', user=user, transfers=transfers)

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

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
