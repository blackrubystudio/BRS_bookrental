import random as r
from flask_login import UserMixin
from . import db, login_manager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, Email
from urllib.parse import urlencode

#도서 데이터베이스 칼럼 ... 나중에 이미지 파일 추가
class Booklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    author = db.Column(db.String(50))
    kategorie = db.Column(db.String(50))
    status = db.Column(db.String(50))
    date = db.Column(db.String(50))

    def __repr__(self):
        return '<Book {}>'.format(self.name)

#사용자 데이터베이스 칼럼 ... 슬랙과 연동하는 문제 추후 해결
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True)
    user_name = db.Column(db.String(50))
    temp_access_code = db.Column(db.String(200), default=None)

    def __repr__(self):
        return '<User {}>'.format(self.user_name)

    def genarate_access_code(self):
        access_code = ''
        random_str_seq = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

        for i in range(0, 16):
            access_code += str(random_str_seq[r.randint(0, len(random_str_seq) - 1)])

        self.temp_access_code = access_code
        db.session.add(self)
        db.session.commit()

        return access_code

    def save_user(query):
        new_user = User(
            user_id=query['user_id'],
            user_name=query['user_name']
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def update_user(self, query):
        self.user_id = query['user_id']
        self.user_name = query['user_name']
        db.session.add(self)
        db.session.commit()
        return self

    def get_access_code(query):
        user = User.query.filter_by(user_id=query['user_id'], user_name=query['user_name']).first()
        if user is None:
            new_user = User.save_user(query)
            access_code = new_user.genarate_access_code()
            return access_code
        else:
            user = user.update_user(query=query)
            access_code = user.genarate_access_code()
            return access_code

    def reset_access_code(self):
        self.temp_access_code = None
        db.session.add(self)
        db.session.commit()
        return self

# 로그인 기능
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):  # 로그인 화면 구성
    username = StringField('username', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):  # 가입 화면 구성
    email = StringField('email', validators=[InputRequired(), Email(message='Invaild email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])