import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const message = error.response?.data?.error || error.response?.data?.message || 'Something went wrong';

    // Handle specific error cases
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      toast.error('Session expired. Please login again.');
    } else if (error.response?.status === 403) {
      toast.error('Access denied. You do not have permission for this action.');
    } else if (error.response?.status === 404) {
      toast.error('Resource not found.');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else {
      toast.error(message);
    }

    return Promise.reject(error);
  }
);

// Auth API functions
export const authAPI = {
  // Register new user
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  // Login user
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },

  // Verify email
  verifyEmail: async (token, email) => {
    const response = await api.post('/api/auth/verify-email', { token, email });
    return response.data;
  },

  // Resend verification email
  resendVerification: async (email) => {
    const response = await api.post('/api/auth/resend-verification', { email });
    return response.data;
  },

  // Forgot password
  forgotPassword: async (email) => {
    const response = await api.post('/api/auth/forgot-password', { email });
    return response.data;
  },

  // Validate reset token
  validateResetToken: async (token, email) => {
    const response = await api.get(`/api/auth/validate-reset-token?token=${token}&email=${email}`);
    return response.data;
  },

  // Reset password
  resetPassword: async (token, email, newPassword) => {
    const response = await api.post('/api/auth/reset-password', {
      token,
      email,
      new_password: newPassword
    });
    return response.data;
  },

  // Get current user profile
  getProfile: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

// User management functions
export const userAPI = {
  // Update profile
  updateProfile: async (profileData) => {
    const response = await api.put('/api/user/profile', profileData);
    return response.data;
  },

  // Change password
  changePassword: async (passwordData) => {
    const response = await api.post('/api/user/change-password', passwordData);
    return response.data;
  },

  // Delete account
  deleteAccount: async (password) => {
    const response = await api.post('/api/user/delete-account', { password });
    return response.data;
  },

  // Get user stats
  getStats: async () => {
    const response = await api.get('/api/user/stats');
    return response.data;
  },

  // Get user dashboard
  getDashboard: async () => {
    const response = await api.get('/api/user/dashboard');
    return response.data;
  },
};

// Coupon API functions
export const couponAPI = {
  // Get public coupons
  getPublicCoupons: async (page = 1, perPage = 10) => {
    const response = await api.get(`/api/coupons/public?page=${page}&per_page=${perPage}`);
    return response.data;
  },

  // Validate coupon
  validateCoupon: async (code) => {
    const response = await api.get(`/api/coupons/validate/${code}`);
    return response.data;
  },

  // Redeem coupon
  redeemCoupon: async (code, orderAmount) => {
    const response = await api.post('/api/coupons/redeem', {
      code,
      order_amount: orderAmount
    });
    return response.data;
  },

  // Search coupons
  searchCoupons: async (query = '', discountType = '', sortBy = 'expiry', page = 1) => {
    // If no query is provided, use the public endpoint instead
    if (!query.trim()) {
      const response = await api.get(`/api/coupons/public?page=${page}&per_page=12`);
      return response.data;
    }
    // If query is provided, use the search endpoint
    const response = await api.get(`/api/coupons/search?q=${query}&discount_type=${discountType}&sort_by=${sortBy}&page=${page}&per_page=12`);
    return response.data;
  },

  // Get user redemptions
  getUserRedemptions: async (page = 1, perPage = 10, queryParams = '') => {
    const url = queryParams
      ? `/api/coupons/user/redemptions?${queryParams}`
      : `/api/coupons/user/redemptions?page=${page}&per_page=${perPage}`;
    const response = await api.get(url);
    return response.data;
  },
};

// Admin API functions
export const adminAPI = {
  // Dashboard
  getDashboard: async () => {
    const response = await api.get('/api/admin/dashboard');
    return response.data;
  },

  getRecentActivities: async () => {
    const response = await api.get('/api/admin/activities');
    return response.data;
  },

  // Coupons
  createCoupon: async (couponData) => {
    const response = await api.post('/api/admin/coupons', couponData);
    return response.data;
  },

  getCoupons: async (page = 1, perPage = 10, status = 'all', search = '') => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString()
    });
    if (status && status !== 'all') params.append('status', status);
    if (search) params.append('search', search);

    const response = await api.get(`/api/admin/coupons?${params}`);
    return response.data;
  },

  getCoupon: async (id) => {
    const response = await api.get(`/api/admin/coupons/${id}`);
    return response.data;
  },

  updateCoupon: async (id, couponData) => {
    const response = await api.put(`/api/admin/coupons/${id}`, couponData);
    return response.data;
  },

  deleteCoupon: async (id) => {
    const response = await api.delete(`/api/admin/coupons/${id}`);
    return response.data;
  },

  getCouponRedemptions: async (id, page = 1, perPage = 10) => {
    const response = await api.get(`/api/admin/coupons/${id}/redemptions?page=${page}&per_page=${perPage}`);
    return response.data;
  },

  // Products
  createProduct: async (productData) => {
    const response = await api.post('/api/admin/products', productData);
    return response.data;
  },

  getProducts: async (page = 1, perPage = 10, category = 'all', status = 'all') => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString()
    });
    if (category && category !== 'all') params.append('category', category);
    if (status && status !== 'all') params.append('status', status);

    const response = await api.get(`/api/admin/products?${params}`);
    return response.data;
  },

  getProduct: async (id) => {
    const response = await api.get(`/api/admin/products/${id}`);
    return response.data;
  },

  updateProduct: async (id, productData) => {
    const response = await api.put(`/api/admin/products/${id}`, productData);
    return response.data;
  },

  deleteProduct: async (id) => {
    const response = await api.delete(`/api/admin/products/${id}`);
    return response.data;
  },

  getCategories: async () => {
    const response = await api.get('/api/admin/categories');
    return response.data;
  },

  bulkUploadProducts: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/admin/products/bulk-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Users
  getUsers: async (page = 1, perPage = 10, search = '') => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString()
    });
    if (search) params.append('search', search);

    const response = await api.get(`/api/admin/users?${params}`);
    return response.data;
  },

  getUser: async (id) => {
    const response = await api.get(`/api/admin/users/${id}`);
    return response.data;
  },

  getUserStats: async (id) => {
    const response = await api.get(`/api/admin/users/${id}/stats`);
    return response.data;
  },

  updateUserRole: async (id, data) => {
    const response = await api.put(`/api/admin/users/${id}/role`, data);
    return response.data;
  },

  updateUserStatus: async (id, data) => {
    const response = await api.put(`/api/admin/users/${id}/status`, data);
    return response.data;
  }
};

// Product API functions
export const productAPI = {
  // Get products
  getProducts: async (page = 1, perPage = 10, category = '', sortBy = 'name') => {
    const response = await api.get(`/api/products?page=${page}&per_page=${perPage}&category=${category}&sort_by=${sortBy}`);
    return response.data;
  },

  // Get product details
  getProduct: async (id) => {
    const response = await api.get(`/api/products/${id}`);
    return response.data;
  },

  // Search products
  searchProducts: async (query, page = 1, perPage = 10) => {
    const response = await api.get(`/api/products/search?q=${query}&page=${page}&per_page=${perPage}`);
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/api/products/categories');
    return response.data;
  },

  // Calculate discount
  calculateDiscount: async (cartData, couponCode) => {
    const response = await api.post('/api/products/calculate-discount', {
      cart: cartData,
      coupon_code: couponCode
    });
    return response.data;
  },
};

// Cart API functions
export const cartAPI = {
  // Add to cart
  addToCart: async (productId, quantity) => {
    const response = await api.post('/api/cart/add', { product_id: productId, quantity });
    return response.data;
  },

  // Get cart
  getCart: async () => {
    const response = await api.get('/api/cart');
    return response.data;
  },

  // Check if product is in cart
  isProductInCart: async (productId) => {
    try {
      const response = await api.get('/api/cart');
      const cart = response.data.cart;
      return cart.items.some(item => item.product_id === parseInt(productId));
    } catch (error) {
      console.error('Error checking cart:', error);
      return false;
    }
  },

  // Update cart
  updateCart: async (productId, quantity) => {
    const requestData = {
      updates: [{ product_id: parseInt(productId), quantity: parseInt(quantity) }]
    };
    console.log('Sending cart update request:', requestData); // Debug log
    const response = await api.put('/api/cart/update', requestData);
    return response.data;
  },

  // Remove from cart
  removeFromCart: async (productId) => {
    const response = await api.delete(`/api/cart/remove/${productId}`);
    return response.data;
  },

  // Apply coupon
  applyCoupon: async (couponCode) => {
    const response = await api.post('/api/cart/apply-coupon', { coupon_code: couponCode });
    return response.data;
  },

  // Remove coupon
  removeCoupon: async () => {
    const response = await api.post('/api/cart/remove-coupon');
    return response.data;
  },

  // Checkout
  checkout: async (checkoutData) => {
    const response = await api.post('/api/cart/checkout', checkoutData);
    return response.data;
  },
};

export default api;
