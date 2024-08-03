from flask import Blueprint, render_template

bp = Blueprint('errors', __name__, url_prefix='')


@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html')