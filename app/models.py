from sqlalchemy.sql.schema import Column
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login_manager
from hashlib import md5
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    info = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_avatar(self, size):
        hashed_email = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{hashed_email}?d=identicon&s={size}'


@login_manager.user_loader # функция-загрузчик, связывает flask-login и пользователей с БД
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = Column(db.Integer, db.ForeignKey('user.id'))
    likes_count = db.Column(db.Integer, default=0)
class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)
