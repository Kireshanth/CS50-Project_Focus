import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, validate, greeting

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///focus.db")

# Make sure API key is set --> Look into adding API integration with Google Calender later
#if not os.environ.get("API_KEY"): raise RuntimeError("API_KEY not set")

@app.route("/delete/<int:task_id>")
@login_required
def delete(task_id):
    db.execute("DELETE FROM tasks WHERE task_id = ?", task_id)
    return redirect("/tasks")

@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    db.execute("CREATE TABLE IF NOT EXISTS tasks(task TEXT NOT NULL, comment TEXT NOT NULL, user_id TEXT NOT NULL, task_id INTEGER PRIMARY KEY AUTOINCREMENT, priority INTEGER NOT NULL, record TEXT NOT NULL, deadline TEXT NOT NULL)")
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY priority DESC", session["user_id"])
    print(tasks)

    if request.method == "POST":

        # get user input
        task = request.form.get("task")
        comments = request.form.get("comments")
        priority = request.form.get("priority")
        deadline = request.form.get("deadline")

        # validate user input
        try:
            priority = int(priority)
        except:
            flash("Please enter in a value from 1 to 5")
            pass

        # check to see if task database exists, then store task into database
        db.execute("INSERT INTO tasks(task, comment, user_id, priority, record, deadline) VALUES (?,?,?,?, datetime('now','localtime'),?)", task, comments, session["user_id"], priority, deadline)
        flash("Task added succesfully!")
    
        return redirect("/tasks")

    else:
        return render_template("tasks.html", tasks=tasks)

# GENERAL APP FUNCTIONALITY 

@app.route("/")
@login_required
def index():
    #Show dashboard of tasks, allow user to add and close out tasks"""
    return apology("TODO")

@app.route("/login", methods=["GET", "POST"])
def login():
    #Log user in

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    #Log user out

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check to see if username already exists and if user entered in password details correctly
        current_user = db.execute("SELECT * FROM users WHERE username = ?", name)
        if not name or len(current_user) == 1:
            return apology("User’s input is blank or the username already exists")
        elif not password or password != confirmation:
            return apology("Either password input is blank or the passwords do not match")

        # check to see if password meets character requirements
        elif validate(password) != True:
            return validate(password)

        else:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", name, generate_password_hash(password))
            flash("Registered!")
            return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    #Allow users to enter in personal information and change password
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        new_password_confirm = request.form.get("new_password_confirm")

        # Retrieve current hash of user's password stored in database
        current_pass_hash = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        # Check to see if all input fields were completed
        if not old_password or not new_password or not new_password_confirm:
            return apology("Password field is missing")

        # Check to see if user has confirmed their new password successfully, then check to see if user has entered in their correct current password
        if new_password == new_password_confirm:
            if check_password_hash(current_pass_hash[0]["hash"], old_password):
                db.execute("Update users SET hash = ? WHERE id = ?", generate_password_hash(new_password), session["user_id"])
            else:
                return apology("Current password entered is not correct")
        else:
            return apology("Please confirm new password")

        flash("Password has been successfully changed")
        return redirect("/account")

    else:
        return render_template("account.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
