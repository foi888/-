from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager #  импорт класс  LoginManager 

my_app = Flask(__name__)
my_app.config['SECRET_KEY'] = '12345'
my_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(my_app) # db  - database объект БД
migrate = Migrate(my_app, db) 
login_manager = LoginManager(my_app) # объект login_manager, в котором функции и свойства для системы авторизации
login_manager.login_view = 'login'


from app import routes

