from flask import Blueprint, render_template, request, flash, url_for, redirect, session
from flask_login import login_required, login_manager, logout_user, current_user
from .models import User
from .extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

auth_blueprint = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                load_user(user.id)
                flash("Login successful", category="success")
                return redirect(url_for('views.home'))
            else:
                flash("Invalid email or password", category="error")


    return render_template("login.html")



@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out", category="success") # Attempt to make an info cat. later
    return redirect(url_for('views.login'))

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        check_password = request.form.get('password')


        if email and password:
            user = User.query.filter_by(email=email).first()
            if user:
                flash("Email already exists", category="error")
            elif len(email) < 4:
                flash("Email must be greater than 3 characters", category="error")
            elif len(username) < 2:
                flash("Username must be greater than 1 character", category="error")
            elif password != check_password:
                flash("Passwords don't match", category="error")
            elif len(password) < 7:
                flash("Password must be at least 7 characters", category="error")

            else:
                new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash( "User created successfully", category="success")



@auth_blueprint.route('/billing', methods=['GET'])
@login_required
def billing():
    return "<h1>Billing</h1>"