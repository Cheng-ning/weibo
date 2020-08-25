import datetime

from flask import Blueprint, redirect
from flask import request
from flask import render_template
from flask import session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from libs.orm import db
from libs.utils import check_password, login_required, make_password, save_avatar
from user.models import User

user_bp = Blueprint('user', __name__, url_prefix='/user')
user_bp.template_folder = './templates'


@user_bp.route('/register', methods=('POST', 'GET'))
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password1 = request.form.get('password1','').strip()
        password2 = request.form.get('password2', '').strip()
        gender = request.form.get('gender', '').strip()
        birthday = request.form.get('birthday', '').strip()
        city = request.form.get('city','').strip()
        bio = request.form.get('bio', '').strip()
        now = datetime.datetime.now()

        if not password1 or password1 != password2:
            return render_template('register.html', err='密码不符合要求')

        user = User(username=username, password=make_password(password1), gender=gender,
                    birthday=birthday, city=city, bio=bio, created=now)

        avatar_file = request.files.get('avatar')
        if avatar_file:
            user.avatar = save_avatar(avatar_file)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/user/login')
        except IntegrityError:
            db.session.rollback()
            return render_template('register.html', err='您的昵称已被占用')
    else:
        return render_template('register.html')



@user_bp.route('/login', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()

        #  获取用户
        try:
            user = User.query.filter_by(username=username).one()
        except NoResultFound:
            return render_template('login.html', err='该用户不存在')

        #检查密码
        if check_password(password, user.password):
            session['uid'] = user.id
            session['username'] = user.username
            return redirect('/user/info')
        else:
            return render_template('login.html', err='密码错误')
    else:
        return render_template('login.html')


@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@user_bp.route('/info')
@login_required
def info():
     uid = session['uid']
     user = User.query.get(uid)
     return render_template('info.html', user=user)