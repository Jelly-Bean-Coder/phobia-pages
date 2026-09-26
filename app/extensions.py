from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask import redirect, url_for, Blueprint, Response
from functools import wraps
from flask_login import current_user
import time
import json

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# --- REAL-TIME JS STREAM STATE ---
js_stream_bp = Blueprint('js_stream', __name__)

# Tracks the function name, string data payload, and active state
trigger_state = {"function_name": "", "payload": "", "active": False}


def call_js(function_name, payload=""):
    """
    Fires a JS event. If payload is a dict/list, it converts it to JSON automatically.
    Example: call_js("flash", {"message": "Hello!", "type": "success"})
    """
    trigger_state["function_name"] = function_name

    # Serialize objects to JSON strings so JavaScript can parse them easily
    if isinstance(payload, (dict, list)):
        trigger_state["payload"] = json.dumps(payload)
    else:
        trigger_state["payload"] = str(payload)

    trigger_state["active"] = True


@js_stream_bp.route('/js-event-stream')
def js_event_stream():
    """
    The endpoint your frontend JavaScript will connect to via EventSource.
    """

    def event_stream():
        while True:
            if trigger_state["active"]:
                # Sends the specific function name as the event type, and data as the payload
                yield f"event: {trigger_state['function_name']}\n"
                yield f"data: {trigger_state['payload']}\n\n"
                trigger_state["active"] = False
            time.sleep(0.1)  # Prevents high CPU usage

    return Response(event_stream(), mimetype="text/event-stream")


# --- ORIGINAL DECORATORS WITH REAL-TIME JS INTEGRATION ---

def anonymity_required(redirect_to='views.home'):
    """
    Prevents logged-in users from accessing guest-only pages.
    Defaults to redirecting to the 'index' route.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated:
                # Trigger the browser UI alert instantly before redirecting
                call_js("flash", {"message": "You are already logged in.", "type": "info"})
                newFlash("You are already logged in.", "info")
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
        if current_user.is_authenticated and (current_user.gateway_tier or current_user.pro_tier):
            return f(*args, **kwargs)

        msg = "You must have a Gateway or Pro subscription to use this feature."
        # Trigger your JavaScript newFlashMessage dynamically
        call_js("flash", {"message": msg, "type": "warning"})

        newFlash(msg, "info")
        return "Forbidden", 403

    return wrapper


def check_pro(f):
    """
    Restricts access strictly to Pro tier users only.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.pro_tier:
            return f(*args, **kwargs)

        msg = "You must have a Pro subscription to use this feature."
        # Trigger your JavaScript newFlashMessage dynamically
        call_js("flash", {"message": msg, "type": "danger"})

        newFlash(msg, "info")
        return "Forbidden", 403

    return wrapper

def newFlash(message, category="info"):
    """
    A utility function to trigger a flash message both server-side and client-side.
    """
    # Trigger your JavaScript newFlashMessage dynamically
    call_js("flash", {
        "message": message,
        "type": category
    })

    # Also flash it server-side for any non-JS fallback