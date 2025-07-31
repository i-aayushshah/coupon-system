from app import db, create_app
from sqlalchemy import text

def migrate_add_order_tables():
    app = create_app()
    with app.app_context():
        try:
            # Check if orders table exists
            result = db.session.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='orders'
            """))

            if not result.fetchone():
                # Create orders table
                db.session.execute(text("""
                    CREATE TABLE orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        subtotal NUMERIC(10, 2) NOT NULL,
                        discount_amount NUMERIC(10, 2) DEFAULT 0,
                        final_total NUMERIC(10, 2) NOT NULL,
                        coupon_code_used VARCHAR(50),
                        coupon_id INTEGER,
                        order_status VARCHAR(20) DEFAULT 'pending',
                        shipping_address TEXT,
                        payment_method VARCHAR(50),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (coupon_id) REFERENCES coupons (id)
                    )
                """))
                print('Successfully created orders table.')
            else:
                print('orders table already exists.')

            # Check if order_items table exists
            result = db.session.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='order_items'
            """))

            if not result.fetchone():
                # Create order_items table
                db.session.execute(text("""
                    CREATE TABLE order_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        unit_price NUMERIC(10, 2) NOT NULL,
                        line_total NUMERIC(10, 2) NOT NULL,
                        FOREIGN KEY (order_id) REFERENCES orders (id),
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                """))
                print('Successfully created order_items table.')
            else:
                print('order_items table already exists.')

            # Check if redemptions table exists
            result = db.session.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='redemptions'
            """))

            if not result.fetchone():
                # Create redemptions table
                db.session.execute(text("""
                    CREATE TABLE redemptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        coupon_id INTEGER NOT NULL,
                        order_id INTEGER NOT NULL,
                        redeemed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        discount_applied NUMERIC(10, 2) NOT NULL,
                        original_amount NUMERIC(10, 2) NOT NULL,
                        discount_amount NUMERIC(10, 2) NOT NULL,
                        final_amount NUMERIC(10, 2) NOT NULL,
                        products_applied_to TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (coupon_id) REFERENCES coupons (id),
                        FOREIGN KEY (order_id) REFERENCES orders (id)
                    )
                """))
                print('Successfully created redemptions table.')
            else:
                print('redemptions table already exists.')

            db.session.commit()
            print('Migration completed successfully!')

        except Exception as e:
            print(f'Error during migration: {str(e)}')
            db.session.rollback()

if __name__ == '__main__':
    migrate_add_order_tables()
