import sqlite3
from flask import current_app, g
import click


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.cursor().executescript(f.read().decode('utf-8'))


@click.command('init-db')
def init_db_command():
    # init_db()
    # click.echo('Database initialized.')
    create_tags()
    click.echo('Tags created.')


def create_tags():
    db = get_db()
    db.executemany(
        'insert into tags (name) values(?)',
        [('IT',), ('Art',), ('Sport',), ('Cars',), ('collecting',), ('Architecture',), ('traveling',),
         ('Animals',), ('Health',), ('Sleeping',)]
    )
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
