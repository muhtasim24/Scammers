from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, template_folder='templates')

#users = {}
client = MongoClient('mongodb://mongo:27017')
db = client['accounts']
users = db['users']

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users.find_one({'username': username})
        if user:
            return "Username already exists! Please try a different one."
        else:
            hashed_password = generate_password_hash(password)
            users.insert_one({'username': username, 'password': hashed_password})
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            return redirect(url_for('feed'))
        else:
            return "Invalid username/password. Please try again."

    return render_template('login.html')


@app.route('/feed')
def feed():
    return render_template('feed.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)