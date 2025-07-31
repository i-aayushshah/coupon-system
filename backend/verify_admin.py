#!/usr/bin/env python3
"""
Script to verify admin user exists in the database
Usage: python verify_admin.py
"""

from app import create_app, db
from app.models import User

def verify_admin_user():
    app = create_app()

    with app.app_context():
        # Check if admin user exists
        admin_user = User.query.filter_by(email='aayushshah714@gmail.com').first()

        if admin_user:
            print("✅ Admin user found!")
            print(f"ID: {admin_user.id}")
            print(f"Email: {admin_user.email}")
            print(f"Username: {admin_user.username}")
            print(f"First Name: {admin_user.first_name}")
            print(f"Last Name: {admin_user.last_name}")
            print(f"Is Admin: {admin_user.is_admin}")
            print(f"Email Verified: {admin_user.email_verified}")
            print(f"Created At: {admin_user.created_at}")
            print(f"Updated At: {admin_user.updated_at}")
        else:
            print("❌ Admin user not found!")
            print("Please run 'python create_admin.py' to create the admin user.")

if __name__ == '__main__':
    verify_admin_user()
