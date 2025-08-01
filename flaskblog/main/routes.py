from flask import render_template, request, Blueprint
from flaskblog.models import StockTransaction
from flask_login import login_required, current_user
import yfinance as yf
from flaskblog.users.utils import calculate_portfolio_value

main = Blueprint('main', __name__)

@main.route("/portfolio")
@login_required
def portfolio():
    transactions = StockTransaction.query.filter_by(user_id=current_user.id).all()
    total_value = 0

    holdings = {}
    for txn in transactions:
        symbol = txn.stock_symbol.upper()
        if symbol not in holdings:
            holdings[symbol] = {'shares': 0, 'total_spent': 0}
        
        holdings[symbol]['shares'] += txn.shares

        if txn.transaction_type == 'buy':
            holdings[symbol]['total_spent'] += txn.shares * txn.price

    portfolio_data = []
    for symbol, data in holdings.items():
        if data['shares'] <= 0:
            continue

        stock = yf.Ticker(symbol)
        try:
            current_price = stock.info.get('regularMarketPrice', 0)
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")
            current_price = 0

        value = data['shares'] * current_price
        gain_loss = value - data['total_spent']
        total_value += value

        portfolio_data.append({
            'ticker': symbol,
            'shares': data['shares'],
            'current_price': current_price,
            'value': value,
            'gain_loss': gain_loss
        })

    return render_template("portfolio.html",
                           title="Portfolio",
                           portfolio_data=portfolio_data,
                           total_value=total_value)

@main.route("/")
@main.route("/home")
def home():
    total_value = calculate_portfolio_value()
    return render_template('home.html', total_value=total_value)