from flask import Flask, request, render_template, redirect, url_for, session
from datetime import datetime, timedelta
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, template_folder='templates')
app.secret_key = '354545452'

users = {}
auction_items = {
}

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
            session['username'] = username  # Store the username in the session
            return redirect(url_for('feed'))
        else:
            return "Invalid credentials, please try again!"

    return render_template('login.html')

@app.route('/account')
def account():
    # Get the username of the logged-in user from the session or wherever it is stored
    username = session.get('username')
    
    # Fetch the user's account information from the database
    user = users.find_one({'username': username})
    
    if user:
        # Get the current auctions and total auctions won for the user (example data)
        current_auctions = ['Auction 1', 'Auction 2', 'Auction 3']
        total_auctions_won = 5
    
        return render_template('account.html', username=user['username'], current_auctions=current_auctions, total_auctions_won=total_auctions_won)
    else:
        return "User not found."  # Or redirect to an error page


@app.route('/feed')
def feed():
    return render_template('feed.html', auction_items=auction_items)

#@app.route('/bid')
@app.route('/bid', methods=['GET', 'POST'])
def bid():
    item_name = request.args.get('item_name') if request.method == 'GET' else request.form.get('item_name')
    
    if request.method == 'POST':
        bid_amount = float(request.form.get('bid_amount'))
        username = request.form.get('username')  # We assume that the username is given in the form

        if datetime.now() > auction_items[item_name]['end_time']:
            return "Bidding Period Ended!"

        if item_name in auction_items and bid_amount > auction_items[item_name]['current_bid']:
            auction_items[item_name]['current_bid'] = bid_amount
            auction_items[item_name]['current_bidder'] = username
            return redirect(url_for('feed'))
        else:
            return "Invalid bid. Please try again."
    
    return render_template('bid.html', item_name=item_name, item_info=auction_items[item_name])

@app.route('/post_item', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        starting_price = float(request.form.get('starting_price'))
        end_time = datetime.now() + timedelta(days=float(request.form.get('days_to_bid')))

        if item_name in auction_items:
            return "An item with this name already exists. Please choose a different name."

        auction_items[item_name] = {
            "description": description, 
            "current_bid": starting_price, 
            "current_bidder": None,
            "end_time": end_time
        }

        return redirect(url_for('feed'))

    return render_template('post_item.html')





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)