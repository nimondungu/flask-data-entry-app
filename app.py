import sqlite3
from flask import Flask, render_template_string, request, redirect, flash, get_flashed_messages

app = Flask(__name__)
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

def print_backend_records():
    """Helper function to print database contents to the backend terminal."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees ORDER BY id ASC')
    records = cursor.fetchall()
    conn.close()

    print("\n" + "="*50)
    print("      BACKEND DATABASE RECORDS (LIVE VIEW)")
    print("="*50)
    for row in records:
        print(f"ID: {row[0]} | Name: {row[1]} | Email: {row[2]} | Role: {row[3]}")
    print("="*50 + "\n")

@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Print database contents to VS Code terminal
    print_backend_records()

    return render_template_string(html_content)

@app.route('/add', methods=['POST'])
def add_record():
    name = request.form['name'].strip()
    email = request.form['email'].strip().lower()
    department = request.form['department']

    if "@" not in email or "." not in email:
        flash('Invalid email address format!')
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM employees WHERE email = ?', (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        flash(f'The email {email} is already registered!')
        return redirect('/')

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