import os
import requests
import urllib.parse
import re

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import datetime


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def validate(password):
    while True:
        if len(password) < 8:
            return apology("Make sure password is at least 8 letters")
        elif re.search('[0-9]', password) is None:
            return apology("Make sure your password has a number in it")
        elif re.search('[A-Z]', password) is None:
            return apology("Make sure your password has a capital letter in it")
        else:
            break
    return True

def greeting():
    now = datetime.now()
    print(now)
    current_time = int(now.strftime("%H"))

    if current_time < 12:
        greeting = 'Good morning '
    if current_time > 12:
        greeting = 'Good afternoon '
    else:
        greeting = 'Good evening '

    return greeting


