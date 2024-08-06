from flask import Blueprint, render_template, request, g, redirect, url_for, abort, flash
from sqlalchemy.sql.functions import current_user

from flaskr.db import db
from flaskr.auth import login_required
from flaskr.models import Post, Tag, Like

bp = Blueprint('blog', __name__)


@bp.route('/', methods=['GET'])
def index():
    search = request.args.get('search')
    posts = Post.query.options(db.joinedload(Post.author), db.joinedload(Post.tags))
    if search:
        posts = posts.filter(Post.title.ilike(f'%{search}%'))

    posts = posts.order_by(Post.created_at.desc()).all()
    for post in posts:
        print(post.title, post.likes_number, )
    return render_template('blog/index.html', posts=posts)


@bp.route('/<int:id>', methods=['GET'])
def post_details(id):
    post = get_post(id, check_if_author=False)

    likes_num, dislikes_num = Like.get_post_likes_num(post.id)
    like_status = None
    if g.user is not None:
        like_status = Like.query.filter_by(post_id=post.id, user_id=g.user.id).first()

    if like_status is not None:
        like_status = like_status.status

    return render_template(
        'blog/post_page.html', post=post,
        count_likes=likes_num,
        count_dislikes=dislikes_num,
        like_status=like_status,
        tags=post.tags
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
        body = request.form['description']
        tag_ids = request.form.getlist('tags')

        short_description, error = get_validated_description(short_description)

        if error is None:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            post = Post(
                title=title,
                body=body,
                short_description=short_description,
                author=g.user
            )
            db.session.add(post)
            post.tags.extend(tags)
            db.session.commit()

            return redirect(url_for('blog.index'))

        flash(error)

    tags = Tag.query.all()

    return render_template('blog/create.html', tags=tags)


def get_post(post_id, check_if_author: bool = False):

    post = Post.query.filter_by(id=post_id).options(db.joinedload(Post.author)).first()

    if post is None:
        abort(404)

    if check_if_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    post = get_post(id, check_if_author=True)
    if request.method == 'POST':
        title = request.form['title']
        short_description = request.form['short_description']
        body = request.form['body']
        tags = [int(x) for x in request.form.getlist('tags')]

        short_description, error = get_validated_description(short_description)

        if title is None:
            error = 'Title is required.'

        if error is None:
            post.title = title
            post.short_description = short_description
            post.body = body
            post.tags = Tag.query.filter(Tag.id.in_(tags)).all()
            db.session.add(post)
            db.session.commit()

            return redirect(url_for('blog.index'))
        flash(error)
    tags = Tag.query.all()

    post_tag_ids = [tag.id for tag in post.tags]

    return render_template('blog/update.html', post=post, tags=tags, post_tag_ids=post_tag_ids)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    post = get_post(id, check_if_author=True)

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('blog.index'))


@bp.route('/like/<int:id>', methods=['POST'])
@login_required
def like_post(id):
    Like.change_post_like_status(post_id=id, user_id=g.user.id, action=Like.LIKE)

    return redirect(url_for('blog.post_details', id=id))


@bp.route('/dislike/<int:id>', methods=['POST'])
@login_required
def dislike_post(id):
    Like.change_post_like_status(post_id=id, user_id=g.user.id, action=Like.DISLIKE)

    return redirect(url_for('blog.post_details', id=id))
