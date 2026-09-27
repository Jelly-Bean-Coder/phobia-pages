import http
# CRITICAL: Import Werkzeug's HTTPException instead of http.client's
from werkzeug.exceptions import HTTPException

from flask import Flask, render_template
from .extensions import db, login_manager, csrf
from .models import Phobia, Tag
import os
import socket

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
    from .extensions import js_stream_bp

    app.register_blueprint(views_blueprint) # Register all routes. Done later to prevent circular imports
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(js_stream_bp)

    with app.app_context(): # Create tables for M2M relationship
        db.create_all()

    # Define error_codes here so it is available inside the error handler below
    error_codes = [status.value for status in http.HTTPStatus if status.value >= 400]

    # Error handler function (Takes exactly ONE argument: error)
    @app.errorhandler(HTTPException)
    def error_handler(error):
        # Werkzeug HTTPExceptions natively provide 'code' and 'description' attributes
        code = getattr(error, 'code', None)
        error_msg = getattr(error, 'description', "no error message")

        if not error_msg:
            error_msg = "no error message"

        # Safe formatting now that error_codes is defined above
        error_text = f"Error {str(code) if code else '[SYSTEM]'}: {error_msg}"

        # Returning the code along with the template passes the true HTTP status to the browser
        return render_template("error.html", error=error_text), code

    return app
