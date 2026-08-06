from pathlib import Path

from flask import Blueprint, render_template, current_app, request
import click
import json
from .models import Phobia, Tag
from .extensions import db
import os

views_blueprint = Blueprint('views', __name__)

@views_blueprint.route("/")
def home():
    try:
        tags = Tag.query.all()
        return render_template("pre-search.html", all_tags=Tag.query.all())

    except Exception as e:
        print(e)


@views_blueprint.route('/after_search', methods=['POST'])
def after_search():
    phobias = None
    if request.form.get("phobia") and request.form.get("tag"):
        phobias = []
        tag_objs = Tag.query.filter_by(name=request.form.get("tag")).first()
        if tag_objs:
            tagged_phobias = tag_objs.phobias
            for fear in tagged_phobias:
                if fear.name == request.form.get("phobia"):
                    phobias.append(fear)

    elif request.form.get("tag"):
        tags = Tag.query.filter_by(name=request.form.get("tag")).first()
        if tags:
            phobias = tags.phobias

    elif request.form.get("phobia"):
        phobia = Phobia.query.filter_by(name=request.form.get("phobia")).all()
        if phobia:
            phobias = phobia



    else:
        return render_template("error.html", error="Invalid search term")

    if not phobias:
        return render_template("error.html", error="No phobia found")


    return render_template("post-search.html", phobias=phobias)

@views_blueprint.cli.command("update-db-json")
@click.option("--file-path", default="./static/json/phobias.json", help="Path to json file")
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