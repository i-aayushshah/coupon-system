import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../hooks/useAuth';
import { userAPI } from '../utils/api';
import DashboardLayout from '../components/DashboardLayout';
import StatsCard from '../components/StatsCard';
import { Input, Button, Card, Alert, LoadingSpinner } from '../components/FormComponents';
import toast from 'react-hot-toast';

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors },
    reset: resetProfile
  } = useForm();

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    formState: { errors: passwordErrors },
    reset: resetPassword,
    watch
  } = useForm();

  const password = watch('newPassword');

  useEffect(() => {
    const fetchUserStats = async () => {
      try {
        const statsData = await userAPI.getStats();
        setStats(statsData);
      } catch (error) {
        console.error('Error fetching user stats:', error);
      }
    };

    fetchUserStats();
  }, []);

  useEffect(() => {
    if (user) {
      resetProfile({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || ''
      });
    }
  }, [user, resetProfile]);

  const onProfileSubmit = async (data) => {
    setLoading(true);
    try {
      // Only send allowed fields to the backend
      const allowedData = {
        first_name: data.first_name,
        last_name: data.last_name,
        phone: data.phone
      };

      const response = await userAPI.updateProfile(allowedData);
      updateUser(response.profile);
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const onPasswordSubmit = async (data) => {
    setLoading(true);
    try {
      await userAPI.changePassword({
        current_password: data.currentPassword,
        new_password: data.newPassword
      });
      toast.success('Password changed successfully!');
      setShowPasswordForm(false);
      resetPassword();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const tabs = [
    { id: 'profile', name: 'Profile Information', icon: '👤' },
    { id: 'security', name: 'Security', icon: '🔒' },
    { id: 'stats', name: 'Account Statistics', icon: '📊' }
  ];

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
          <p className="text-gray-600 mt-2">Manage your account information and preferences</p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Profile Information Tab */}
        {activeTab === 'profile' && (
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Personal Information</h2>
            <form onSubmit={handleProfileSubmit(onProfileSubmit)} method="POST" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Input
                  label="First Name"
                  error={profileErrors.first_name?.message}
                  {...registerProfile('first_name', {
                    required: 'First name is required',
                    minLength: {
                      value: 2,
                      message: 'First name must be at least 2 characters'
                    }
                  })}
                />
                <Input
                  label="Last Name"
                  error={profileErrors.last_name?.message}
                  {...registerProfile('last_name', {
                    required: 'Last name is required',
                    minLength: {
                      value: 2,
                      message: 'Last name must be at least 2 characters'
                    }
                  })}
                />
              </div>

                             <div>
                 <Input
                   label="Username"
                   value={user?.username || ''}
                   disabled={true}
                   className="bg-gray-50"
                 />
                 <p className="text-sm text-gray-500 mt-1">Username cannot be changed for security reasons</p>
               </div>

               <div>
                 <Input
                   label="Email Address"
                   type="email"
                   value={user?.email || ''}
                   disabled={true}
                   className="bg-gray-50"
                 />
                 <p className="text-sm text-gray-500 mt-1">Email cannot be changed for security reasons</p>
               </div>

               <Input
                 label="Phone Number"
                 error={profileErrors.phone?.message}
                 {...registerProfile('phone', {
                   pattern: {
                     value: /^[\+]?[1-9][\d]{0,15}$/,
                     message: 'Please enter a valid phone number'
                   }
                 })}
               />

              <div className="flex justify-end">
                <Button
                  type="submit"
                  loading={loading}
                  disabled={loading}
                >
                  Update Profile
                </Button>
              </div>
            </form>
          </Card>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Change Password</h2>

              {!showPasswordForm ? (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <p className="text-gray-500 mb-4">Keep your account secure with a strong password</p>
                  <Button onClick={() => setShowPasswordForm(true)}>
                    Change Password
                  </Button>
                </div>
              ) : (
                <form onSubmit={handlePasswordSubmit(onPasswordSubmit)} className="space-y-6">
                  <Input
                    label="Current Password"
                    type="password"
                    error={passwordErrors.currentPassword?.message}
                    {...registerPassword('currentPassword', {
                      required: 'Current password is required'
                    })}
                  />

                  <Input
                    label="New Password"
                    type="password"
                    error={passwordErrors.newPassword?.message}
                    {...registerPassword('newPassword', {
                      required: 'New password is required',
                      minLength: {
                        value: 8,
                        message: 'Password must be at least 8 characters'
                      },
                      pattern: {
                        value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                        message: 'Password must contain at least one uppercase letter, one lowercase letter, and one number'
                      }
                    })}
                  />

                  <Input
                    label="Confirm New Password"
                    type="password"
                    error={passwordErrors.confirmPassword?.message}
                    {...registerPassword('confirmPassword', {
                      required: 'Please confirm your password',
                      validate: (value) =>
                        value === password || 'Passwords do not match'
                    })}
                  />

                  <div className="flex justify-end space-x-3">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowPasswordForm(false);
                        resetPassword();
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      loading={loading}
                      disabled={loading}
                    >
                      Change Password
                    </Button>
                  </div>
                </form>
              )}
            </Card>

            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Account Security</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h3 className="font-medium text-gray-900">Email Verification</h3>
                    <p className="text-sm text-gray-600">Your email is verified and secure</p>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Verified
                  </span>
                </div>

                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h3 className="font-medium text-gray-900">Two-Factor Authentication</h3>
                    <p className="text-sm text-gray-600">Add an extra layer of security</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Enable
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Account Statistics Tab */}
        {activeTab === 'stats' && (
          <div className="space-y-6">
            {stats ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <StatsCard
                    title="Total Redemptions"
                    value={stats.stats?.total_redemptions || 0}
                    subtitle="Coupons used"
                    color="blue"
                  />
                  <StatsCard
                    title="Total Savings"
                    value={formatCurrency(stats.stats?.total_savings || 0)}
                    subtitle="Money saved"
                    color="green"
                  />
                  <StatsCard
                    title="Available Coupons"
                    value={stats.stats?.available_coupons || 0}
                    subtitle="Ready to use"
                    color="purple"
                  />
                </div>

                <Card>
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">Account Information</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Member Since:</span>
                        <span className="font-medium">
                          {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Account Status:</span>
                        <span className="font-medium text-green-600">Active</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Email Verified:</span>
                        <span className="font-medium text-green-600">✓</span>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Last Login:</span>
                        <span className="font-medium">Today</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Account Type:</span>
                        <span className="font-medium">
                          {user?.is_admin ? 'Administrator' : 'Standard User'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Username:</span>
                        <span className="font-medium">@{user?.username}</span>
                      </div>
                    </div>
                  </div>
                </Card>
              </>
            ) : (
              <div className="flex items-center justify-center h-64">
                <LoadingSpinner size="lg" />
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Profile;
