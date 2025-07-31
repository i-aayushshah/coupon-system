from app import db, create_app
from sqlalchemy import text

def migrate_add_coupon_fields():
    app = create_app()
    with app.app_context():
        try:
            # Check if minimum_order_value column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('coupons')
                WHERE name='minimum_order_value'
            """))

            if result.scalar() == 0:
                # Add minimum_order_value column
                db.session.execute(text("""
                    ALTER TABLE coupons
                    ADD COLUMN minimum_order_value NUMERIC(10, 2) DEFAULT 0
                """))
                print('Successfully added minimum_order_value column to coupons table.')
            else:
                print('minimum_order_value column already exists.')

            # Check if applicable_categories column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('coupons')
                WHERE name='applicable_categories'
            """))

            if result.scalar() == 0:
                # Add applicable_categories column
                db.session.execute(text("""
                    ALTER TABLE coupons
                    ADD COLUMN applicable_categories TEXT
                """))
                print('Successfully added applicable_categories column to coupons table.')
            else:
                print('applicable_categories column already exists.')

            # Check if maximum_discount_amount column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('coupons')
                WHERE name='maximum_discount_amount'
            """))

            if result.scalar() == 0:
                # Add maximum_discount_amount column
                db.session.execute(text("""
                    ALTER TABLE coupons
                    ADD COLUMN maximum_discount_amount NUMERIC(10, 2)
                """))
                print('Successfully added maximum_discount_amount column to coupons table.')
            else:
                print('maximum_discount_amount column already exists.')

            # Check if first_time_user_only column exists
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM pragma_table_info('coupons')
                WHERE name='first_time_user_only'
            """))

            if result.scalar() == 0:
                # Add first_time_user_only column
                db.session.execute(text("""
                    ALTER TABLE coupons
                    ADD COLUMN first_time_user_only BOOLEAN DEFAULT 0
                """))
                print('Successfully added first_time_user_only column to coupons table.')
            else:
                print('first_time_user_only column already exists.')

            db.session.commit()
            print('Migration completed successfully!')

        except Exception as e:
            print(f'Error during migration: {str(e)}')
            db.session.rollback()

if __name__ == '__main__':
    migrate_add_coupon_fields()
