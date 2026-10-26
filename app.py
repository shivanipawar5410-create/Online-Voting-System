from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

conn = sqlite3.connect('voting.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS votes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
candidate TEXT
)
''')

conn.commit()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/save_user', methods=['POST'])
def save_user():

    username = request.form['username']
    password = request.form['password']

    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,password)
        )
        conn.commit()

    except:
        return "Username already exists"

    return redirect('/')

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
    )

    user = cursor.fetchone()

    if user:
        session['username'] = username
        return render_template('voting.html')

    return "Invalid Username or Password"

@app.route('/vote', methods=['POST'])
def vote():

    username = session.get('username')
    candidate = request.form['candidate']

    cursor.execute(
        "SELECT * FROM votes WHERE username=?",
        (username,)
    )

    already = cursor.fetchone()

    if already:
        return "You have already voted"

    cursor.execute(
        "INSERT INTO votes(username,candidate) VALUES(?,?)",
        (username,candidate)
    )

    conn.commit()

    return render_template('success.html')

@app.route('/result')
def result():

    cursor.execute(
        "SELECT candidate, COUNT(*) FROM votes GROUP BY candidate"
    )

    results = cursor.fetchall()

    return render_template('result.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)