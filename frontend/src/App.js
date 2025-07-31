import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './hooks/useAuth';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';
import AdminRedirect from './components/AdminRedirect';

// Import pages
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import VerifyEmail from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Coupons from './pages/Coupons';
import Products from './pages/Products';
import RedemptionHistory from './pages/RedemptionHistory';
import Cart from './pages/Cart';

// Import admin pages
import AdminDashboard from './pages/admin/AdminDashboard';
import ManageCoupons from './pages/admin/ManageCoupons';
import CouponForm from './pages/admin/CouponForm';
import Users from './pages/admin/Users';
import ManageProducts from './pages/admin/ManageProducts';
import ProductForm from './pages/admin/ProductForm';
import ImportProducts from './pages/admin/ImportProducts';
import CouponView from './pages/admin/CouponView';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#10B981',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#EF4444',
                  secondary: '#fff',
                },
              },
            }}
          />

          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />
            <Route path="/verify-email/:token" element={<VerifyEmail />} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <AdminRedirect>
                    <Dashboard />
                  </AdminRedirect>
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <AdminRedirect>
                    <Profile />
                  </AdminRedirect>
                </ProtectedRoute>
              }
            />
            <Route
              path="/coupons"
              element={
                <ProtectedRoute>
                  <AdminRedirect>
                    <Coupons />
                  </AdminRedirect>
                </ProtectedRoute>
              }
            />
            <Route
              path="/products"
              element={
                <ProtectedRoute>
                  <AdminRedirect>
                    <Products />
                  </AdminRedirect>
                </ProtectedRoute>
              }
            />
            <Route
              path="/redemption-history"
              element={
                <ProtectedRoute>
                  <AdminRedirect>
                    <RedemptionHistory />
                  </AdminRedirect>
                </ProtectedRoute>
              }
            />
            <Route
              path="/cart"
              element={
                <ProtectedRoute>
                  <AdminRedirect>
                    <Cart />
                  </AdminRedirect>
                </ProtectedRoute>
              }
            />

            {/* Admin routes */}
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/coupons"
              element={
                <AdminRoute>
                  <ManageCoupons />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/coupons/create"
              element={
                <AdminRoute>
                  <CouponForm />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/coupons/:id"
              element={
                <AdminRoute>
                  <CouponView />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/coupons/:id/edit"
              element={
                <AdminRoute>
                  <CouponForm />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/products"
              element={
                <AdminRoute>
                  <ManageProducts />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/products/create"
              element={
                <AdminRoute>
                  <ProductForm />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/products/:id"
              element={
                <AdminRoute>
                  <ProductForm />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/products/:id/edit"
              element={
                <AdminRoute>
                  <ProductForm />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/products/import"
              element={
                <AdminRoute>
                  <ImportProducts />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <AdminRoute>
                  <Users />
                </AdminRoute>
              }
            />

            {/* Redirect root to dashboard if authenticated, otherwise to login */}
            <Route
              path="/"
              element={<Navigate to="/dashboard" replace />}
            />

            {/* Catch all route - redirect to dashboard */}
            <Route
              path="*"
              element={<Navigate to="/dashboard" replace />}
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
