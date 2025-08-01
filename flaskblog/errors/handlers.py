from flask import Blueprint, render_template
from flaskblog.users.utils import calculate_portfolio_value

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@errors.app_errorhandler(500)
def error_500(error):
    total_value = 0
    try:
        total_value = calculate_portfolio_value() or 0
    except:
        pass
    return render_template('errors/500.html', total_value=total_value), 500