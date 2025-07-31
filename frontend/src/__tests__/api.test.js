import { authAPI, couponAPI, productAPI, cartAPI, adminAPI } from '../utils/api';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  }))
}));

describe('API Services', () => {
  let mockAxios;

  beforeEach(() => {
    mockAxios = require('axios').create();
    jest.clearAllMocks();
  });

  describe('authAPI', () => {
    test('register should make POST request to /api/auth/register', async () => {
      const userData = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'Password123',
        first_name: 'Test',
        last_name: 'User'
      };

      mockAxios.post.mockResolvedValueOnce({ data: { message: 'User registered successfully' } });

      await authAPI.register(userData);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/auth/register', userData);
    });

    test('login should make POST request to /api/auth/login', async () => {
      const loginData = {
        email: 'test@example.com',
        password: 'Password123'
      };

      mockAxios.post.mockResolvedValueOnce({
        data: {
          access_token: 'test-token',
          user: { id: 1, email: 'test@example.com' }
        }
      });

      await authAPI.login(loginData);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/auth/login', loginData);
    });

    test('verifyEmail should make POST request to /api/auth/verify-email', async () => {
      const token = 'test-verification-token';

      mockAxios.post.mockResolvedValueOnce({ data: { message: 'Email verified successfully' } });

      await authAPI.verifyEmail(token);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/auth/verify-email', { token });
    });

    test('resendVerification should make POST request to /api/auth/resend-verification', async () => {
      const email = 'test@example.com';

      mockAxios.post.mockResolvedValueOnce({ data: { message: 'Verification email sent' } });

      await authAPI.resendVerification(email);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/auth/resend-verification', { email });
    });

    test('forgotPassword should make POST request to /api/auth/forgot-password', async () => {
      const email = 'test@example.com';

      mockAxios.post.mockResolvedValueOnce({ data: { message: 'Password reset email sent' } });

      await authAPI.forgotPassword(email);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/auth/forgot-password', { email });
    });

    test('resetPassword should make POST request to /api/auth/reset-password', async () => {
      const resetData = {
        token: 'test-reset-token',
        new_password: 'NewPassword123'
      };

      mockAxios.post.mockResolvedValueOnce({ data: { message: 'Password reset successfully' } });

      await authAPI.resetPassword(resetData);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/auth/reset-password', resetData);
    });

    test('me should make GET request to /api/auth/me', async () => {
      mockAxios.get.mockResolvedValueOnce({
        data: {
          user: { id: 1, email: 'test@example.com' }
        }
      });

      await authAPI.me();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/auth/me');
    });
  });

  describe('couponAPI', () => {
    test('getPublicCoupons should make GET request to /api/coupons/public', async () => {
      mockAxios.get.mockResolvedValueOnce({
        data: {
          coupons: [
            { id: 1, code: 'SAVE20', title: '20% Off' }
          ]
        }
      });

      await couponAPI.getPublicCoupons();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/coupons/public');
    });

    test('validateCoupon should make GET request to /api/coupons/validate/:code', async () => {
      const code = 'SAVE20';

      mockAxios.get.mockResolvedValueOnce({
        data: {
          valid: true,
          coupon: { code: 'SAVE20', title: '20% Off' }
        }
      });

      await couponAPI.validateCoupon(code);

      expect(mockAxios.get).toHaveBeenCalledWith(`/api/coupons/validate/${code}`);
    });

    test('redeemCoupon should make POST request to /api/coupons/redeem', async () => {
      const redemptionData = {
        coupon_code: 'SAVE20',
        order_id: 1
      };

      mockAxios.post.mockResolvedValueOnce({
        data: {
          redemption: { id: 1, discount_amount: 20 }
        }
      });

      await couponAPI.redeemCoupon(redemptionData);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/coupons/redeem', redemptionData);
    });

    test('searchCoupons should make GET request to /api/coupons/search', async () => {
      const query = 'SAVE20';

      mockAxios.get.mockResolvedValueOnce({
        data: {
          coupons: [
            { id: 1, code: 'SAVE20', title: '20% Off' }
          ]
        }
      });

      await couponAPI.searchCoupons(query);

      expect(mockAxios.get).toHaveBeenCalledWith(`/api/coupons/search?q=${query}`);
    });

    test('getUserRedemptions should make GET request to /api/coupons/user/redemptions', async () => {
      mockAxios.get.mockResolvedValueOnce({
        data: {
          redemptions: [
            { id: 1, coupon_code: 'SAVE20', discount_amount: 20 }
          ]
        }
      });

      await couponAPI.getUserRedemptions();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/coupons/user/redemptions');
    });
  });

  describe('productAPI', () => {
    test('getProducts should make GET request to /api/products', async () => {
      mockAxios.get.mockResolvedValueOnce({
        data: {
          products: [
            { id: 1, name: 'Test Product', price: 100 }
          ]
        }
      });

      await productAPI.getProducts();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/products?page=1&per_page=10&category=&sort_by=name');
    });

    test('getProduct should make GET request to /api/products/:id', async () => {
      const productId = 1;

      mockAxios.get.mockResolvedValueOnce({
        data: {
          product: { id: 1, name: 'Test Product', price: 100 }
        }
      });

      await productAPI.getProduct(productId);

      expect(mockAxios.get).toHaveBeenCalledWith(`/api/products/${productId}`);
    });

    test('searchProducts should make GET request to /api/products/search', async () => {
      const query = 'test';

      mockAxios.get.mockResolvedValueOnce({
        data: {
          products: [
            { id: 1, name: 'Test Product', price: 100 }
          ]
        }
      });

      await productAPI.searchProducts(query);

      expect(mockAxios.get).toHaveBeenCalledWith(`/api/products/search?q=${query}&page=1&per_page=10`);
    });

    test('getCategories should make GET request to /api/products/categories', async () => {
      mockAxios.get.mockResolvedValueOnce({
        data: {
          categories: ['Electronics', 'Clothing']
        }
      });

      await productAPI.getCategories();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/products/categories');
    });
  });

  describe('cartAPI', () => {
    test('addToCart should make POST request to /api/cart/add', async () => {
      const cartData = {
        product_id: 1,
        quantity: 2
      };

      mockAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Product added to cart',
          cart: { items: [{ product_id: 1, quantity: 2 }] }
        }
      });

      await cartAPI.addToCart(1, 2);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/cart/add', cartData);
    });

    test('getCart should make GET request to /api/cart', async () => {
      mockAxios.get.mockResolvedValueOnce({
        data: {
          cart: { items: [{ product_id: 1, quantity: 2 }] }
        }
      });

      await cartAPI.getCart();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/cart');
    });

    test('updateCart should make PUT request to /api/cart/update', async () => {
      const updates = [{ product_id: 1, quantity: 3 }];

      mockAxios.put.mockResolvedValueOnce({
        data: {
          message: 'Cart updated successfully',
          cart: { items: [{ product_id: 1, quantity: 3 }] }
        }
      });

      await cartAPI.updateCart(updates);

      expect(mockAxios.put).toHaveBeenCalledWith('/api/cart/update', { updates });
    });

    test('removeFromCart should make DELETE request to /api/cart/remove/:product_id', async () => {
      const productId = 1;

      mockAxios.delete.mockResolvedValueOnce({
        data: {
          message: 'Product removed from cart'
        }
      });

      await cartAPI.removeFromCart(productId);

      expect(mockAxios.delete).toHaveBeenCalledWith(`/api/cart/remove/${productId}`);
    });

    test('applyCoupon should make POST request to /api/cart/apply-coupon', async () => {
      const couponCode = 'SAVE20';

      mockAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Coupon applied successfully',
          discount: 20
        }
      });

      await cartAPI.applyCoupon(couponCode);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/cart/apply-coupon', { coupon_code: couponCode });
    });

    test('checkout should make POST request to /api/cart/checkout', async () => {
      const checkoutData = {
        shipping_address: '123 Test St',
        payment_method: 'credit_card'
      };

      mockAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Order placed successfully',
          order: { id: 1, total_amount: 100 }
        }
      });

      await cartAPI.checkout(checkoutData);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/cart/checkout', checkoutData);
    });
  });

  describe('adminAPI', () => {
    test('getDashboard should make GET request to /api/admin/dashboard', async () => {
      mockAxios.get.mockResolvedValueOnce({
        data: {
          stats: {
            total_users: 100,
            total_coupons: 50,
            total_products: 200
          }
        }
      });

      await adminAPI.getDashboard();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/admin/dashboard');
    });

    test('getProducts should make GET request to /api/admin/products', async () => {
      mockAxios.get.mockResolvedValueOnce({
        data: {
          products: [
            { id: 1, name: 'Test Product', price: 100 }
          ],
          pagination: { page: 1, pages: 1 }
        }
      });

      await adminAPI.getProducts();

      expect(mockAxios.get).toHaveBeenCalledWith('/api/admin/products?page=1&per_page=10&category=all&status=all&search=');
    });

    test('createProduct should make POST request to /api/admin/products', async () => {
      const productData = {
        name: 'Test Product',
        price: 100,
        category: 'Electronics'
      };

      mockAxios.post.mockResolvedValueOnce({
        data: {
          product: { id: 1, name: 'Test Product', price: 100 }
        }
      });

      await adminAPI.createProduct(productData);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/admin/products', productData);
    });

    test('updateProduct should make PUT request to /api/admin/products/:id', async () => {
      const productId = 1;
      const updateData = {
        name: 'Updated Product',
        price: 150
      };

      mockAxios.put.mockResolvedValueOnce({
        data: {
          product: { id: 1, name: 'Updated Product', price: 150 }
        }
      });

      await adminAPI.updateProduct(productId, updateData);

      expect(mockAxios.put).toHaveBeenCalledWith(`/api/admin/products/${productId}`, updateData);
    });

    test('deleteProduct should make DELETE request to /api/admin/products/:id', async () => {
      const productId = 1;

      mockAxios.delete.mockResolvedValueOnce({
        data: {
          message: 'Product deleted successfully'
        }
      });

      await adminAPI.deleteProduct(productId);

      expect(mockAxios.delete).toHaveBeenCalledWith(`/api/admin/products/${productId}`);
    });
  });
});
