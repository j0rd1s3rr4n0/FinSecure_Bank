import os
import random
import sqlite3

DB_NAME = 'bank.db'
UPLOAD_DIR = 'docs'

schema = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    password TEXT NOT NULL,
    doc_path TEXT,
    balance REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_user TEXT,
    to_user TEXT NOT NULL,
    amount REAL NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"


def dni_letter(number: int) -> str:
    return LETTERS[number % 23]


def create_dummy_pdf() -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, 'dummy.pdf')
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(b'0')
    return path


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.executescript(schema)

    doc_path = create_dummy_pdf()

    samples = [
        ('12345678' + dni_letter(12345678), 'Juan Perez', 'juan123', doc_path, 1000.0),
        ('87654321' + dni_letter(87654321), 'Maria Lopez', 'maria123', doc_path, 1200.0),
        ('11223344' + dni_letter(11223344), 'Carlos Ruiz', 'carlos123', doc_path, 1500.0),
    ]
    c.executemany(
        'INSERT OR IGNORE INTO users (dni, full_name, password, doc_path, balance) '
        'VALUES (?, ?, ?, ?, ?)',
        samples
    )

    batch = []
    for i in range(250_000):
        num = 30000000 + i
        dni = f"{num}{dni_letter(num)}"
        full_name = f"User {i}"
        password = f"pass{i}"
        balance = random.random() * 1_000_000
        batch.append((dni, full_name, password, doc_path, balance))
        if len(batch) >= 10000:
            c.executemany(
                'INSERT INTO users (dni, full_name, password, doc_path, balance) '
                'VALUES (?, ?, ?, ?, ?)',
                batch
            )
            batch.clear()
    if batch:
        c.executemany(
            'INSERT INTO users (dni, full_name, password, doc_path, balance) '
            'VALUES (?, ?, ?, ?, ?)',
            batch
        )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print('Database initialized')

