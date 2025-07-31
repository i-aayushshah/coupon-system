from app import db, create_app
from sqlalchemy import text

def migrate_fix_redemptions_table():
    app = create_app()
    with app.app_context():
        try:
            # Check if order_id column exists in redemptions table
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('redemptions')
                WHERE name='order_id'
            """))

            if result.scalar() == 0:
                # Add order_id column
                db.session.execute(text("""
                    ALTER TABLE redemptions
                    ADD COLUMN order_id INTEGER
                """))
                print('Successfully added order_id column to redemptions table.')
            else:
                print('order_id column already exists in redemptions table.')

            # Check if original_amount column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('redemptions')
                WHERE name='original_amount'
            """))

            if result.scalar() == 0:
                # Add original_amount column
                db.session.execute(text("""
                    ALTER TABLE redemptions
                    ADD COLUMN original_amount NUMERIC(10, 2)
                """))
                print('Successfully added original_amount column to redemptions table.')
            else:
                print('original_amount column already exists in redemptions table.')

            # Check if discount_amount column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('redemptions')
                WHERE name='discount_amount'
            """))

            if result.scalar() == 0:
                # Add discount_amount column
                db.session.execute(text("""
                    ALTER TABLE redemptions
                    ADD COLUMN discount_amount NUMERIC(10, 2)
                """))
                print('Successfully added discount_amount column to redemptions table.')
            else:
                print('discount_amount column already exists in redemptions table.')

            # Check if final_amount column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('redemptions')
                WHERE name='final_amount'
            """))

            if result.scalar() == 0:
                # Add final_amount column
                db.session.execute(text("""
                    ALTER TABLE redemptions
                    ADD COLUMN final_amount NUMERIC(10, 2)
                """))
                print('Successfully added final_amount column to redemptions table.')
            else:
                print('final_amount column already exists in redemptions table.')

            # Check if products_applied_to column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('redemptions')
                WHERE name='products_applied_to'
            """))

            if result.scalar() == 0:
                # Add products_applied_to column
                db.session.execute(text("""
                    ALTER TABLE redemptions
                    ADD COLUMN products_applied_to TEXT
                """))
                print('Successfully added products_applied_to column to redemptions table.')
            else:
                print('products_applied_to column already exists in redemptions table.')

            db.session.commit()
            print('Redemptions table migration completed successfully!')

        except Exception as e:
            print(f'Error during migration: {str(e)}')
            db.session.rollback()

if __name__ == '__main__':
    migrate_fix_redemptions_table()
