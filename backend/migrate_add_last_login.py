#!/usr/bin/env python3
"""
Migration script to add last_login column to existing users
Usage: python migrate_add_last_login.py
"""

from app import create_app, db
from sqlalchemy import text

def migrate_add_last_login():
    app = create_app()

    with app.app_context():
        try:
            # Check if last_login column already exists
            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            if 'last_login' not in columns:
                # Add last_login column
                db.session.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME"))
                db.session.commit()
                print("✅ Successfully added last_login column to users table")
            else:
                print("ℹ️  last_login column already exists")

        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_add_last_login()
