from flask import Flask
from .extensions import db
from .models import Phobia, Tag

def create_app():

    app = Flask(__name__) # Create app

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///phobias.db" # set location of database
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .views import views_blueprint
    app.register_blueprint(views_blueprint) # Register all routes. Done later to prevent circular imports

    with app.app_context(): # Create tables for M2M relationship
        db.create_all()

    return app

