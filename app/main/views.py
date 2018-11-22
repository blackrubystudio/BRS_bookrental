import requests
from . import main
from ..model import LoginForm, RegisterForm, User, Booklist, db
from flask import render_template, redirect, url_for, request, json, Response, current_app
from flask_login import login_required, logout_user, current_user, login_user
from werkzeug.security import check_password_hash, generate_password_hash

@main.route('/slack/', methods=['POST'])
def slack_verify():
    request_json = json.loads(request.data)
    return Response(request_json["challenge"], mimetype='application/x-www-form-urlencoded')

@main.route('/redirect/', methods=['POST'])
def redirect_main():
    token = request.form['token']
    team_id = request.form['team_id']
    query = request.form

    if token == current_app.config['VERIFICATION_TOKEN'] and team_id == current_app.config['TEAM_ID']:
        access_code = User.get_access_code(query)
        redirect_uri = request.url_root + '?access_code=' + access_code
        return redirect_uri
    else:
        return '사용자 인증에 실패 하셨습니다.'

@main.route('/', methods=['GET'])  # 자동 로그인, 인증되지 않을시 noauth로 redirect 한다.
def login():
    access_code = request.args.get('access_code')
    if access_code is None:
        return redirect(url_for('main.no_auth'))

    user = User.query.filter_by(temp_access_code=access_code).first()

    if user is None:
        return redirect(url_for('main.no_auth'))
    else:
        user = user.reset_access_code()
        login_user(user, remember=True)
        return redirect(url_for('main.index'))


@main.route('/noauth', methods=['GET'])  #인증되지 않은 사용자가 접근할때 나오는 페이지
def no_auth():
    return render_template('no_auth.html')


@main.route('/logout')  # 로그아웃
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# page route
@main.route('/home')  # 로그인 후 첫 페이지
@login_required  # 로그인한 사용자만 접근 가능
def index():
    return render_template('index.html', name=current_user.user_name)


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
    return render_template('table.html', lists=lists, name=current_user.user_name)


@main.route('/table')  # 도서 목록 페이지
def table():
    lists = Booklist.query.all()
    return render_template('table.html', lists=lists, name=current_user.user_name)


@main.route('/table2')  # 대출 가능 목록 페이지
def table2():
    lists = Booklist.query.filter_by(status='대출가능').all()
    return render_template('table.html', lists=lists, name=current_user.user_name)