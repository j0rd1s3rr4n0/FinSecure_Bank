import sqlite3
import os

DB_NAME = 'bank.db'

schema = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    balance REAL DEFAULT 0
);
'''

users = [
    ('juan', 'juan123', 1000.0),
    ('maria', 'maria123', 1200.0),
    ('carlos', 'carlos123', 1500.0)
]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.executescript(schema)
    for u in users:
        try:
            c.execute('INSERT INTO users (username, password, balance) VALUES (?, ?, ?)', u)
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Database initialized')
