from flask import Blueprint, render_template, current_app, request, redirect, url_for
import click
import json

from flask_login import login_required, current_user
from sqlalchemy import null

from .models import Phobia, Tag, User, Bookmark, AnxietyLog
from .extensions import db, check_gateway, newFlash

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

        if not tags:
            return render_template("error.html", error="No tags selected")

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
@check_gateway
def bookmarks():
    return render_template("bookmarks.html", bookmarks=current_user.bookmarks)


@views_blueprint.route('/create_bookmark', methods=['GET'])
@check_gateway
def create_bookmark():
    phobia_id = request.args.get('phobia_id')
    if current_user.is_authenticated:
        if phobia_id:
            if Bookmark.query.filter_by(phobia_id=phobia_id, user_id=current_user.id).first():
                db.session.delete(Bookmark.query.filter_by(phobia_id=phobia_id, user_id=current_user.id).first())
                db.session.commit()
                return "Bookmark removed successfully", 200

            bookmark = Bookmark(user_id=current_user.id, phobia_id=phobia_id)
            db.session.add(bookmark)
            db.session.commit()
            return "Bookmark created successfully", 201

    return render_template(f"{request.endpoint}.html", phobia_id=phobia_id)


@views_blueprint.route('/logs', methods=['GET'])
@login_required
@check_gateway
def logs():
    chart_list = []
    dates_list = []

    chart_list.append(["Date"])
    for log in current_user.logs:
        if log.phobia.name not in chart_list[0]:
            chart_list[0].append(log.phobia.name)

    for _ in chart_list[0]:
        for log in current_user.logs:
            if log.created_at.strftime("%Y-%m-%d") not in dates_list:
                dates_list.append(log.created_at.strftime("%Y-%m-%d"))

    for date in dates_list:
        tmp = [date] + [None] * (len(chart_list[0]) - 1)  # Initialize with None for each phobia

        for log in AnxietyLog.query.filter_by(user_id=current_user.id).filter(db.func.date(AnxietyLog.created_at) == date).all():

            for i in range(len(chart_list[0])):
                if not i: continue # If "i" is 0, skip (date column)

                if chart_list[0][i] == log.phobia.name: # If the phobia name matches, append the severity
                    tmp[i] = log.severity

        chart_list.append(tmp)

    return render_template("logs.html", logs=current_user.logs, phobias=Phobia.query.all(), pro=current_user.pro_tier, matrix=chart_list)


@views_blueprint.route('/create_log', methods=['POST'])
@login_required
@check_gateway
def create_log():
    if request.method == 'POST':
        log_form = request.form
        if log_form:
            db.session.add(
                AnxietyLog(user_id=current_user.id, phobia_id=log_form.get("phobia"), trigger=log_form.get("trigger"),
                           notes=log_form.get("notes"), severity=log_form.get("severity")))
            db.session.commit()
            newFlash('Log created successfully!', 'success')
        else:
            newFlash('Log content cannot be empty.', 'error')

    return redirect(url_for('views.logs'))


@views_blueprint.route('/delete_log', methods=['POST'])
@login_required
@check_gateway
def delete_log():
    if request.method == 'POST':
        data = request.get_json()

        if not data: return "Invalid JSON data", 400

        log_id = data.get('log_id')
        if not data.get('log_id'): return "Error: No log ID provided", 400

        log = AnxietyLog.query.get(log_id)
        if not log: return "Error: Log not found", 404

        if log.user.id != current_user.id:
            newFlash('You do not have permission to edit this log.', 'error')
            return "Error: You do not have permission to edit this log", 403

        try:
            db.session.delete(log)
            db.session.commit()
            newFlash('Log deleted successfully!', 'success')

            return "Log deleted successfully!", 200

        except:
            newFlash('Cannot delete log', 'error')

    return redirect(url_for('views.logs'))


@views_blueprint.route('/detailed_phobia', methods=['GET'])
def detailed_phobia():
    if not request.args.get("phobia_id"):
        return render_template("error.html", error="No phobia ID provided")

    if not Phobia.query.filter_by(id=request.args.get("phobia_id")).first():
        return render_template("error.html", error="Phobia not found")

    return render_template("detailed-phobia.html",
                           phobia=Phobia.query.filter_by(id=request.args.get("phobia_id")).first())


# DEV COMMAND
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
        data = json.load(json_file)  # Load phobias

    for entry in data:
        if Phobia.query.filter_by(name=entry["name"]).first(): continue  # Prevent duplicates

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

            tag_obj = Tag.query.filter_by(name=formatted_tag).first()  # Check if tag exists
            if not tag_obj:
                tag_obj = Tag(name=formatted_tag)
                db.session.add(tag_obj)

            phobia.tags.append(tag_obj)  # Add tag to phobia
        db.session.commit()