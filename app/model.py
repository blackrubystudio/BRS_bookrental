from flask_login import UserMixin, login_manager
from . import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, Email

#도서 데이터베이스 칼럼 ... 나중에 이미지 파일 추가
class Booklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    author = db.Column(db.String(50))
    kategorie = db.Column(db.String(50))
    status = db.Column(db.String(50))
    date = db.Column(db.String(50))

#사용자 데이터베이스 칼럼 ... 슬랙과 연동하는 문제 추후 해결
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

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