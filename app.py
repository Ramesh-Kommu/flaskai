import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session and flashing messages

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('nanidb.db')
    conn.row_factory = sqlite3.Row  # Allows access to columns by name
    return conn

# Function to call Gemini AI API
def get_gemini_response(query):
    api_key = "AIzaSyAHO-FX0qySIZI3FeMc2pzdq04NEmIRu98"  # Replace with your Gemini API key
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    data = {
        "contents": [
            {"parts": [{"text": query}]}
        ]
    }
    
    response = requests.post(url + f"?key={api_key}", json=data)
    if response.status_code == 200:
        result = response.json()['candidates'][0]['content']['parts'][0]['text']
        return result
    else:
        return "Sorry, I couldn't generate a response. Please try again later."

# Home Route (Landing Page)
@app.route('/')
def home():
    return render_template('home.html')

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        userrole = 'user'  # Default role for new users
        usercreatedDate = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM userdata WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('signup'))

        cursor.execute("INSERT INTO userdata (firstname, lastname, username, password, usercreatedDate, userrole) VALUES (?, ?, ?, ?, ?, ?)",
                       (firstname, lastname, username, password, usercreatedDate, userrole))  # Insert new user
        conn.commit()
        conn.close()

        flash('Sign up successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = user['username']
            session['role'] = user['userrole']
            flash('Login successful!', 'success')
            return redirect(url_for('primary'))  # Redirect to primary page after login
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Primary Tab (Query Input) Route
@app.route('/primary', methods=['GET', 'POST'])
def primary():
    if 'username' not in session:
        flash('Please log in to access the page.', 'warning')
        return redirect(url_for('login'))

    response_text = ""
    if request.method == 'POST':
        user_query = request.form['query']
        queried_time = datetime.now()

        # Call Gemini AI
        response_text = get_gemini_response(user_query)

        # Store the query and AI response in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO userQuery (username, userQuery, queriedtime, aiResponse) VALUES (?, ?, ?, ?)",
                       (session['username'], user_query, queried_time, response_text))  # Insert query and AI response
        conn.commit()
        conn.close()

        flash('Your query has been submitted!', 'success')
    
    # Fetch query history for the user
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if session['role'] == 'admin':
        cursor.execute("SELECT * FROM userQuery")  # Admin sees all queries
    else:
        cursor.execute("SELECT * FROM userQuery WHERE username = ?", (session['username'],))  # Regular user sees only their queries
    
    queries = cursor.fetchall()
    conn.close()

    return render_template('home.html', response_text=response_text, queries=queries)

# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear the session to log out
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, host='0.0.0.0', port=port)
