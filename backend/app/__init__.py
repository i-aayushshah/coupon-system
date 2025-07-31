from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

from app.models import *  # <-- Import models at module level

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    from app.routes.test_db import bp as test_db_bp
    app.register_blueprint(test_db_bp)

    @app.route('/')
    def hello():
        return 'Hello, World! (Flask)'
    return app
