from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = 'bank.db'

# Helper to get db connection

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/users')
def list_users():
    """Return list of all usernames."""
    conn = get_db()
    c = conn.execute('SELECT username FROM users')
    data = [r['username'] for r in c.fetchall()]
    conn.close()
    return jsonify({'users': data})


@app.route('/founds')
def get_founds():
    """Return balances for all users."""
    conn = get_db()
    c = conn.execute('SELECT username, balance FROM users')
    data = [{'username': r['username'], 'balance': r['balance']} for r in c.fetchall()]
    conn.close()
    return jsonify(data)


def _record_transfer(c, from_user, to_user, amount):
    c.execute('INSERT INTO transfers (from_user, to_user, amount) VALUES (?,?,?)',
              (from_user, to_user, amount))


@app.route('/transfer')
def transfer():
    from_user = request.args.get('from')
    to_user = request.args.get('to')
    amount = request.args.get('amount')
    missing = []
    if not from_user:
        missing.append('from')
    if not to_user:
        missing.append('to')
    if not amount:
        missing.append('amount')
    if missing:
        return jsonify({'error': 'missing fields', 'fields': missing}), 400
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'invalid amount'}), 400
    if amount <= 0:
        return jsonify({'error': 'amount must be positive'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT balance FROM users WHERE username=?', (from_user,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'from_user not found'}), 404
    if row['balance'] < amount:
        conn.close()
        return jsonify({'error': 'insufficient funds'}), 400

    c.execute('UPDATE users SET balance=balance-? WHERE username=?',
              (amount, from_user))
    c.execute('UPDATE users SET balance=balance+? WHERE username=?',
              (amount, to_user))
    _record_transfer(c, from_user, to_user, amount)
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'from_user': from_user, 'to_user': to_user, 'amount': amount})


@app.route('/transfer_all')
def transfer_all():
    to_user = request.args.get('to_user')
    if not to_user:
        return jsonify({'error': 'to_user required'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT username, balance FROM users')
    users = c.fetchall()
    total = 0
    for u in users:
        if u['username'] == to_user or u['balance'] <= 0:
            continue
        amount = u['balance']
        total += amount
        c.execute('UPDATE users SET balance=0 WHERE username=?', (u['username'],))
        _record_transfer(c, u['username'], to_user, amount)
    c.execute('UPDATE users SET balance=balance+? WHERE username=?', (total, to_user))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'transferred': total, 'to_user': to_user})

if __name__ == '__main__':
    app.run('127.0.0.1', 5001)
