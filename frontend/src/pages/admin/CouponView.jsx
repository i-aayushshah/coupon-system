import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { adminAPI } from '../../utils/api';
import { Button, Card, LoadingSpinner } from '../../components/FormComponents';
import toast from 'react-hot-toast';

const CouponView = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [coupon, setCoupon] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCoupon();
  }, [id]);

  const fetchCoupon = async () => {
    setLoading(true);
    try {
      const response = await adminAPI.getCoupon(id);
      setCoupon(response.coupon);
    } catch (error) {
      console.error('Error fetching coupon:', error);
      toast.error('Failed to load coupon');
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

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusBadge = (isActive, startDate, endDate) => {
    if (!isActive) return 'bg-red-100 text-red-800';

    const now = new Date();
    const start = startDate ? new Date(startDate) : null;
    const end = endDate ? new Date(endDate) : null;

    if (start && now < start) return 'bg-yellow-100 text-yellow-800';
    if (end && now > end) return 'bg-red-100 text-red-800';
    return 'bg-green-100 text-green-800';
  };

  const getStatusText = (isActive, startDate, endDate) => {
    if (!isActive) return 'Inactive';

    const now = new Date();
    const start = startDate ? new Date(startDate) : null;
    const end = endDate ? new Date(endDate) : null;

    if (start && now < start) return 'Pending';
    if (end && now > end) return 'Expired';
    return 'Active';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!coupon) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <div className="text-center py-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Coupon Not Found</h2>
            <p className="text-gray-600 mb-4">The coupon you're looking for doesn't exist.</p>
            <Button onClick={() => navigate('/admin/coupons')}>
              Back to Coupons
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Coupon Details</h1>
            <p className="text-gray-600 mt-2">View coupon information and statistics</p>
          </div>
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={() => navigate('/admin/coupons')}
            >
              Back to Coupons
            </Button>
            <Button
              onClick={() => navigate(`/admin/coupons/${id}/edit`)}
            >
              Edit Coupon
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Coupon Information */}
        <div className="lg:col-span-2">
          <Card>
            <div className="space-y-6">
              {/* Basic Information */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Coupon Title</label>
                    <p className="text-sm text-gray-900 mt-1">{coupon.title}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Coupon Code</label>
                    <p className="text-sm text-gray-900 mt-1 font-mono">{coupon.code}</p>
                  </div>
                </div>
                <div className="mt-4">
                  <label className="text-sm font-medium text-gray-500">Description</label>
                  <p className="text-sm text-gray-900 mt-1">{coupon.description}</p>
                </div>
              </div>

              {/* Discount Settings */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Discount Settings</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Discount Type</label>
                    <p className="text-sm text-gray-900 mt-1 capitalize">{coupon.discount_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Discount Value</label>
                    <p className="text-sm text-gray-900 mt-1">
                      {coupon.discount_type === 'percentage'
                        ? `${coupon.discount_value}%`
                        : formatCurrency(coupon.discount_value)
                      }
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Minimum Order Value</label>
                    <p className="text-sm text-gray-900 mt-1">
                      {coupon.minimum_order_value ? formatCurrency(coupon.minimum_order_value) : 'No minimum'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Maximum Discount Amount</label>
                    <p className="text-sm text-gray-900 mt-1">
                      {coupon.maximum_discount_amount ? formatCurrency(coupon.maximum_discount_amount) : 'No limit'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Usage Settings */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Usage Settings</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Current Uses</label>
                    <p className="text-sm text-gray-900 mt-1">{coupon.current_uses}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Maximum Uses</label>
                    <p className="text-sm text-gray-900 mt-1">{coupon.max_uses || 'Unlimited'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Public Coupon</label>
                    <p className="text-sm text-gray-900 mt-1">{coupon.is_public ? 'Yes' : 'No'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">First-time Users Only</label>
                    <p className="text-sm text-gray-900 mt-1">{coupon.first_time_user_only ? 'Yes' : 'No'}</p>
                  </div>
                </div>
              </div>

              {/* Validity Period */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Validity Period</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Start Date</label>
                    <p className="text-sm text-gray-900 mt-1">{formatDate(coupon.start_date)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">End Date</label>
                    <p className="text-sm text-gray-900 mt-1">{formatDate(coupon.end_date)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Status</label>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${getStatusBadge(coupon.is_active, coupon.start_date, coupon.end_date)}`}>
                      {getStatusText(coupon.is_active, coupon.start_date, coupon.end_date)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Applicable Categories */}
              {coupon.applicable_categories && coupon.applicable_categories.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Applicable Categories</h3>
                  <div className="flex flex-wrap gap-2">
                    {coupon.applicable_categories.map((category, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Created Information */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Created Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Created At</label>
                    <p className="text-sm text-gray-900 mt-1">{formatDate(coupon.created_at)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Last Updated</label>
                    <p className="text-sm text-gray-900 mt-1">{formatDate(coupon.updated_at)}</p>
                  </div>
                  {coupon.creator && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Created By</label>
                      <p className="text-sm text-gray-900 mt-1">{coupon.creator.username}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Preview */}
        <div className="lg:col-span-1">
          <Card>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Coupon Preview</h3>
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
              <div className="text-center">
                <h4 className="text-xl font-bold mb-2">{coupon.title}</h4>
                <div className="text-3xl font-bold mb-2">{coupon.code}</div>
                <p className="text-blue-100 mb-4">{coupon.description}</p>
                <div className="bg-white bg-opacity-20 rounded-lg p-3">
                  <div className="text-2xl font-bold">
                    {coupon.discount_type === 'percentage'
                      ? `${coupon.discount_value}% OFF`
                      : `${formatCurrency(coupon.discount_value)} OFF`
                    }
                  </div>
                  {coupon.minimum_order_value && (
                    <div className="text-sm">
                      Min. order: {formatCurrency(coupon.minimum_order_value)}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CouponView;
