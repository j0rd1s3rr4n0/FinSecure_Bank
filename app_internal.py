from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = 'bank.db'

# Helper to get db connection

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/internal/transfer_all')
def transfer_all():
    to_user = request.args.get('to_user')
    if not to_user:
        return jsonify({'error': 'to_user required'}), 400
    conn = get_db()
    c = conn.cursor()
    # Calculate total balance
    c.execute('SELECT SUM(balance) FROM users')
    total = c.fetchone()[0] or 0
    # Reset all balances to 0
    c.execute('UPDATE users SET balance=0')
    # Add total to target user
    c.execute('UPDATE users SET balance=? WHERE username=?', (total, to_user))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'transferred': total, 'to_user': to_user})

if __name__ == '__main__':
    app.run('127.0.0.1', 5001)
