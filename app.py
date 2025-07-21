from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import sqlite3
import numpy as np
import webbrowser
from threading import Timer

app = Flask(__name__)
app.secret_key = 'your_secret_key'

model = joblib.load('model.joblib')

def validate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    conn.commit()
    conn.close()

create_user_table()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if validate_user(username, password):
        session['user'] = username
        return redirect(url_for('predict'))
    else:
        return render_template('login.html', error="Invalid credentials")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        try:
            pregnancies = float(request.form['pregnancies'])
            glucose = float(request.form['glucose'])
            bp = float(request.form['bp'])
            skin = float(request.form['skin'])
            insulin = float(request.form['insulin'])
            bmi = float(request.form['bmi'])
            dpf = float(request.form['dpf'])
            age = float(request.form['age'])

            data = [[pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]]
            result = model.predict(data)[0]
            output = "Diabetic" if result == 1 else "Not Diabetic"
            return render_template('result.html', result=output)
        except Exception as e:
            return f"Error: {e}"

    return render_template('predict.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = 5000
    url = f"http://127.0.0.1:{port}"
    
    def open_browser():
        webbrowser.open_new(url)

    Timer(1, open_browser).start()
    app.run(port=port, debug=True)

def create_user_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def create_prediction_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            username TEXT,
            pregnancies REAL,
            glucose REAL,
            bp REAL,
            skin REAL,
            insulin REAL,
            bmi REAL,
            dpf REAL,
            age REAL,
            result TEXT
        )
    ''')
    conn.commit()
    conn.close()


create_user_table()
create_prediction_table()
