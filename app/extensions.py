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
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated:
                flash("You are already logged in.", "info")
                return redirect(url_for(redirect_to))

            return f(*args, **kwargs)

        return wrapper

    return decorator


def check_gateway(f):
    """
    Prevents basic users from accessing gateway features.
    Allows both Gateway and Pro tier users to pass.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Cleaned up '== True' checks for idiomatic Python code
        if current_user.is_authenticated and (current_user.gateway_tier or current_user.pro_tier):
            return f(*args, **kwargs)

        flash("You must have a Gateway or Pro subscription to use this feature.", "info")
        return "Forbidden", 403

    return wrapper


def check_pro(f):
    """
    Restricts access strictly to Pro tier users only.
    """
    # Fixed the indentation error on these lines
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.pro_tier:
            return f(*args, **kwargs)

        flash("You must have a Pro subscription to use this feature.", "info")
        return "Forbidden", 403

    return wrapper
