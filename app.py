from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO, send
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_db, get_user_by_username, add_user, add_message, get_messages

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
socketio = SocketIO(app)

# Create the database if it doesn't exist yet
create_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    messages = get_messages()
    return render_template('index.html', messages=messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]  # Store user ID in session
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("Passwords do not match")
        elif get_user_by_username(username):
            flash("Username already taken")
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            add_user(username, hashed_password)
            flash("Registration successful, you can now log in.")
            return redirect(url_for('login'))
    return render_template('register.html')

@socketio.on('message')
def handle_message(msg):
    add_message(msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
