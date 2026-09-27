from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required, logout_user, current_user, login_user
from .models import User
from .extensions import db, login_manager, anonymity_required, newFlash
from werkzeug.security import generate_password_hash, check_password_hash

auth_blueprint = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_blueprint.route('/login', methods=['GET', 'POST'])
@anonymity_required()
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                login_user(user, remember=True)
                newFlash("Login successful", category="success")
                return redirect(url_for('views.home'))
            else:
                newFlash("Invalid email or password", category="error")


    return render_template("login.html")



@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    newFlash("You have been logged out", category="success") # Attempt to make an info cat. later
    return redirect(url_for('auth.login'))

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
@anonymity_required()
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        check_password = request.form.get('password')


        if email and password:
            user = User.query.filter_by(email=email).first()
            if user:
                newFlash("Email already exists", category="error")
            elif len(email) < 4:
                newFlash("Email must be greater than 3 characters", category="error")
            elif len(username) < 2:
                newFlash("Username must be greater than 1 character", category="error")
            elif password != check_password:
                newFlash("Passwords don't match", category="error")
            elif len(password) < 7:
                newFlash("Password must be at least 7 characters", category="error")

            else:
                new_user = User(username=username, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'), gateway_tier=False, pro_tier=False)
                db.session.add(new_user)
                db.session.commit()
                newFlash( "User created successfully", category="success")

                return redirect(url_for('views.home'))

    return render_template("signup.html")



@auth_blueprint.route('/billing', methods=['GET'])
@login_required
def billing():
    return render_template("billing.html", user=current_user)