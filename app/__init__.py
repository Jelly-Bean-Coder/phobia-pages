from flask import Flask
from .extensions import db, login_manager, csrf
from .models import Phobia, Tag
import os

def create_app():

    app = Flask(__name__) # Create app

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///phobias.db" # set location of database
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .views import views_blueprint
    from .auth import auth_blueprint
    app.register_blueprint(views_blueprint) # Register all routes. Done later to prevent circular imports
    app.register_blueprint(auth_blueprint)

    with app.app_context(): # Create tables for M2M relationship
        db.create_all()

    return app

