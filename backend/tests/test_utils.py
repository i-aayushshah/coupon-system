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

class UtilsTestCase(unittest.TestCase):
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
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_is_valid_coupon_code(self):
        """Test coupon code validation"""
        from app.routes.admin import is_valid_coupon_code

        # Valid codes
        self.assertTrue(is_valid_coupon_code('SAVE20'))
        self.assertTrue(is_valid_coupon_code('SAVE-20'))
        self.assertTrue(is_valid_coupon_code('SAVE20OFF'))
        self.assertTrue(is_valid_coupon_code('ABC123'))

        # Invalid codes
        self.assertFalse(is_valid_coupon_code('SA'))  # Too short
        self.assertFalse(is_valid_coupon_code('SAVE20SAVE20SAVE20SAVE20'))  # Too long
        self.assertFalse(is_valid_coupon_code('SAVE 20'))  # Contains space
        self.assertFalse(is_valid_coupon_code('SAVE_20'))  # Contains underscore
        self.assertFalse(is_valid_coupon_code(''))  # Empty

    def test_is_valid_date_range(self):
        """Test date range validation"""
        from app.routes.admin import is_valid_date_range

        # Valid date ranges
        start_date = '2024-01-01'
        end_date = '2024-12-31'
        self.assertTrue(is_valid_date_range(start_date, end_date))

        # Invalid date ranges
        self.assertFalse(is_valid_date_range('2024-12-31', '2024-01-01'))  # End before start
        self.assertFalse(is_valid_date_range('invalid-date', '2024-12-31'))  # Invalid start date
        self.assertFalse(is_valid_date_range('2024-01-01', 'invalid-date'))  # Invalid end date
        self.assertFalse(is_valid_date_range('', '2024-12-31'))  # Empty start date
        self.assertFalse(is_valid_date_range('2024-01-01', ''))  # Empty end date

    def test_is_valid_discount(self):
        """Test discount validation"""
        from app.routes.admin import is_valid_discount

        # Valid percentage discounts
        self.assertTrue(is_valid_discount('percentage', 10))
        self.assertTrue(is_valid_discount('percentage', 50))
        self.assertTrue(is_valid_discount('percentage', 100))

        # Valid fixed amount discounts
        self.assertTrue(is_valid_discount('fixed', 5))
        self.assertTrue(is_valid_discount('fixed', 25))
        self.assertTrue(is_valid_discount('fixed', 100))

        # Invalid discounts
        self.assertFalse(is_valid_discount('percentage', -10))  # Negative percentage
        self.assertFalse(is_valid_discount('percentage', 150))  # Percentage > 100
        self.assertFalse(is_valid_discount('fixed', -5))  # Negative fixed amount
        self.assertFalse(is_valid_discount('invalid', 10))  # Invalid discount type

    def test_parse_date_string(self):
        """Test date string parsing"""
        from app.routes.admin import parse_date_string

        # Valid date strings
        date1 = parse_date_string('2024-01-01')
        self.assertEqual(date1.year, 2024)
        self.assertEqual(date1.month, 1)
        self.assertEqual(date1.day, 1)

        date2 = parse_date_string('2024-12-31')
        self.assertEqual(date2.year, 2024)
        self.assertEqual(date2.month, 12)
        self.assertEqual(date2.day, 31)

        # Invalid date strings
        with self.assertRaises(ValueError):
            parse_date_string('invalid-date')

        with self.assertRaises(ValueError):
            parse_date_string('2024-13-01')  # Invalid month

        with self.assertRaises(ValueError):
            parse_date_string('2024-01-32')  # Invalid day

    def test_is_valid_product_data(self):
        """Test product data validation"""
        from app.routes.admin import is_valid_product_data

        # Valid product data
        valid_data = {
            'name': 'Test Product',
            'price': 100.0,
            'category': 'Electronics',
            'brand': 'Test Brand',
            'sku': 'TEST001',
            'stock_quantity': 10
        }
        self.assertTrue(is_valid_product_data(valid_data))

        # Invalid product data - missing required fields
        invalid_data1 = {
            'name': 'Test Product',
            'price': 100.0
            # Missing category
        }
        self.assertFalse(is_valid_product_data(invalid_data1))

        # Invalid product data - invalid price
        invalid_data2 = {
            'name': 'Test Product',
            'price': -100.0,  # Negative price
            'category': 'Electronics'
        }
        self.assertFalse(is_valid_product_data(invalid_data2))

        # Invalid product data - invalid stock quantity
        invalid_data3 = {
            'name': 'Test Product',
            'price': 100.0,
            'category': 'Electronics',
            'stock_quantity': -5  # Negative stock
        }
        self.assertFalse(is_valid_product_data(invalid_data3))

    def test_coupon_validation_utils(self):
        """Test coupon validation utility functions"""
        # Create test user
        user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            email_verified=True,
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()

        # Test coupon validation with valid data
        valid_coupon_data = {
            'code': 'SAVE20',
            'title': '20% Off',
            'description': 'Get 20% off your purchase',
            'discount_type': 'percentage',
            'discount_value': 20,
            'is_public': True,
            'max_uses': 100,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'minimum_order_value': 50.0,
            'applicable_categories': ['Electronics', 'Clothing'],
            'maximum_discount_amount': 25.0,
            'first_time_user_only': False
        }

        # Test that all validation functions work correctly
        from app.routes.admin import is_valid_coupon_code, is_valid_date_range, is_valid_discount

        self.assertTrue(is_valid_coupon_code(valid_coupon_data['code']))
        self.assertTrue(is_valid_date_range(valid_coupon_data['start_date'], valid_coupon_data['end_date']))
        self.assertTrue(is_valid_discount(valid_coupon_data['discount_type'], valid_coupon_data['discount_value']))

    def test_email_validation(self):
        """Test email validation"""
        import re

        def is_valid_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None

        # Valid emails
        self.assertTrue(is_valid_email('test@example.com'))
        self.assertTrue(is_valid_email('user.name@domain.co.uk'))
        self.assertTrue(is_valid_email('test+tag@example.com'))

        # Invalid emails
        self.assertFalse(is_valid_email('invalid-email'))
        self.assertFalse(is_valid_email('test@'))
        self.assertFalse(is_valid_email('@example.com'))
        self.assertFalse(is_valid_email('test@.com'))

    def test_password_validation(self):
        """Test password validation"""
        def is_valid_password(password):
            # At least 8 characters, contains uppercase, lowercase, and number
            if len(password) < 8:
                return False
            if not any(c.isupper() for c in password):
                return False
            if not any(c.islower() for c in password):
                return False
            if not any(c.isdigit() for c in password):
                return False
            return True

        # Valid passwords
        self.assertTrue(is_valid_password('Password123'))
        self.assertTrue(is_valid_password('MySecurePass1'))
        self.assertTrue(is_valid_password('ComplexP@ss1'))

        # Invalid passwords
        self.assertFalse(is_valid_password('short'))  # Too short
        self.assertFalse(is_valid_password('nouppercase123'))  # No uppercase
        self.assertFalse(is_valid_password('NOLOWERCASE123'))  # No lowercase
        self.assertFalse(is_valid_password('NoNumbers'))  # No numbers

    def test_sku_validation(self):
        """Test SKU validation"""
        def is_valid_sku(sku):
            # SKU should be alphanumeric and 3-20 characters
            if not sku:
                return True  # SKU can be empty (auto-generated)
            if len(sku) < 3 or len(sku) > 20:
                return False
            if not sku.replace('-', '').replace('_', '').isalnum():
                return False
            return True

        # Valid SKUs
        self.assertTrue(is_valid_sku('ABC123'))
        self.assertTrue(is_valid_sku('PROD-001'))
        self.assertTrue(is_valid_sku('SKU_123'))
        self.assertTrue(is_valid_sku(''))  # Empty is valid (auto-generated)

        # Invalid SKUs
        self.assertFalse(is_valid_sku('AB'))  # Too short
        self.assertFalse(is_valid_sku('VERY-LONG-SKU-CODE-THAT-EXCEEDS-LIMIT'))  # Too long
        self.assertFalse(is_valid_sku('SKU 123'))  # Contains space
        self.assertFalse(is_valid_sku('SKU@123'))  # Contains special character

    def test_price_validation(self):
        """Test price validation"""
        def is_valid_price(price):
            try:
                price_float = float(price)
                return price_float >= 0
            except (ValueError, TypeError):
                return False

        # Valid prices
        self.assertTrue(is_valid_price('100.00'))
        self.assertTrue(is_valid_price('0.99'))
        self.assertTrue(is_valid_price('0'))
        self.assertTrue(is_valid_price(100.0))

        # Invalid prices
        self.assertFalse(is_valid_price('-100.00'))  # Negative
        self.assertFalse(is_valid_price('invalid'))  # Not a number
        self.assertFalse(is_valid_price(''))  # Empty

    def test_stock_quantity_validation(self):
        """Test stock quantity validation"""
        def is_valid_stock_quantity(quantity):
            try:
                quantity_int = int(quantity)
                return quantity_int >= 0
            except (ValueError, TypeError):
                return False

        # Valid quantities
        self.assertTrue(is_valid_stock_quantity('10'))
        self.assertTrue(is_valid_stock_quantity('0'))
        self.assertTrue(is_valid_stock_quantity(100))

        # Invalid quantities
        self.assertFalse(is_valid_stock_quantity('-5'))  # Negative
        self.assertFalse(is_valid_stock_quantity('invalid'))  # Not a number
        self.assertFalse(is_valid_stock_quantity(''))  # Empty

if __name__ == '__main__':
    unittest.main()
