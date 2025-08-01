from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange

class BuyForm(FlaskForm):
    symbol = StringField('Stock Symbol', validators=[DataRequired()])
    shares = IntegerField('Number of Shares', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Buy')

class SellForm(FlaskForm):
    symbol = SelectField('Stock Symbol', choices=[], validators=[DataRequired()])
    shares = IntegerField('Number of Shares', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Sell')
