from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_required, current_user
from flaskblog.trading.forms import BuyForm, SellForm
from flaskblog.models import StockTransaction
from flaskblog.extensions import db
import random
import yfinance as yf
from flaskblog.users.utils import calculate_portfolio_value, get_current_price

trading = Blueprint('trading', __name__)

@trading.route("/buy", methods=['GET', 'POST'])
@login_required
def buy():
    total_value = calculate_portfolio_value()
    form = BuyForm()
    if form.validate_on_submit():
        price = get_current_price(form.symbol.data.upper())
        transaction = StockTransaction(user_id=current_user.id, stock_symbol=form.symbol.data.upper(), shares=form.shares.data, price= price or 0, transaction_type='buying')
        db.session.add(transaction)
        db.session.commit()
        flash(f'Bought {form.shares.data} shares of {form.symbol.data.upper()}', 'success')
        return redirect(url_for('buy.html'))
    stock_options = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    return render_template('buy.html', form=form, portfolio=current_user.get_portfolio(), advice=get_stock_advice(), total_value=total_value, stock_options=stock_options)

@trading.route("/sell", methods=['GET', 'POST'])
@login_required
def sell():
    form = SellForm(request.form)  # Explicitly bind to request data
    
    # Always rebuild choices fresh for each request
    stock_options = db.session.query(
        StockTransaction.stock_symbol
    ).filter_by(user_id=current_user.id).distinct().all()
    
    form.symbol.choices = [(s[0], s[0]) for s in stock_options]  # Ensure choices are fresh

    if request.method == 'POST' and form.validate():
        try:
            # Explicit type conversion as safety measure
            shares_to_sell = int(form.shares.data)
            symbol = str(form.symbol.data).upper()  # Ensure string type
            
            # Rest of your sell logic...
            current_shares = db.session.query(
                db.func.sum(StockTransaction.shares)
            ).filter_by(
                user_id=current_user.id,
                stock_symbol=symbol
            ).scalar() or 0

            if shares_to_sell <= 0:
                flash("Number of shares must be positive", "danger")
                return redirect(url_for('trading.sell'))

            if current_shares < shares_to_sell:
                flash(f"Not enough shares to sell. You own {current_shares}.", "danger")
                return redirect(url_for('trading.sell'))

            # Get current price
            try:
                stock = yf.Ticker(symbol)
                price = stock.info.get('regularMarketPrice', 0)
            except Exception as e:
                flash(f"Error getting stock price: {str(e)}", "danger")
                return redirect(url_for('trading.sell'))

            # Create transaction
            transaction = StockTransaction(
                user_id=current_user.id,
                stock_symbol=symbol,
                shares=-shares_to_sell,  # Negative for sell
                price=price,
                transaction_type='sell'
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            flash(f"Successfully sold {shares_to_sell} shares of {symbol}", "success")
            return redirect(url_for('trading.sell'))

        except ValueError as e:
            flash(f"Invalid input: {str(e)}", "danger")
            return redirect(url_for('trading.sell'))

    total_value = calculate_portfolio_value()
    return render_template('sell.html',
        form=form,
        portfolio=current_user.get_portfolio(),
        total_value=total_value,
        stock_options=form.symbol.choices)

def get_stock_advice():

    advice_samples = [
        "Consider buying low-volatility stocks this week.",
        "Tech sector shows positive momentum.",
        "Monitor energy stocks — prices are volatile.",
        "Diversify to reduce risk.",
        "Sell if a stock has risen too fast."
    ]
    return random.choice(advice_samples)
