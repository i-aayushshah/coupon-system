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
from app.routes.auth import bp as auth_bp
from app.routes.admin import bp as admin_bp
from app.routes.coupons import bp as coupons_bp
from app.routes.user import bp as user_bp
from app.routes.products import bp as products_bp
from app.routes.cart import bp as cart_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Configure CORS properly
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    app.register_blueprint(test_db_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(coupons_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)

    @app.route('/')
    def hello():
        return 'Hello, World! (Flask)'
    return app
