from flask import Blueprint, render_template
from flask_login import login_required

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST'])
def login():
    pass


@auth_blueprint.route('/logout')
@login_required
def logout():
    pass

@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    pass

@auth_blueprint.route('/billing', methods=['POST'])
@login_required
def billing():
    pass