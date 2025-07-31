import unittest
import json
import tempfile
import os
from app import create_app, db
from app.models.user import User
from app.models.coupon import Coupon
from app.models.redemption import Redemption
from app.models.product import Product
from app.models.order import Order, OrderItem
import datetime

class CouponTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and create test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.db_path}',
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret'
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test user and admin
        self.create_test_user()
        self.create_test_admin()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def create_test_user(self):
        """Create a test user"""
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
        self.user = user

    def create_test_admin(self):
        """Create a test admin user"""
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
        self.admin = admin

    def get_auth_token(self, user):
        """Get authentication token for a user"""
        login_data = {
            'email': user.email,
            'password': 'Password123' if user.username == 'testuser' else 'Admin123'
        }
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        data = json.loads(response.data)
        return data['access_token']

    def test_create_coupon_success(self):
        """Test successful coupon creation by admin"""
        token = self.get_auth_token(self.admin)
        headers = {'Authorization': f'Bearer {token}'}

        data = {
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

        response = self.client.post('/api/admin/coupons',
                                  data=json.dumps(data),
                                  content_type='application/json',
                                  headers=headers)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('coupon', response_data)
        self.assertEqual(response_data['coupon']['code'], 'SAVE20')

    def test_create_coupon_unauthorized(self):
        """Test coupon creation without admin privileges"""
        token = self.get_auth_token(self.user)
        headers = {'Authorization': f'Bearer {token}'}

        data = {
            'code': 'SAVE20',
            'title': '20% Off',
            'description': 'Get 20% off your purchase',
            'discount_type': 'percentage',
            'discount_value': 20,
            'is_public': True,
            'max_uses': 100,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }

        response = self.client.post('/api/admin/coupons',
                                  data=json.dumps(data),
                                  content_type='application/json',
                                  headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_create_coupon_invalid_data(self):
        """Test coupon creation with invalid data"""
        token = self.get_auth_token(self.admin)
        headers = {'Authorization': f'Bearer {token}'}

        data = {
            'code': 'SAVE20',
            'title': '',
            'description': '',
            'discount_type': 'invalid',
            'discount_value': -10,
            'is_public': True,
            'max_uses': -1,
            'start_date': 'invalid-date',
            'end_date': '2024-01-01'
        }

        response = self.client.post('/api/admin/coupons',
                                  data=json.dumps(data),
                                  content_type='application/json',
                                  headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_list_coupons(self):
        """Test listing coupons"""
        token = self.get_auth_token(self.admin)
        headers = {'Authorization': f'Bearer {token}'}

        # Create a test coupon
        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2024, 12, 31),
            created_by=self.admin.id
        )
        db.session.add(coupon)
        db.session.commit()

        response = self.client.get('/api/admin/coupons', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('coupons', data)
        self.assertEqual(len(data['coupons']), 1)

    def test_get_coupon(self):
        """Test getting a specific coupon"""
        token = self.get_auth_token(self.admin)
        headers = {'Authorization': f'Bearer {token}'}

        # Create a test coupon
        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2024, 12, 31),
            created_by=self.admin.id
        )
        db.session.add(coupon)
        db.session.commit()

        response = self.client.get(f'/api/admin/coupons/{coupon.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('coupon', data)
        self.assertEqual(data['coupon']['code'], 'SAVE20')

    def test_update_coupon(self):
        """Test updating a coupon"""
        token = self.get_auth_token(self.admin)
        headers = {'Authorization': f'Bearer {token}'}

        # Create a test coupon
        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2024, 12, 31),
            created_by=self.admin.id
        )
        db.session.add(coupon)
        db.session.commit()

        # Update the coupon
        update_data = {
            'title': 'Updated 20% Off',
            'description': 'Updated description',
            'discount_value': 25
        }

        response = self.client.put(f'/api/admin/coupons/{coupon.id}',
                                  data=json.dumps(update_data),
                                  content_type='application/json',
                                  headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['coupon']['title'], 'Updated 20% Off')

    def test_delete_coupon(self):
        """Test deleting a coupon"""
        token = self.get_auth_token(self.admin)
        headers = {'Authorization': f'Bearer {token}'}

        # Create a test coupon
        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2024, 12, 31),
            created_by=self.admin.id
        )
        db.session.add(coupon)
        db.session.commit()

        response = self.client.delete(f'/api/admin/coupons/{coupon.id}', headers=headers)
        self.assertEqual(response.status_code, 200)

        # Verify coupon is deleted
        response = self.client.get(f'/api/admin/coupons/{coupon.id}', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_public_coupons(self):
        """Test getting public coupons"""
        # Create a public coupon
        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2024, 12, 31),
            created_by=self.admin.id
        )
        db.session.add(coupon)
        db.session.commit()

        response = self.client.get('/api/coupons/public')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('coupons', data)
        self.assertEqual(len(data['coupons']), 1)

    def test_validate_coupon(self):
        """Test coupon validation"""
        # Create a test coupon
        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2024, 12, 31),
            created_by=self.admin.id
        )
        db.session.add(coupon)
        db.session.commit()

        response = self.client.get(f'/api/coupons/validate/{coupon.code}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('valid', data)
        self.assertTrue(data['valid'])

    def test_validate_invalid_coupon(self):
        """Test validation of invalid coupon"""
        response = self.client.get('/api/coupons/validate/INVALID')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('valid', data)
        self.assertFalse(data['valid'])

    def test_redeem_coupon(self):
        """Test coupon redemption"""
        token = self.get_auth_token(self.user)
        headers = {'Authorization': f'Bearer {token}'}

        # Create a test coupon
        coupon = Coupon(
            code='SAVE20',
            title='20% Off',
            description='Get 20% off your purchase',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2024, 12, 31),
            created_by=self.admin.id
        )
        db.session.add(coupon)
        db.session.commit()

        # Create a test product
        product = Product(
            name='Test Product',
            description='Test product description',
            price=100.0,
            category='Electronics',
            brand='Test Brand',
            sku='TEST001',
            stock_quantity=10,
            created_by=self.admin.id
        )
        db.session.add(product)
        db.session.commit()

        # Create a test order
        order = Order(
            user_id=self.user.id,
            total_amount=100.0,
            status='pending',
            shipping_address='Test Address'
        )
        db.session.add(order)
        db.session.commit()

        # Redeem coupon
        redemption_data = {
            'coupon_code': 'SAVE20',
            'order_id': order.id
        }

        response = self.client.post('/api/coupons/redeem',
                                  data=json.dumps(redemption_data),
                                  content_type='application/json',
                                  headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('redemption', data)

    def test_search_coupons(self):
        """Test coupon search"""
        # Create test coupons
        coupon1 = Coupon(
            code='SAVE20',
            title='20% Off Electronics',
            description='Get 20% off electronics',
            discount_type='percentage',
            discount_value=20,
            is_public=True,
            max_uses=100,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2024, 12, 31),
            created_by=self.admin.id
        )
        coupon2 = Coupon(
            code='SAVE10',
            title='10% Off Clothing',
            description='Get 10% off clothing',
            discount_type='percentage',
            discount_value=10,
            is_public=True,
            max_uses=50,
            start_date=datetime.datetime(2024, 1, 1),
            end_date=datetime.datetime(2024, 12, 31),
            created_by=self.admin.id
        )
        db.session.add_all([coupon1, coupon2])
        db.session.commit()

        response = self.client.get('/api/coupons/search?q=Electronics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('coupons', data)
        self.assertEqual(len(data['coupons']), 1)

if __name__ == '__main__':
    unittest.main()
