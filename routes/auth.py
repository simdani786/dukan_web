from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import datetime

auth_bp = Blueprint('auth', __name__)

# Dummy user data (Replace with database check)
users = {
    "admin": "password123",
    "user1": "1234"
}

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember")

        if username in users and users[username] == password:
            session['username'] = username
            
            # Set session expiry for "remember me"
            if remember:
                # Session will last for 30 days
                session.permanent = True
                session.permanent_session_lifetime = datetime.timedelta(days=30)
            else:
                # Default session expires when browser closes
                session.permanent = False
                
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop('username', None)
    flash("Logged out successfully", "info")
    return redirect(url_for("auth.login"))