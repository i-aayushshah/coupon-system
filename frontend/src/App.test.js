import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock all problematic modules
jest.mock('react-hot-toast', () => ({
  Toaster: () => <div data-testid="toaster" />,
}));

jest.mock('./hooks/useAuth', () => ({
  AuthProvider: ({ children }) => <div data-testid="auth-provider">{children}</div>,
}));

jest.mock('./components/ProtectedRoute', () => {
  return function MockProtectedRoute({ children }) {
    return <div data-testid="protected-route">{children}</div>;
  };
});

jest.mock('./components/AdminRoute', () => {
  return function MockAdminRoute({ children }) {
    return <div data-testid="admin-route">{children}</div>;
  };
});

jest.mock('./components/AdminRedirect', () => {
  return function MockAdminRedirect({ children }) {
    return <div data-testid="admin-redirect">{children}</div>;
  };
});

// Mock all page components
jest.mock('./pages/Login', () => () => <div data-testid="login-page">Login Page</div>);
jest.mock('./pages/Register', () => () => <div data-testid="register-page">Register Page</div>);
jest.mock('./pages/ForgotPassword', () => () => <div data-testid="forgot-password-page">Forgot Password Page</div>);
jest.mock('./pages/ResetPassword', () => () => <div data-testid="reset-password-page">Reset Password Page</div>);
jest.mock('./pages/VerifyEmail', () => () => <div data-testid="verify-email-page">Verify Email Page</div>);
jest.mock('./pages/Dashboard', () => () => <div data-testid="dashboard-page">Dashboard Page</div>);
jest.mock('./pages/Profile', () => () => <div data-testid="profile-page">Profile Page</div>);
jest.mock('./pages/Coupons', () => () => <div data-testid="coupons-page">Coupons Page</div>);
jest.mock('./pages/Products', () => () => <div data-testid="products-page">Products Page</div>);
jest.mock('./pages/RedemptionHistory', () => () => <div data-testid="redemption-history-page">Redemption History Page</div>);
jest.mock('./pages/Cart', () => () => <div data-testid="cart-page">Cart Page</div>);

// Mock admin pages
jest.mock('./pages/admin/AdminDashboard', () => () => <div data-testid="admin-dashboard-page">Admin Dashboard Page</div>);
jest.mock('./pages/admin/ManageCoupons', () => () => <div data-testid="manage-coupons-page">Manage Coupons Page</div>);
jest.mock('./pages/admin/CouponForm', () => () => <div data-testid="coupon-form-page">Coupon Form Page</div>);
jest.mock('./pages/admin/Users', () => () => <div data-testid="users-page">Users Page</div>);
jest.mock('./pages/admin/ManageProducts', () => () => <div data-testid="manage-products-page">Manage Products Page</div>);
jest.mock('./pages/admin/ProductForm', () => () => <div data-testid="product-form-page">Product Form Page</div>);
jest.mock('./pages/admin/ImportProducts', () => () => <div data-testid="import-products-page">Import Products Page</div>);
jest.mock('./pages/admin/Activities', () => () => <div data-testid="activities-page">Activities Page</div>);
jest.mock('./pages/admin/CouponView', () => () => <div data-testid="coupon-view-page">Coupon View Page</div>);
jest.mock('./pages/admin/Settings', () => () => <div data-testid="settings-page">Settings Page</div>);

test('renders app without crashing', () => {
  render(<App />);

  // Check that the app renders without crashing
  expect(screen.getByTestId('auth-provider')).toBeInTheDocument();
  expect(screen.getByTestId('toaster')).toBeInTheDocument();
});

test('app has correct structure', () => {
  render(<App />);

  // Check that the main app div exists
  const appDiv = document.querySelector('.App');
  expect(appDiv).toBeInTheDocument();
});

test('app renders without errors', () => {
  // This test ensures the app can be rendered without throwing errors
  expect(() => {
    render(<App />);
  }).not.toThrow();
});
