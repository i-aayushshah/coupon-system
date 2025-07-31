#!/usr/bin/env python3
"""
Script to create an admin user in the database
Usage: python create_admin.py
"""

import bcrypt
from app import create_app, db
from app.models import User
from datetime import datetime

def create_admin_user():
    app = create_app()

    with app.app_context():
        # Check if admin user already exists
        existing_user = User.query.filter_by(email='aayushshah714@gmail.com').first()
        if existing_user:
            print(f"Admin user already exists with ID: {existing_user.id}")
            if existing_user.is_admin:
                print("User is already an admin!")
            else:
                existing_user.is_admin = True
                db.session.commit()
                print("User is now an admin!")
            return existing_user

        # Create new admin user
        password = 'Aayush_123!'
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        admin_user = User(
            username='aayushshah',
            email='aayushshah714@gmail.com',
            password_hash=password_hash,
            first_name='Aayush',
            last_name='Shah',
            is_admin=True,
            email_verified=True,  # Skip email verification for admin
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(admin_user)
        db.session.commit()

        print(f"Admin user created successfully!")
        print(f"ID: {admin_user.id}")
        print(f"Email: {admin_user.email}")
        print(f"Username: {admin_user.username}")
        print(f"Is Admin: {admin_user.is_admin}")
        print(f"Email Verified: {admin_user.email_verified}")

        return admin_user

if __name__ == '__main__':
    create_admin_user()
