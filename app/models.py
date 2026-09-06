from datetime import datetime

from flask_login import UserMixin
from . import db

phobia_tag_bridge = db.Table(
    'phobia_tag_bridge',
    db.Column('phobia_id', db.Integer, db.ForeignKey('phobia.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Phobia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    definition = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    symptoms= db.Column(db.Text, nullable=False)

    tags = db.relationship('Tag', secondary=phobia_tag_bridge, back_populates='phobias')


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phobias = db.relationship('Phobia', secondary=phobia_tag_bridge, back_populates='tags')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gateway_tier = db.Column(db.Boolean, nullable=False, default=False)
    pro_tier = db.Column(db.Boolean, nullable=False, default=False)

    bookmarks = db.relationship('Bookmark', back_populates='user', lazy=True)
    logs = db.relationship('AnxietyLog', back_populates='user', lazy=True)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phobia_id = db.Column(db.Integer, db.ForeignKey('phobia.id'), nullable=False)

    user = db.relationship('User', back_populates='bookmarks')
    phobia = db.relationship('Phobia')


class AnxietyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Links to the specific phobia entry they were browsing/logging
    phobia_id = db.Column(db.Integer, db.ForeignKey('phobia.id'), nullable=False)

    # What specifically happened
    trigger = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    severity = db.Column(db.Integer, nullable=False)  # 1-10
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', back_populates='logs')
    phobia = db.relationship('Phobia')