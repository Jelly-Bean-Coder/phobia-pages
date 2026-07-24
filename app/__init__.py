from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # Create database
cursor = db.session
from . import models

def create_app():
    app = Flask(__name__) # Create app

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///phobias.db" # set location of database
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .routes import routes_blueprint
    app.register_blueprint(routes_blueprint) # Register all routes. Done later to prevent circular imports

    with app.app_context(): # Create tables for M2M relationship
        db.create_all()

    return app