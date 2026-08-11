from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask import flash, redirect, url_for
from functools import wraps
from flask_login import current_user

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def anonymity_required(redirect_to='views.home'):
    """
    Prevents logged-in users from accessing guest-only pages.
    Defaults to redirecting to the 'index' route.
    """

    def decorator(f):
        # We wrap the innermost function to preserve your original route's name
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated:
                # Optional: Let the user know why they were kicked out
                flash("You are already logged in.", "info")

                # Redirect to the customized target page
                return redirect(url_for(redirect_to))

            # If they are a guest, let them through to the original route
            return f(*args, **kwargs)

        return wrapper

    return decorator


def check_gateway(redirect_to='views.home'):
    """
    Prevents logged-in users from accessing guest-only pages.
    Defaults to redirecting to the 'index' route.
    """

    def decorator(f):
        # We wrap the innermost function to preserve your original route's name
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated:
                # Optional: Let the user know why they were kicked out
                if not current_user.is_gateway:
                    flash("You must have a Gateway or Pro subscription to use this feature.", "info")

                    # Redirect to the customized target page
                    return redirect(url_for(redirect_to))

            # If they are a guest, let them through to the original route
            return f(*args, **kwargs)

        return wrapper

    return decorator