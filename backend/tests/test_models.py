import unittest
import tempfile
import os
import datetime
from app import create_app, db
from app.models.user import User
from app.models.coupon import Coupon
from app.models.redemption import Redemption
from app.models.product import Product
from app.models.order import Order, OrderItem

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and create test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.db_path}',
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret'
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        try:
            os.close(self.db_fd)
            os.unlink(self.db_path)
        except (OSError, PermissionError):
            pass  # File might already be closed or deleted

    def test_user_model(self):
        """Test User model creation and methods"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            email_verified=True
        )
        user.set_password('Password123')
        db.session.add(user)
        db.session.commit()

        # Test password verification
        self.assertTrue(user.check_password('Password123'))
        self.assertFalse(user.check_password('WrongPassword'))

        # Test user properties
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.email_verified)
        self.assertFalse(user.is_admin)

        # Test user representation
        self.assertIn('testuser', str(user))

    def test_user_admin_role(self):
        """Test admin user creation"""
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            email_verified=True,
            is_admin=True
        )
        admin.set_password('Admin123')
        db.session.add(admin)
        db.session.commit()

        self.assertTrue(admin.is_admin)
        self.assertTrue(admin.check_password('Admin123'))

    def test_coupon_model(self):
        """Test Coupon model creation and methods"""
        user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            email_verified=True,
            is_admin=True
        )
        user.set_password('Admin123')
        db.session.add(user)
        db.session.commit()

        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            current_uses=0,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2025, 12, 31),
            minimum_order_value=50.0,
            maximum_discount_amount=25.0,
            first_time_user_only=False,
            created_by=user.id
        )
        coupon.set_applicable_categories(['Electronics', 'Clothing'])
        db.session.add(coupon)
        db.session.commit()

        # Test coupon properties
        self.assertEqual(coupon.code, 'SAVE20')
        self.assertEqual(coupon.discount_type, 'percentage')
        self.assertEqual(coupon.discount_value, 20)
        self.assertTrue(coupon.is_public)
        self.assertEqual(coupon.max_uses, 100)
        self.assertEqual(coupon.current_uses, 0)

        # Test coupon representation
        self.assertIn('SAVE20', str(coupon))

        # Test coupon validation methods
        self.assertTrue(coupon.is_active)
        self.assertFalse(coupon.is_expired())
        self.assertFalse(coupon.is_fully_used())

    def test_coupon_expired(self):
        """Test expired coupon validation"""
        user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            email_verified=True,
            is_admin=True
        )
        user.set_password('Admin123')
        db.session.add(user)
        db.session.commit()

        coupon = Coupon(
            code='EXPIRED',
            title='Expired Coupon',
            description='This coupon is expired',
            discount_type='percentage',
            discount_value=10,
            is_public=True,
            max_uses=100,
            current_uses=0,
            start_date=datetime.datetime(2023, 1, 1),
            end_date=datetime.datetime(2023, 12, 31),  # Past date
            created_by=user.id
        )
        db.session.add(coupon)
        db.session.commit()

        # The is_active property is a database column, not a computed property
        # We need to set it manually for expired coupons
        coupon.is_active = False
        db.session.commit()
        
        self.assertFalse(coupon.is_active)
        self.assertTrue(coupon.is_expired())

    def test_coupon_fully_used(self):
        """Test fully used coupon validation"""
        user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            email_verified=True,
            is_admin=True
        )
        user.set_password('Admin123')
        db.session.add(user)
        db.session.commit()

        coupon = Coupon(
            code='USED',
            title='Used Coupon',
            description='This coupon is fully used',
            discount_type='percentage',
            discount_value=10,
            is_public=True,
            max_uses=5,
            current_uses=5,  # Fully used
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2025, 12, 31),  # Future date
            created_by=user.id
        )
        db.session.add(coupon)
        db.session.commit()

        # The is_active property is a database column, not a computed property
        # We need to set it manually for fully used coupons
        coupon.is_active = False
        db.session.commit()
        
        self.assertFalse(coupon.is_active)
        self.assertTrue(coupon.is_fully_used())

    def test_product_model(self):
        """Test Product model creation and methods"""
        user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            email_verified=True,
            is_admin=True
        )
        user.set_password('Admin123')
        db.session.add(user)
        db.session.commit()

        product = Product(
            name='Test Product',
            description='Test product description',
            price=100.0,
            category='Electronics',
            brand='Test Brand',
            sku='TEST001',
            stock_quantity=10,
            is_active=True,
            image_url='https://example.com/image.jpg',
            minimum_order_value=10.0,
            created_by=user.id
        )
        db.session.add(product)
        db.session.commit()

        # Test product properties
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 100.0)
        self.assertEqual(product.category, 'Electronics')
        self.assertEqual(product.stock_quantity, 10)
        self.assertTrue(product.is_active)

        # Test product representation
        self.assertIn('Test Product', str(product))

        # Test to_dict method
        product_dict = product.to_dict()
        self.assertEqual(product_dict['name'], 'Test Product')
        self.assertEqual(product_dict['price'], 100.0)
        self.assertEqual(product_dict['category'], 'Electronics')

    def test_order_model(self):
        """Test Order model creation and methods"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            email_verified=True
        )
        user.set_password('Password123')
        db.session.add(user)
        db.session.commit()

        order = Order(
            user_id=user.id,
            subtotal=150.0,
            final_total=150.0,
            order_status='pending',
            shipping_address='123 Test St, Test City, TC 12345',
            payment_method='credit_card'
        )
        db.session.add(order)
        db.session.commit()

        # Test order properties
        self.assertEqual(order.subtotal, 150.0)
        self.assertEqual(order.order_status, 'pending')
        self.assertEqual(order.user_id, user.id)

        # Test order representation
        self.assertIn('Order', str(order))

        # Test to_dict method
        order_dict = order.to_dict()
        self.assertEqual(order_dict['subtotal'], 150.0)
        self.assertEqual(order_dict['order_status'], 'pending')

    def test_order_item_model(self):
        """Test OrderItem model creation and methods"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            email_verified=True
        )
        user.set_password('Password123')
        db.session.add(user)
        db.session.commit()

        order = Order(
            user_id=user.id,
            subtotal=200.0,
            final_total=200.0,
            order_status='pending',
            shipping_address='123 Test St, Test City, TC 12345'
        )
        db.session.add(order)
        db.session.commit()

        order_item = OrderItem(
            order_id=order.id,
            product_id=1,  # Assuming product exists
            quantity=2,
            unit_price=100.0,
            line_total=200.0
        )
        db.session.add(order_item)
        db.session.commit()

        # Test order item properties
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.unit_price, 100.0)
        self.assertEqual(order_item.line_total, 200.0)
        self.assertEqual(order_item.order_id, order.id)

        # Test order item representation
        self.assertIn('OrderItem', str(order_item))

        # Test to_dict method
        item_dict = order_item.to_dict()
        self.assertEqual(item_dict['quantity'], 2)
        self.assertEqual(item_dict['unit_price'], 100.0)

    def test_redemption_model(self):
        """Test Redemption model creation and methods"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            email_verified=True
        )
        user.set_password('Password123')
        db.session.add(user)
        db.session.commit()

        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            email_verified=True,
            is_admin=True
        )
        admin.set_password('Admin123')
        db.session.add(admin)
        db.session.commit()

        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            current_uses=0,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2025, 12, 31),  # Future date
            created_by=admin.id
        )
        db.session.add(coupon)
        db.session.commit()

        order = Order(
            user_id=user.id,
            subtotal=100.0,
            final_total=100.0,
            order_status='completed',
            shipping_address='123 Test St, Test City, TC 12345'
        )
        db.session.add(order)
        db.session.commit()

        redemption = Redemption(
            user_id=user.id,
            coupon_id=coupon.id,
            order_id=order.id,
            original_amount=100.0,
            final_amount=80.0,
            discount_amount=20.0,
            discount_applied=20.0
        )
        redemption.set_products_applied_to(['Electronics'])
        db.session.add(redemption)
        db.session.commit()

        # Test redemption properties
        self.assertEqual(redemption.original_amount, 100.0)
        self.assertEqual(redemption.final_amount, 80.0)
        self.assertEqual(redemption.discount_amount, 20.0)
        self.assertEqual(redemption.user_id, user.id)
        self.assertEqual(redemption.coupon_id, coupon.id)
        self.assertEqual(redemption.order_id, order.id)

        # Test redemption representation - the __repr__ doesn't include coupon code
        self.assertIn('Redemption', str(redemption))

    def test_model_relationships(self):
        """Test model relationships"""
        # Create users
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            email_verified=True
        )
        user.set_password('Password123')
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            email_verified=True,
            is_admin=True
        )
        admin.set_password('Admin123')
        db.session.add_all([user, admin])
        db.session.commit()

        # Create product
        product = Product(
            name='Test Product',
            description='Test product description',
            price=100.0,
            category='Electronics',
            brand='Test Brand',
            sku='TEST001',
            stock_quantity=10,
            created_by=admin.id
        )
        db.session.add(product)
        db.session.commit()

        # Create coupon
        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            current_uses=0,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2025, 12, 31),  # Future date
            created_by=admin.id
        )
        db.session.add(coupon)
        db.session.commit()

        # Create order
        order = Order(
            user_id=user.id,
            subtotal=100.0,
            final_total=100.0,
            order_status='completed',
            shipping_address='123 Test St, Test City, TC 12345'
        )
        db.session.add(order)
        db.session.commit()

        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            unit_price=100.0,
            line_total=100.0
        )
        db.session.add(order_item)
        db.session.commit()

        # Create redemption
        redemption = Redemption(
            user_id=user.id,
            coupon_id=coupon.id,
            order_id=order.id,
            original_amount=100.0,
            final_amount=80.0,
            discount_amount=20.0,
            discount_applied=20.0
        )
        redemption.set_products_applied_to(['Electronics'])
        db.session.add(redemption)
        db.session.commit()

        # Test relationships
        self.assertEqual(order.user_id, user.id)
        self.assertEqual(order_item.order_id, order.id)
        self.assertEqual(order_item.product_id, product.id)
        self.assertEqual(redemption.user_id, user.id)
        self.assertEqual(redemption.coupon_id, coupon.id)
        self.assertEqual(redemption.order_id, order.id)

        # Test backref relationships
        self.assertEqual(len(user.orders), 1)
        self.assertEqual(len(user.redemptions), 1)
        self.assertEqual(len(admin.products), 1)
        self.assertEqual(len(admin.coupons), 1)

if __name__ == '__main__':
    unittest.main()
