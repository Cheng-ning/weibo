import random

from libs.orm import db
from enum import unique
from libs.utils import random_zh_str


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'unknow'), default='unknow')
    birthday = db.Column(db.Date, default='2000-01-01')
    city = db.Column(db.String(10), default='中国')
    avatar = db.Column(db.String(256), default='/static/img/default.png')
    bio = db.Column(db.Text, default='')
    created = db.Column(db.DateTime, nullable=False)

    @classmethod
    def fake_users(cls, num):
        users =[]
        for i in range(num):
            year = random.randint(2010, 2019)
            month = random.randint(1, 12)
            day = random.randint(1, 28)

            username = random_zh_str(3)
            password = '123546453'
            gender = random.choice(['male', 'female', 'unknow'])
            birthday ='%04d-%02d-%02d' % (year, month, day)
            city = random.choice(['上海','苏州','长沙','哈尔滨','长春','北京'])
            bio = random_zh_str(30)
            created = '2010-02-28'
            user = cls(username=username, password=password, gender=gender,
                       birthday=birthday, city=city, bio=bio, created=created)
