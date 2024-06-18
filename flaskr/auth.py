import functools
from flask import Blueprint, render_template, request, session, url_for, redirect, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()

        error = None
        if username is None:
            error = 'Username is required.'
        if password is None:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    'INSERT INTO user (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
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

        db = get_db()

        error = None

        user = db.execute('SELECT id, username, password FROM user WHERE username = ?', (username,)).fetchone()

        if not user or not check_password_hash(user['password'], password):
            error = 'Username or password is incorrect.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id:
        db = get_db()
        g.user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
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

