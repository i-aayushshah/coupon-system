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

class AuthTestCase(unittest.TestCase):
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

    def test_register_success(self):
        """Test successful user registration"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('Registration successful', data['message'])

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create first user
        data = {
            'username': 'testuser1',
            'email': 'test@example.com',
            'password': 'Password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.client.post('/api/auth/register',
                        data=json.dumps(data),
                        content_type='application/json')

        # Try to register with same email
        data['username'] = 'testuser2'
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 409)

    def test_register_invalid_data(self):
        """Test registration with invalid data"""
        data = {
            'username': 'test',
            'email': 'invalid-email',
            'password': '123',
            'first_name': '',
            'last_name': ''
        }
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        """Test successful login"""
        # Register user first
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.client.post('/api/auth/register',
                        data=json.dumps(data),
                        content_type='application/json')

        # Login
        login_data = {
            'email': 'test@example.com',
            'password': 'Password123'
        }
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Email not verified
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Email not verified', data['error'])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_login_unverified_email(self):
        """Test login with unverified email"""
        # Register user without verification
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.client.post('/api/auth/register',
                        data=json.dumps(data),
                        content_type='application/json')

        # Try to login
        login_data = {
            'email': 'test@example.com',
            'password': 'Password123'
        }
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Email not verified

    def test_verify_email_success(self):
        """Test email verification"""
        # Register user
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(data),
                                  content_type='application/json')

        # Get user from database
        user = User.query.filter_by(email='test@example.com').first()
        verification_token = user.email_verification_token

        # Verify email
        verify_data = {
            'token': verification_token,
            'email': 'test@example.com'
        }
        response = self.client.post('/api/auth/verify-email',
                                  data=json.dumps(verify_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_verify_email_invalid_token(self):
        """Test email verification with invalid token"""
        data = {
            'token': 'invalid-token',
            'email': 'test@example.com'
        }
        response = self.client.post('/api/auth/verify-email',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_resend_verification(self):
        """Test resend verification email"""
        # Register user
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.client.post('/api/auth/register',
                        data=json.dumps(data),
                        content_type='application/json')

        # Resend verification
        resend_data = {
            'email': 'test@example.com'
        }
        response = self.client.post('/api/auth/resend-verification',
                                  data=json.dumps(resend_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_forgot_password(self):
        """Test forgot password request"""
        # Register and verify user
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(data),
                                  content_type='application/json')

        # Get user from database
        user = User.query.filter_by(email='test@example.com').first()
        verification_token = user.email_verification_token
        self.client.post('/api/auth/verify-email',
                        data=json.dumps({'token': verification_token, 'email': 'test@example.com'}),
                        content_type='application/json')

        # Request password reset
        forgot_data = {
            'email': 'test@example.com'
        }
        response = self.client.post('/api/auth/forgot-password',
                                  data=json.dumps(forgot_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_reset_password(self):
        """Test password reset"""
        # Register and verify user
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(data),
                                  content_type='application/json')

        # Get user from database
        user = User.query.filter_by(email='test@example.com').first()
        verification_token = user.email_verification_token
        self.client.post('/api/auth/verify-email',
                        data=json.dumps({'token': verification_token, 'email': 'test@example.com'}),
                        content_type='application/json')

        # Request password reset
        forgot_data = {
            'email': 'test@example.com'
        }
        self.client.post('/api/auth/forgot-password',
                        data=json.dumps(forgot_data),
                        content_type='application/json')

        # Get reset token from database
        user = User.query.filter_by(email='test@example.com').first()
        reset_token = user.password_reset_token

        # Reset password
        reset_data = {
            'token': reset_token,
            'email': 'test@example.com',
            'new_password': 'NewPassword123'
        }
        response = self.client.post('/api/auth/reset-password',
                                  data=json.dumps(reset_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_me_endpoint(self):
        """Test /me endpoint with authentication"""
        # Register and verify user
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(data),
                                  content_type='application/json')

        # Get user from database
        user = User.query.filter_by(email='test@example.com').first()
        verification_token = user.email_verification_token
        self.client.post('/api/auth/verify-email',
                        data=json.dumps({'token': verification_token, 'email': 'test@example.com'}),
                        content_type='application/json')

        # Login to get token
        login_data = {
            'email': 'test@example.com',
            'password': 'Password123'
        }
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        login_response = json.loads(response.data)
        token = login_response['access_token']

        # Test /me endpoint
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/auth/me', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'test@example.com')

    def test_me_endpoint_unauthorized(self):
        """Test /me endpoint without authentication"""
        response = self.client.get('/api/auth/me')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
