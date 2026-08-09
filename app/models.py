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
    gateway_tier = db.Column(db.Boolean, nullable=False)
    pro_tier = db.Column(db.Boolean, nullable=False, default=False)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phobia_id = db.Column(db.Integer, db.ForeignKey('phobia.id'), nullable=False)
