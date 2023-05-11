from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__, template_folder='templates')

users = {}

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users:
            return "Username already exists! Please try a different one."
        else:
            users[username] = password
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            return redirect(url_for('feed'))
        else:
            return "Invalid username/password. Please try again."

    return render_template('login.html')

@app.route('/feed')
def feed():
    return render_template('feed.html')

if __name__ == "__main__":
    app.run(port=5001, debug=True)