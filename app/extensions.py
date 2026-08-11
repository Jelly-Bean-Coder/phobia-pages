from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask import flash, redirect, url_for, render_template
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


def check_gateway(f):
    """
    Prevents basic users from accessing gateway features.
    Defaults to redirecting to the 'index' route.
    """
        # We wrap the innermost function to preserve your original route's name
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and (current_user.gateway_tier or current_user.pro_tier):
            return f(*args, **kwargs)

        # If they are a gateway or Pro, let them through to the original route
        flash("You must have a Gateway or Pro subscription to use this feature.", "info")
        return "Forbidden", 403

    return wrapper


def check_gateway(f):
    """
    Prevents basic users from accessing gateway features.
    Defaults to redirecting to the 'index' route.
    """
        # We wrap the innermost function to preserve your original route's name
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.pro_tier:
            return f(*args, **kwargs)
        # If they are a Pro, let them through to the original route

        flash("You must have a Pro subscription to use this feature.", "info")
        return "Forbidden", 403

    return wrapper
