import React, { useState, useEffect } from 'react';
import { adminAPI } from '../utils/api';
import toast from 'react-hot-toast';

const ActivityNotification = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [recentActivities, setRecentActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetchRecentActivities();
    // Poll for new activities every 30 seconds
    const interval = setInterval(fetchRecentActivities, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchRecentActivities = async () => {
    try {
      const response = await adminAPI.getRecentActivities(1, 5);
      const activities = response.activities || [];

      // Check for new activities (last 5 minutes)
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
      const newActivities = activities.filter(activity =>
        new Date(activity.timestamp) > fiveMinutesAgo
      );

      setRecentActivities(activities);
      setUnreadCount(newActivities.length);

      // Show toast for new activities
      newActivities.forEach(activity => {
        toast.success(`${activity.title}`, {
          duration: 4000,
          icon: getActivityIcon(activity.type),
        });
      });
    } catch (error) {
      console.error('Error fetching recent activities:', error);
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'coupon_created':
        return '🎫';
      case 'coupon_redeemed':
        return '💰';
      case 'user_registered':
        return '👤';
      case 'order_placed':
        return '🛒';
      case 'product_created':
        return '📦';
      default:
        return '📊';
    }
  };

  const getActivityTypeColor = (type) => {
    switch (type) {
      case 'coupon_created':
        return 'bg-green-100 text-green-800';
      case 'coupon_redeemed':
        return 'bg-blue-100 text-blue-800';
      case 'user_registered':
        return 'bg-purple-100 text-purple-800';
      case 'order_placed':
        return 'bg-orange-100 text-orange-800';
      case 'product_created':
        return 'bg-indigo-100 text-indigo-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM10.5 3.75a6 6 0 0 1 6 6v3.75l2.25 2.25V21a2.25 2.25 0 0 1-4.5 0v-.75a6 6 0 0 1-6-6v-3.75a6 6 0 0 1 6-6Z" />
        </svg>

        {/* Unread Badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
          <div className="py-2">
            <div className="px-4 py-2 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-900">Recent Activities</h3>
            </div>

            <div className="max-h-64 overflow-y-auto">
              {recentActivities.length > 0 ? (
                recentActivities.map((activity) => (
                  <div key={activity.id} className="px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        <span className="text-lg">{getActivityIcon(activity.type)}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.title}
                        </p>
                        <p className="text-sm text-gray-600">
                          {activity.description}
                        </p>
                        <div className="flex items-center justify-between mt-1">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getActivityTypeColor(activity.type)}`}>
                            {activity.type.replace('_', ' ').toUpperCase()}
                          </span>
                          <p className="text-xs text-gray-400">
                            {formatDate(activity.timestamp)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="px-4 py-3 text-center text-gray-500">
                  <p className="text-sm">No recent activities</p>
                </div>
              )}
            </div>

            <div className="px-4 py-2 border-t border-gray-200">
              <button
                onClick={() => {
                  setIsOpen(false);
                  window.location.href = '/admin/activities';
                }}
                className="w-full text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                View All Activities
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityNotification;
