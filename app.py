from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates')

users = {}
auction_items = {
}


@app.route('/')
def index():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users:
            return "Username already used"
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
            return "Invalid credentials, please try again!"

    return render_template('login.html')

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
    app.run(port=5001, debug=True)