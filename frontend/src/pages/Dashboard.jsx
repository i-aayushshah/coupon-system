import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { userAPI, couponAPI } from '../utils/api';
import DashboardLayout from '../components/DashboardLayout';
import StatsCard from '../components/StatsCard';
import { Button, Card, LoadingSpinner } from '../components/FormComponents';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalRedeemed: 0,
    totalSavings: 0,
    availableCoupons: 0,
    recentRedemptions: []
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch user stats and recent redemptions
        const [statsData, redemptionsData] = await Promise.all([
          userAPI.getStats(),
          couponAPI.getUserRedemptions(1, 5)
        ]);



        setStats({
          totalRedeemed: statsData.stats?.total_redemptions || 0,
          totalSavings: statsData.stats?.total_savings || 0,
          availableCoupons: statsData.stats?.available_coupons || 0,
          recentRedemptions: statsData.recent_redemptions || redemptionsData.redemptions || []
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.first_name}! 👋
        </h1>
        <p className="text-gray-600 mt-2">
          Here's what's happening with your coupons and savings
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="Total Redeemed"
          value={stats.totalRedeemed}
          subtitle="Coupons used"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
            </svg>
          }
          color="blue"
        />
        <StatsCard
          title="Total Savings"
          value={formatCurrency(stats.totalSavings)}
          subtitle="Money saved"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          }
          color="green"
        />
        <StatsCard
          title="Available Coupons"
          value={stats.availableCoupons}
          subtitle="Ready to use"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          color="purple"
        />
        <StatsCard
          title="Member Since"
          value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
          subtitle="Account created"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          }
          color="orange"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Redemptions */}
        <Card>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Recent Redemptions</h2>
            <Button variant="outline" size="sm" onClick={() => window.location.href = '/redemption-history'}>
              View All
            </Button>
          </div>

          {stats.recentRedemptions.length > 0 ? (
            <div className="space-y-4">
              {stats.recentRedemptions.map((redemption) => (
                <div key={redemption.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{redemption.coupon_code}</p>
                    <p className="text-sm text-gray-600">{formatDate(redemption.redeemed_at)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-green-600">
                      -{formatCurrency(redemption.discount_applied)}
                    </p>
                    <p className="text-sm text-gray-600">
                      Order: {formatCurrency(redemption.order?.final_total || 0)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
              </svg>
              <p className="text-gray-500">No redemptions yet</p>
              <p className="text-sm text-gray-400">Start browsing coupons to save money!</p>
            </div>
          )}
        </Card>

        {/* Quick Actions */}
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
          <div className="space-y-4">
            <Button
              onClick={() => window.location.href = '/coupons'}
              className="w-full justify-start"
              size="lg"
            >
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
              </svg>
              Browse Available Coupons
            </Button>

            <Button
              onClick={() => window.location.href = '/products'}
              variant="outline"
              className="w-full justify-start"
              size="lg"
            >
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              Shop Products
            </Button>

            <Button
              onClick={() => window.location.href = '/profile'}
              variant="outline"
              className="w-full justify-start"
              size="lg"
            >
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Edit Profile
            </Button>

            <Button
              onClick={() => window.location.href = '/redemption-history'}
              variant="outline"
              className="w-full justify-start"
              size="lg"
            >
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              View Redemption History
            </Button>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
