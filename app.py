from flask import Flask, request, render_template, redirect, url_for, session
from datetime import datetime, timedelta
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sock import Sock
import json
from datetime import datetime, timedelta


app = Flask(__name__, template_folder='templates')
sock = Sock(app)
connected_clients = set()  # Store connected clients

app.secret_key = '354545452'

users = {}
auction_items = {
}

#users = {}
client = MongoClient('mongodb://mongo:27017')
db = client['accounts']
users = db['users']
auction_items=db['auction_items']

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
def broadcast_to_clients(message):
    for client in connected_clients:
        client.send(message)

@sock.route('/ws')
def websocket_connection(sock):
    connected_clients.add(sock)  # Add the new connected client

 
    while not sock.closed:
        data = sock.receive()
        # Process received data if needed
        # Handle individual client messages

        # After processing the data, if you want to broadcast a message to all connected clients, call the `broadcast_to_clients` function
        message = "Your message to broadcast"
        broadcast_to_clients(message)

    connected_clients.remove(sock)  # Remove disconnected client


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

@sock.route('/echo')
def echo(sock):
    while True:
        data = sock.receive()
        sock.send(data)

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
    items = list(auction_items.find())
    auction_items_dict = {item['item_name']: item for item in items}

    for item_name, item in auction_items_dict.items():
        remaining_time = item['end_time'] - datetime.now()
        item['remaining_time'] = max(remaining_time, timedelta(0))

    return render_template('feed.html', auction_items=auction_items_dict)


@app.route('/bid', methods=['GET', 'POST'])
def bid():
    item_name = request.args.get('item_name') if request.method == 'GET' else request.form.get('item_name')
    item = auction_items.find_one({'item_name': item_name})
    print("test state 1")
    if request.method == 'POST':
        print("test state 2")

        bid_amount = request.form.get('bid_amount')
        username = session.get('username')

        if datetime.now() > item['end_time']:
            return "Bidding Period Ended!"

        print("Bid Amount:", bid_amount)
        print("Current Bid:", item['current_bid'])

        if bid_amount and float(bid_amount) > item['current_bid']:
            print("test state 3")
            auction_items.update_one({'item_name': item_name}, {'$set': {'current_bid': float(bid_amount), 'current_bidder': username}})
            return redirect(url_for('feed'))
        else:
            return "Invalid bid. Please try again."

    return render_template('bid.html', item_name=item_name, item_info=item)


@app.route('/post_item', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        starting_price = float(request.form.get('starting_price'))
        days_to_bid = int(request.form.get('days_to_bid'))

        # Calculate the end time by adding the specified number of days to the current time
        end_time = datetime.now() + timedelta(days=days_to_bid)

        if auction_items.find_one({'item_name': item_name}):
            return "An item with this name already exists. Please choose a different name."

        auction_items.insert_one({
            "item_name": item_name,
            "description": description,
            "current_bid": starting_price,
            "current_bidder": None,
            "end_time": end_time
        })
        updated_auction_data = {'item_name': item_name, 'description': description}
        broadcast_to_clients(json.dumps(updated_auction_data))

        return redirect(url_for('feed'))

    return render_template('post_item.html')






if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)