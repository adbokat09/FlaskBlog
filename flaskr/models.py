from datetime import datetime

from sqlalchemy import func, case
from werkzeug.security import check_password_hash

from flaskr.db import db
from sqlalchemy_utils import aggregated


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

    def __repr__(self):
        return f'<User id={self.id} usename={self.username}'

    def check_password(self, password):
        return check_password_hash(self.password, password)


PostXTag = db.Table(
    'PostXTag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    title = db.Column(db.String(400), nullable=False)
    short_description = db.Column(db.Text(), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    tags = db.relationship('Tag', secondary=PostXTag, lazy=True, backref=db.backref('post', lazy=True))

    @aggregated('likes', db.Column(db.Integer))
    def likes_number(self):
        return db.func.sum(case((Like.status == True, 1), else_=0))

    @aggregated('likes', db.Column(db.Integer))
    def dislikes_number(self):
        return db.func.sum(case((Like.status == False, 1), else_=0))

    likes = db.relationship('Like', backref='post', lazy=True)

    def __repr__(self):
        return f'<Post id={self.id} post_title={self.title}'


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag id={self.id} tagname={self.name}'


class Like(db.Model):
    LIKE = True
    DISLIKE = False
    UNSET = None
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True, nullable=False)
    status = db.Column(db.Boolean, nullable=True)

    @property
    def is_like(self):
        return self.status == self.LIKE

    @property
    def is_dislike(self):
        return self.status == self.DISLIKE

    @property
    def is_unset(self):
        return self.status == self.UNSET

    @classmethod
    def get_post_likes_num(cls, post_id: int) -> tuple[int, int]:
        likes_data = db.session.query(
            func.coalesce(func.sum(case((cls.status == True, 1), else_=0)), 0).label('count_likes'),
            func.coalesce(func.sum(case((cls.status == False, 1), else_=0)), 0).label('count_dislikes')
        ).filter(Like.post_id == post_id).one()

        return likes_data

    @classmethod
    def change_post_like_status(cls, post_id: int, user_id: int, action: bool):
        like = cls.query.filter_by(post_id=post_id, user_id=user_id).first()
        if not like:
            like = cls(post_id=post_id, user_id=user_id, status=action)
        elif like.status == action:
            like.status = cls.UNSET
        else:
            like.status = action

        db.session.add(like)
        db.session.commit()
