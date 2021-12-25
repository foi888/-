from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager #  импорт класс  LoginManager 
from flask_mail import Mail

my_app = Flask(__name__)
my_app.config['SECRET_KEY'] = '12345'
my_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

my_app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
my_app.config['MAIL_PORT'] = 587
my_app.config['MAIL_USE_TLS'] = True
my_app.config['MAIL_USERNAME'] = 'flaskmicroblog63@gmail.com'
my_app.config['MAIL_DEFAULT_SENDER'] = 'flaskmicroblog63@gmail.com'
my_app.config['MAIL_PASSWORD'] = 'Flaskmicroblog123'

mail = Mail(my_app)

db = SQLAlchemy(my_app) # db  - database объект БД
migrate = Migrate(my_app, db) 
login_manager = LoginManager(my_app) # объект login_manager, в котором функции и свойства для системы авторизации
login_manager.login_view = 'login'


from app import routes

