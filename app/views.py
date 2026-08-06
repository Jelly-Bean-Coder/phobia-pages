from pathlib import Path

from flask import Blueprint, render_template, current_app
import click
import json
from .models import Phobia, Tag
from .extensions import db
import os

os.chdir(Path(__file__).parent) # Change working directory to the current file's directory

views_blueprint = Blueprint('views', __name__)


@views_blueprint.route('/')
def home():
    phobia = db.session.query(Phobia).filter_by(name='Acrophobia').first()
    tags = [tag.name for tag in db.session.query(Tag).filter(Tag.phobias.any(name=phobia.name)).all()]

    if not phobia:
        return render_template("index.html")

    return render_template("index.html", title=phobia.name, fear_of=phobia.summary, tags=", ".join(tags).capitalize())

@views_blueprint.cli.command("update-db-json")
@click.option("--file-path", default="./static/json/phobias.json", help="path to json file")
@click.option("--reset", is_flag=True, default=False, help="Reset database")
def update_db(file_path, reset):
    with current_app.app_context():
        if reset:
            click.echo("Resetting database...")
            db.drop_all()
            db.create_all()

    with open(file_path) as json_file:
        data = json.load(json_file) # Load phobias

    for entry in data:
        if Phobia.query.filter_by(name=entry["name"]).first(): continue # Prevent duplicates

        phobia = Phobia(
            name=entry["name"],
            type=entry["type"],
            definition=entry["definition"],
            summary=entry["summary"],
            description=entry["description"],
            symptoms=entry["symptoms"],
        )
        db.session.add(phobia)

        for tag in entry.get("tags", []):
            formatted_tag = tag.lower().strip()

            tag_obj = Tag.query.filter_by(name=formatted_tag).first() # Check if tag exists
            if not tag_obj:
                tag_obj = Tag(name=formatted_tag)
                db.session.add(tag_obj)

            phobia.tags.append(tag_obj) # Add tag to phobia
        db.session.commit()