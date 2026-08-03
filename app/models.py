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