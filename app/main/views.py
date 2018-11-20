from . import main
from ..model import LoginForm, RegisterForm, User, Booklist, db
from flask import render_template, redirect, url_for, request
from flask_login import login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

@main.route('/', methods=['GET', 'POST'])  # 로그인 페이지
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))
        return '이름이나 비밀번호를 다시 확인해 주세요'
    return render_template('login.html', form=form)


@main.route('/signup', methods=['GET', 'POST'])  # 가입페이지
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@main.route('/logout')  # 로그아웃
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# page route
@main.route('/home')  # 로그인 후 첫 페이지
@login_required  # 로그인한 사용자만 접근 가능능
def index():
    return render_template('index.html', name=current_user.username)


@main.route('/mypage')  # 마이페이지
@login_required  ##로그인한 사용자만 들어갈 수 있게 설정
def mypage():
    return render_template('mypage.html')


@main.route('/add')  # 도서등록페이지
def add():
    return render_template('add.html')


@main.route('/addbook', methods=['POST'])  # 등록한 도서를 데이터 베이스에 추가
def addbook():
    name = request.form['name']
    author = request.form['author']
    kategorie = request.form['kategorie']
    status = request.form['status']
    date = request.form['date']

    booklist = Booklist(name=name, author=author, kategorie=kategorie, status=status, date=date)

    db.session.add(booklist)
    db.session.commit()

    return redirect(url_for('add'))


@main.route('/search', methods=['POST'])  # 검색 도서 목록
def search():
    book = request.form['book']
    lists = Booklist.query.filter(Booklist.name.like('%%%s%%' % book)).all()
    return render_template('table.html', lists=lists, name=current_user.username)


@main.route('/table')  # 도서 목록 페이지
def table():
    lists = Booklist.query.all()
    return render_template('table.html', lists=lists, name=current_user.username)


@main.route('/table2')  # 대출 가능 목록 페이지
def table2():
    lists = Booklist.query.filter_by(status='대출가능').all()
    return render_template('table.html', lists=lists, name=current_user.username)