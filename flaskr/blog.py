from flask import Blueprint, render_template, request, g, redirect, url_for, abort, flash
from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)


@bp.route('/', methods=['GET'])
def index():
    search = request.args.get('search')
    print(search)
    db = get_db()
    query = (
        'SELECT p.id, p.title, p.short_description, p.created, u.username, p.author_id '
        'FROM post p '
        'JOIN user u ON p.author_id = u.id '
    )
    if search:
        query += 'where p.title like ? '
    query += 'ORDER BY created DESC'
    if search:
        posts = db.execute(query, (f'%{search}%',)).fetchall()
    else:
        posts = db.execute(query).fetchall()

    posts = list(map(dict, posts))

    posts = posts or []
    post_ids = ', '.join([str(i['id']) for i in posts])

    tags = db.execute(
        'select id, name, post_id '
        'from post_tags p '
        'join tags t on p.tag_id = t.id '
        f'where p.post_id in ({post_ids})'
    ).fetchall()

    tags_by_post_id = {}

    for tag in tags:
        # tags_by_post_id[tag['post_id']] = tags_by_post_id.get(tag['post_id'], []) + [tag]
        if tag['post_id'] in tags_by_post_id:
            tags_by_post_id[tag['post_id']].append(tag)
        else:
            tags_by_post_id[tag['post_id']] = [tag]

    for post in posts:
        post['tags'] = tags_by_post_id.get(post['id'], [])

    return render_template('blog/index.html', posts=posts)


@bp.route('/<int:id>', methods=['GET'])
def post_details(id):
    post = get_post(id, check_if_author=False)
    db = get_db()
    likes_data = db.execute(
        'select '
        'coalesce(sum(case when like_status is True then 1 end), 0) count_likes, '
        'coalesce(sum(case when like_status is False then 1 end), 0) count_dislikes '
        'from likes '
        'where post_id=? ',
        (id,)
    ).fetchone()
    like_status = None
    if g.user is not None:
        like_status = db.execute(
            'select '
            'like_status '
            'from likes '
            'where post_id=? and user_id=?',
            (id, g.user['id'])
        ).fetchone()

    if like_status is not None:
        like_status = like_status['like_status']

    tags = db.execute(
        'select id, name, post_id '
        'from tags '
        'join post_tags on post_tags.tag_id=tags.id '
        'where post_id=?',
        (id,)
    ).fetchall()

    return render_template(
        'blog/post_page.html', post=post,
        count_likes=likes_data['count_likes'],
        count_dislikes=likes_data['count_dislikes'],
        like_status=like_status,
        tags=tags
    )


def get_validated_description(value: str):
    value = ' '.join(value.split('\n'))
    if not 3 <= len(value) <= 300:
        return value, 'Short Description must be between 3 and 300 characters'
    return value, None


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        short_description = request.form['short_description']
        body = request.form['body']
        tags = request.form.getlist('tags')

        short_description, error = get_validated_description(short_description)

        if error is None:
            db = get_db()
            row = db.execute(
                'INSERT INTO post (title, short_description, body, author_id) '
                'VALUES (?, ?, ?, ?)',
                (title, short_description, body, g.user['id'])
            )
            db.commit()

            db.executemany(
                'INSERT INTO post_tags (post_id, tag_id) '
                'VALUES (?, ?)',
                [(row.lastrowid, tag) for tag in tags]
            )
            db.commit()
            return redirect(url_for('blog.index'))

        flash(error)

    db = get_db()

    tags = db.execute(
        'select * from tags '
    ).fetchall()

    return render_template('blog/create.html', tags=tags)


def get_post(post_id, check_if_author: bool = False):
    db = get_db()
    post = db.execute(
        'SELECT  p.id, title,short_description,  body, created, username, p.author_id '
        'FROM post p '
        'JOIN user u ON p.author_id = u.id '
        'WHERE p.id = ?', (post_id,)
    ).fetchone()
    if post is None:
        abort(404)

    if check_if_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    db = get_db()
    post = get_post(id, check_if_author=True)
    if request.method == 'POST':
        title = request.form['title']
        short_description = request.form['short_description']
        body = request.form['body']

        short_description, error = get_validated_description(short_description)

        if title is None:
            error = 'Title is required.'

        if error is None:
            db.execute(
                'UPDATE post SET title = ?, short_description = ?, body = ? WHERE id = ?',
                (title, short_description, body, id)
            )
            db.commit()

            return redirect(url_for('blog.index'))
        flash(error)

    db = get_db()

    tags = db.execute(
        'select * from tags '
    ).fetchall()

    return render_template('blog/update.html', post=post, tags=tags)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    get_post(id, check_if_author=True)

    db = get_db()
    db.execute(
        'DELETE FROM post WHERE id = ?', (id,)
    )
    db.commit()

    return redirect(url_for('blog.index'))


@bp.route('/like/<int:id>', methods=['POST'])
@login_required
def like_post(id):
    db = get_db()
    status = db.execute(
        'select like_status '
        'from likes '
        'where user_id=? AND post_id=?',
        (g.user['id'], id)
    ).fetchone()

    if status and status['like_status']:
        db.execute(
            'update likes set like_status=null '
            'where post_id=? and user_id=?',
            (id, g.user['id'])
        )
        db.commit()

    elif status is None:
        db.execute(
            'INSERT INTO likes (post_id, user_id, like_status)'
            'VALUES (?, ?, ?)',
            (id, g.user['id'], True)
        )
        db.commit()

    elif status and not status['like_status']:
        db.execute(
            'update likes set like_status=TRUE '
            'where post_id=? and user_id=?',
            (id, g.user['id'])
        )
        db.commit()
    # fix html
    return redirect(url_for('blog.post_details', id=id))


@bp.route('/dislike/<int:id>', methods=['POST'])
@login_required
def dislike_post(id):
    db = get_db()
    status = db.execute(
        'select like_status '
        'from likes '
        'where user_id=? AND post_id=?',
        (g.user['id'], id)
    ).fetchone()
    if status and status['like_status'] is False:
        db.execute(
            'update likes set like_status=null '
            'where post_id=? and user_id=?',
            (id, g.user['id'])
        )
        db.commit()

    elif status is None:
        db.execute(
            'INSERT INTO likes (post_id, user_id, like_status) '
            'VALUES (?, ?, ?)',
            (id, g.user['id'], False)
        )
        db.commit()

    elif status and status['like_status'] or status and status['like_status'] is None:
        db.execute(
            'update likes set like_status=False '
            'where post_id=? and user_id=?',
            (id, g.user['id'])
        )
        db.commit()

    return redirect(url_for('blog.post_details', id=id))
