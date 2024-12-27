from flask import redirect, render_template, request, session
from functools import wraps


def login_required(f):
    """
    Taken from flask documentation itself
    - Redirects user into login page if they try to access the website content without logging in

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
