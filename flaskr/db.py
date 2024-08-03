import sqlite3
from flask import current_app, g
import click
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # engine_options={'echo': True}


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    from flaskr.models import User, Post, Tag, PostXTag, Like
    with current_app.app_context():
        db.create_all()


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Database initialized.')
    create_tags()
    click.echo('Tags created.')


def create_tags():
    from flaskr.models import Tag

    tags = [
        Tag(
            name='IT'
        ),
        Tag(
            name='Art'
        ),
        Tag(
            name='Sport'
        ),
        Tag(
            name='Cars'
        ),
        Tag(
            name='Collecting'
        ),

        Tag(
            name='Architecture'
        ),
        Tag(
            name='Traveling'
        ),
        Tag(
            name='Animals'
        ),
        Tag(
            name='Health'
        ),
        Tag(
            name='Sleeping'
        )
    ]
    db.session.bulk_save_objects(tags)
    db.session.commit()

