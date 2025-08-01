import os
import secrets
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail
import yfinance as yf
from flask_login import current_user
from flaskblog.models import StockTransaction

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    return stock.info.get('regularMarketPrice')

def calculate_portfolio_value():
    if not current_user.is_authenticated:
        return 0

    transactions = StockTransaction.query.filter_by(user_id=current_user.id).all()
    holdings = {}
    
    for txn in transactions:
        symbol = txn.stock_symbol
        if symbol not in holdings:
            holdings[symbol] = 0
        holdings[symbol] += txn.shares

    total_value = 0
    for symbol, shares in holdings.items():
        try:
            price = yf.Ticker(symbol).info.get("regularMarketPrice", 0)
        except:
            price = 0
        total_value += shares * price

    return total_value