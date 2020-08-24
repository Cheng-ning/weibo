from flask import Blueprint, redirect
from flask import request
from flask import render_template
from flask import session

from libs.orm import db
from user.models import User

user_bp = Blueprint('user', __name__, url_prefix='/user')
user_bp.template_folder = './templates'


@user_bp.route('/register', methods=('PSOT', 'GET'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/user/login')
    else:
        return render_template('register.html')
