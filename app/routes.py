import re
from turtle import pos
from typing import Coroutine
from app import my_app
from datetime import date
from flask import render_template, request, flash, redirect, url_for
from app import utils
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Likes
from app import db
from datetime import datetime
import jwt
import json


@my_app.route('/')
@my_app.route('/index') # маршруты
@login_required
def index():  # функция представления
    all_posts = Post.query.all()
    return render_template('index.html', current_date=date.today(), posts=all_posts)


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
            flash('неверный пароль или логин')
            return redirect(url_for('login'))  # перенаправляем пользователя на страницу с логином 
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
    posts = Post.query.filter_by(author=user_from_db)
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

@my_app.route('/reset_password', methods=['get','post'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('reset_password.html')
    if request.method == 'POST':
        form = request.form
        inputed_email = form.get ('email')
        user = User.query.filter_by(email=inputed_email).first()
        if user is not None: # если пользователь найден
            new_password = utils.generate_pass(8,True,True,True)
            utils.send_password_to_email(new_password,inputed_email,user.user_name)
            user.set_password(new_password)
            db.session.commit()
            return redirect(url_for ('login'))
        else:
            flash('маил ненайден')
            return redirect(url_for('reset_password'))

tokens = []

@my_app.route('/api/login')
def api_login():
    username = request.args['username']
    password = request.args['password']
    user = User.query.filter_by(user_name=username).first()
    if user is not None and user.check_password(password):
        token = jwt.encode({'user_id': user.id, 'avatar': user.get_avatar(128)}, 'my-secret', algorithm='HS256')
        tokens.append (token)
        return json.dumps({
        'token': token,
        'user_data': 
                    {'username': user.user_name, 
                    'avatar': user.get_avatar(128),
                    'id': user.id
                    }
        })   
    else:
        return 'неправельный логин или пароль',400

@my_app.route('/api/register')
def api_register():
    username = request.args['username']
    password = request.args['password']
    email = request.args['email']
    user = User(user_name=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return 'register ok',200

@my_app.route('/api/check_token')
def check_token():
    token = request.args['token']
    print(tokens)
    if token in tokens:   # token = eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo3fQ.nPW-p0Hg803ROeR0kdw7lr_iyONsWsMTMgk0jBSIg0c
        data = jwt.decode(token, 'my-secret', algorithms=['HS256'])
        print(data)
        return 'Token is valid', 200
    else:
        return 'token invalid', 400


@my_app.route('/api/get_posts')
def get_posts():
    page = int(request.args['page'])
    qty = int(request.args['qty'])
    all_posts = Post.query.order_by(Post.time.desc()).paginate(page, qty)
    posts_json = []
    for post in all_posts.items:
        posts_json.append({
            'post_id':post.id,
            'text':post.text,
            'author_id':post.author.id,
            'author_user_name':post.author.user_name,
            'author_avatar':post.author.get_avatar(128),
            'likes_count':post.likes_count,
            'is_liked':bool(Likes.query.filter_by(user_id = request.args['user_id'], post_id=post.id).first())
        })
    return json.dumps(posts_json)

@my_app.route('/api/get_user')  # localhost:5000/api/get_user?user_id=1  - GET запрос
def get_user():
    user_id = request.args['user_id']
    user = User.query.get_or_404(user_id)
    user_posts = [{'post_id': post.id, 'text': post.text, 'timestamp': str(
        post.time), 'likes_count':post.likes_count} for post in Post.query.filter_by(author=user)]
    user_data = {
        'id':user.id,
        'user_name':user.user_name,
        'info':user.info,
        'last_seen':str(user.last_seen),
        'avatar':user.get_avatar(128),
        'posts': user_posts

    }
    return json.dumps(user_data)






@my_app.route('/api/add_post', methods=['POST'])
def api_add_post():
    data = json.loads(request.data)       #  data = {'text':    , 'user_id' }
    post_text = data['text']
    user_id = data['user_id']
    if len(post_text) in range(1,300):
        new_post = Post(text=post_text, author = User.query.get(user_id))
        db.session.add(new_post)
        db.session.commit()
        return 'post added', 200
    else:
        return 'invalid post len', 400

@my_app.route('/api/del_post', methods=['POST'])
def del_post():
    data = json.loads(request.data)
    post_id = data['post_id']
    user_id = data['user_id']
    post = Post.query.get(post_id)
    if post.author.id == int(user_id):
        db.session.delete(post)
        db.session.commit()
        return 'post deleted', 200
    else:
        return 'wrong author', 400

@my_app.route('/api/like', methods=['POST'])
def like():
    data = json.loads(request.data)
    post_id = data['post_id']
    user_id = data['user_id']
    like = Likes.query.filter_by(user_id=user_id, post_id=post_id).first()
    post = Post.query.get(post_id)
    if like is None:
        post.likes_count += 1
        like=Likes(user_id=user_id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
    else:
        current_likes = post.likes_count
        current_likes -= 1
        post.likes_count = current_likes
        db.session.delete(like)
        db.session.commit()
    return json.dumps({'likes_count': post.likes_count, 'is_liked':bool(Likes.query.filter_by(user_id = user_id, post_id=post.id).first()) })




 # {'text': 'hello world'}
