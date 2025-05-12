from flask import Flask, render_template, request, redirect, url_for, flash,session
from config import config
from flask_mysqldb import MySQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf import CSRFProtect
from models.ModelUser import db
from models.init_db import create_default_user

app = Flask(__name__)
app.config.from_object(config['development'])  # Carga la config con SQLALCHEMY_DATABASE_URI



db.init_app(app)

with app.app_context():
    db.create_all()
    create_default_user()