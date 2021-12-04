import re
from typing import Coroutine
from app import my_app
from datetime import date
from flask import render_template, request, flash, redirect, url_for
from app import utils
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from app import db
from datetime import datetime

@my_app.route('/')
@my_app.route('/index') # маршруты
@login_required
def index():  # функция представления
    return render_template('index.html', current_date=date.today())


@my_app.route('/generator', methods=['get', 'post']) # маршруты
def generator():  # функция представления
    if request.method == 'POST':
        form = request.form
        use_numbers = form.get('use_numbers') 
        use_letters = form.get('use_letters')
        use_signs = form.get('use_signs') 
        pass_len = int(form.get('pass_len'))
        password = utils.generate_pass(pass_len, use_numbers, use_letters, use_signs)
        flash(password)
    return render_template('generator.html')


@my_app.route('/login', methods=['post', 'get'])
def login():
    if current_user.is_authenticated: # если пользователь авторизован 
        return redirect(url_for('index')) # перенаправляем на главную 

    if request.method == 'POST': # если пришел запрос POST - значит пользователь отправил форму
        form = request.form # форма
        inputed_username = form.get('user_name') # введеный username
        inputed_password = form.get('user_password') # введеный password
        remember_me = bool(form.get('remember')) 

        user = User.query.filter_by(user_name=inputed_username).first() # пробуем найти пользователя в БД. Если пользователь не найден, то user == None
        if user is not None and user.check_password(inputed_password): # если пользователь существует и пароль верен
            login_user(user, remember=remember_me) # авторизовываем пользователя
            return redirect(url_for('index'))
        else:
            # TODO flashmessages
            return redirect(url_for('login'))  # перенаправляем пользователя на страницу с логином 

            # TODO redirect to requested page (next)
    elif request.method == 'GET':
        return render_template('login.html')


@my_app.route('/logout') 
def logout():
    logout_user()
    return redirect(url_for('index'))

@my_app.route('/register', methods=['get', 'post'])
def register():
    if current_user.is_authenticated: # если пользователь авторизован 
        return redirect(url_for('index'))
    if request.method == 'POST': # если пользователь что-то отправил на сервер (форму)
        form = request.form # форма
        inputed_username = form.get('user_name') # введеный username
        inputed_password = form.get('user_password') # введеный password
        inputed_email = form.get('email')
        user = User(user_name=inputed_username, email=inputed_email)
        user.set_password(inputed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('register.html')

@my_app.route('/user/<requested_username>')  # requested_user_name - запрашиваемое имя пользователя
def user(requested_username):
    user_from_db = User.query.filter_by(user_name=requested_username).first_or_404()   # ищем пользователя. либо нашли, либо 404 (если не найден)
    posts = [
        {'author': user_from_db, 'text': 'Test post #1'},
        {'author': user_from_db, 'text': 'Test post #2'}
    ]
    return render_template('user.html', user=user_from_db, posts=posts)


@my_app.before_request
def for_every_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow().replace(microsecond=0)
        db.session.commit()

@my_app.route('/edit_profile', methods=['post', 'get'])
def edit_profile():
    if request.method == 'GET':
        return render_template('edit.html')
    if request.method == 'POST':
        form = request.form
        new_username = form.get('user_name')
        new_info = form.get('info')

        if new_username is not None and ' ' not in new_username.strip():
            current_user.user_name = new_username
        current_user.info = new_info
        db.session.commit()
        return redirect(url_for('user', requested_username=current_user.user_name))
 

@my_app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@my_app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@my_app.route('/add_post', methods=['get','post'])
def add_post():
    if request.method == 'GET':
        return render_template('add_post.html')
    if request.method == 'POST':
        form = request.form
        post_text = form.get ('text') # TODO validate post text
        new_post = Post(text=post_text, author = current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))