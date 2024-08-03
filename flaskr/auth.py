import functools
from flask import Blueprint, render_template, request, session, url_for, redirect, flash, g
from werkzeug.security import generate_password_hash
from flaskr.db import db
from flaskr.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None
        if username is None:
            error = 'Username is required.'
        if password is None:
            error = 'Password is required.'

        if error is None:
            try:
                user = User(
                    username=username,
                    password=generate_password_hash(password)
                )
                db.session.add(user)
                db.session.commit()
            except:
                error = f'Username {username} already exists.'
            else:
                return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            error = 'Username or password is incorrect.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id:
        g.user = User.query.get(user_id)
    else:
        g.user = None

@bp.route('/logout')
def logout():
    session.clear()
    g.user = None
    return redirect(url_for('blog.index'))


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)


    return wrapper

