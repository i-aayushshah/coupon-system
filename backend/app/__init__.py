from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()  # Shared DB instance
jwt = JWTManager()
mail = Mail()

from app.models import * # Imported at module level to resolve SyntaxError
from app.routes.test_db import bp as test_db_bp
from app.routes.auth import bp as auth_bp # New: Registered auth blueprint
from app.routes.admin import bp as admin_bp # New: Registered admin blueprint
from app.routes.coupons import bp as coupons_bp # New: Registered coupons blueprint
from app.routes.user import bp as user_bp # New: Registered user blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    app.register_blueprint(test_db_bp)
    app.register_blueprint(auth_bp) # New: Registered auth blueprint
    app.register_blueprint(admin_bp) # New: Registered admin blueprint
    app.register_blueprint(coupons_bp) # New: Registered coupons blueprint
    app.register_blueprint(user_bp) # New: Registered user blueprint

    @app.route('/')
    def hello():
        return 'Hello, World! (Flask)'
    return app
