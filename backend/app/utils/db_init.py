from app import db, create_app
from app.models import User, Coupon, Redemption
from flask import current_app


def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print('Database and tables created.')


def drop_db():
    app = create_app()
    with app.app_context():
        db.drop_all()
        print('Database and tables dropped.')


def migrate_db():
    # For simplicity, just re-create all tables (not for production use)
    drop_db()
    init_db()
