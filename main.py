from flask import Flask, redirect, render_template
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from article.models import Article
from article.views import article_bp
from libs.orm import db
from user.models import User
from user.views import user_bp

app = Flask(__name__)
app.secret_key = r'zxicojnv90u3nlcnxvp39-vl39(*l31j'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost:3306/weibo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

manager = Manager(app)

db.init_app(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

app.register_blueprint(user_bp)
app.register_blueprint(article_bp)


@app.route('/')
def home():
    """首页"""
    return redirect('/article/index')


@manager.command
def create_test_article():
    users = User.fake_users(50)
    uid_list = [u.id for u in users]
    Article.fake_article(uid_list, 2000)


if __name__ == '__main__':
    manager.run()
