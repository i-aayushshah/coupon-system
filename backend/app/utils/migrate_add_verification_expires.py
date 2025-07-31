from app import db, create_app
from sqlalchemy import text

def migrate_add_verification_expires():
    app = create_app()
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('users')
                WHERE name='email_verification_expires'
            """))

            if result.scalar() == 0:
                # Add the new column
                db.session.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN email_verification_expires DATETIME
                """))
                db.session.commit()
                print('Successfully added email_verification_expires column to users table.')
            else:
                print('email_verification_expires column already exists.')

        except Exception as e:
            print(f'Error during migration: {str(e)}')
            db.session.rollback()

if __name__ == '__main__':
    migrate_add_verification_expires()
