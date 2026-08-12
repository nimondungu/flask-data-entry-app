import sqlite3
from flask import Flask, render_template_string, request, redirect, flash, get_flashed_messages

app = Flask(__name__)
# Secret key is required to use Flask's flash messaging system
app.secret_key = 'super_secret_key_for_flash_messages'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees ORDER BY id ASC')
    records = cursor.fetchall()
    conn.close()

    return render_template_string(html_content, records=records)

@app.route('/add', methods=['POST'])
def add_record():
    name = request.form['name'].strip()
    email = request.form['email'].strip().lower()
    department = request.form['department']

    # 1. Format check
    if "@" not in email or "." not in email:
        flash('Invalid email address format!')
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. Duplicate check
    cursor.execute('SELECT id FROM employees WHERE email = ?', (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        # Flash the message to session memory (URL stays clean)
        flash(f'The email "{email}" is already registered!')
        return redirect('/')

    # 3. Save record if unique
    try:
        cursor.execute(
            'INSERT INTO employees (name, email, department) VALUES (?, ?, ?)',
            (name, email, department)
        )
        conn.commit()
    finally:
        conn.close()

    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)