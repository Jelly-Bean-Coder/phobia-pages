from flask import Blueprint, render_template, current_app, request
import click
import json

from flask_login import login_required, current_user

from .models import Phobia, Tag
from .extensions import db

views_blueprint = Blueprint('views', __name__)

@views_blueprint.route("/")
def home():
    try:
        tags = Tag.query.all()
        return render_template("pre-search.html", all_tags=tags)

    except Exception as e:
        print(e)


@views_blueprint.route('/after_search', methods=['POST'])
def after_search():
    phobias = []

    if request.form.get("phobia") and request.form.getlist("tags"):
        queried_phobias = Phobia.query.filter(Phobia.name.ilike(f"%{request.form.get("phobia")}%")).all()
        tags = Tag.query.filter(Tag.name.in_(request.form.getlist("tags"))).all()

        if tags:
            for tag in tags:
                for phobia in queried_phobias:
                    for phobia_tag in phobia.tags:
                        if tag.name == phobia_tag.name:
                            if phobia not in phobias:
                                phobias.append(phobia)

    elif request.form.getlist("tags"):
        tags = Tag.query.filter(Tag.name.in_(request.form.getlist("tags"))).all()
        print(tags)

        if tags != []:
            for tag in tags:
                for phobia in tag.phobias:
                    if phobia not in phobias:
                        phobias.append(phobia)

    elif request.form.get("phobia"):
        phobia_query_name = None

        if request.form.get("phobia"):
            phobia_query_name = Phobia.query.filter(Phobia.name.ilike(f"%{request.form.get("phobia")}%")).all()

        if phobia_query_name:
            for phobia in phobia_query_name:
                phobias.append(phobia)



    else:
        return render_template("error.html", error="Invalid search term")

    if not phobias:
        return render_template("error.html", error="No phobia found")


    return render_template("post-search.html", phobias=phobias)

@views_blueprint.route('/bookmarks', methods=['POST', 'GET'])
@login_required
def bookmarks():
    return render_template("bookmarks.html", bookmarks=current_user.bookmarks)

@views_blueprint.route('/detailed_phobia', methods=['GET'])
def detailed_phobia():
    if not request.args.get("phobia_id"):
        return render_template("error.html", error="No phobia ID provided")

    if not Phobia.query.filter_by(id=request.args.get("phobia_id")).first():
        return render_template("error.html", error="Phobia not found")

    return render_template("detailed-phobia.html", phobia=Phobia.query.filter_by(id=request.args.get("phobia_id")).first())

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