import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { Button, Card } from '../components/FormComponents';

const Dashboard = () => {
  const { user, logout, isAdmin } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900">
            Welcome to the Coupon System
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Manage your coupons and track your savings
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* User Profile Card */}
          <Card className="md:col-span-2 lg:col-span-1">
            <div className="text-center">
              <div className="mx-auto h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                <span className="text-xl font-semibold text-blue-600">
                  {user?.first_name?.[0]}{user?.last_name?.[0]}
                </span>
              </div>
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                {user?.first_name} {user?.last_name}
              </h3>
              <p className="text-sm text-gray-500">{user?.email}</p>
              <p className="text-sm text-gray-500">@{user?.username}</p>

              {isAdmin() && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 mt-2">
                  Admin
                </span>
              )}

              <div className="mt-4">
                <Button
                  onClick={logout}
                  variant="outline"
                  size="sm"
                >
                  Sign Out
                </Button>
              </div>
            </div>
          </Card>

          {/* Quick Stats */}
          <Card>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Account Status:</span>
                <span className="text-sm font-medium text-green-600">Active</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Email Verified:</span>
                <span className="text-sm font-medium text-green-600">✓</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Member Since:</span>
                <span className="text-sm font-medium text-gray-900">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </Card>

          {/* Quick Actions */}
          <Card>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => alert('Coupon browsing feature coming soon!')}
              >
                Browse Coupons
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => alert('Profile management feature coming soon!')}
              >
                Edit Profile
              </Button>
              {isAdmin() && (
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => alert('Admin panel feature coming soon!')}
                >
                  Admin Panel
                </Button>
              )}
            </div>
          </Card>
        </div>

        {/* Coming Soon Section */}
        <div className="mt-8">
          <Card>
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                🚀 More Features Coming Soon!
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                We're working hard to bring you a complete coupon management experience.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900">Coupon Management</h4>
                  <p className="text-blue-700">Browse, search, and redeem coupons</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-900">Shopping Cart</h4>
                  <p className="text-green-700">Add products and apply discounts</p>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg">
                  <h4 className="font-medium text-purple-900">Analytics</h4>
                  <p className="text-purple-700">Track your savings and usage</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
