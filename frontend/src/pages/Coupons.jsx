import React, { useState, useEffect } from 'react';
import { couponAPI } from '../utils/api';
import DashboardLayout from '../components/DashboardLayout';
import CouponCard from '../components/CouponCard';
import { Input, Button, Card, LoadingSpinner } from '../components/FormComponents';
import toast from 'react-hot-toast';

const Coupons = () => {
  const [coupons, setCoupons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [discountType, setDiscountType] = useState('');
  const [sortBy, setSortBy] = useState('expiry');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [redeemingCoupon, setRedeemingCoupon] = useState(null);
  const [showRedeemed, setShowRedeemed] = useState(false);
  const [redeemedCoupons, setRedeemedCoupons] = useState([]);
  const [loadingRedeemed, setLoadingRedeemed] = useState(false);

  useEffect(() => {
    fetchCoupons();
  }, [searchQuery, discountType, sortBy, currentPage]);

  useEffect(() => {
    if (showRedeemed) {
      fetchRedeemedCoupons();
    }
  }, [showRedeemed]);

  // Refresh coupons when page becomes visible (e.g., after returning from cart)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchCoupons();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  const fetchCoupons = async () => {
    setLoading(true);
    try {
      const response = await couponAPI.searchCoupons(
        searchQuery,
        discountType,
        sortBy,
        currentPage
      );
      setCoupons(response.coupons || []);
      setTotalPages(response.pagination?.pages || 1);
    } catch (error) {
      console.error('Error fetching coupons:', error);
      toast.error('Failed to load coupons');
    } finally {
      setLoading(false);
    }
  };

  const fetchRedeemedCoupons = async () => {
    setLoadingRedeemed(true);
    try {
      const response = await couponAPI.getUserRedemptions(1, 50); // Get more redeemed coupons
      setRedeemedCoupons(response.redemptions || []);
    } catch (error) {
      console.error('Error fetching redeemed coupons:', error);
      toast.error('Failed to load redeemed coupons');
    } finally {
      setLoadingRedeemed(false);
    }
  };

  const handleRedeem = (coupon) => {
    setRedeemingCoupon(coupon);
    // Refresh the coupons list after redemption
    setTimeout(() => {
      fetchCoupons();
      setRedeemingCoupon(null);
    }, 1000);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchCoupons();
  };

  const clearFilters = () => {
    setSearchQuery('');
    setDiscountType('');
    setSortBy('expiry');
    setCurrentPage(1);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Available Coupons</h1>
          <p className="text-gray-600 mt-2">
            Browse and redeem coupons to save money on your purchases
          </p>
        </div>

        {/* Search and Filters */}
        <Card className="mb-8">
          <form onSubmit={handleSearch} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-2">
                <Input
                  label="Search Coupons"
                  placeholder="Search by title, description, or code..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Discount Type
                </label>
                <select
                  value={discountType}
                  onChange={(e) => setDiscountType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Types</option>
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed Amount</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="expiry">Expiry Date</option>
                  <option value="discount">Discount Value</option>
                  <option value="created">Recently Added</option>
                </select>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <Button type="submit" loading={loading}>
                Search
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={clearFilters}
              >
                Clear Filters
              </Button>
            </div>
          </form>
        </Card>

        {/* Toggle for Redeemed Coupons */}
        <div className="mb-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <p className="text-gray-600">
                Showing {coupons.length} available coupon{coupons.length !== 1 ? 's' : ''}
              </p>
              <button
                onClick={() => setShowRedeemed(!showRedeemed)}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                {showRedeemed ? 'Hide' : 'Show'} Redeemed Coupons
              </button>
              <button
                onClick={() => {
                  fetchCoupons();
                  if (showRedeemed) fetchRedeemedCoupons();
                }}
                className="text-sm text-green-600 hover:text-green-800 font-medium"
                disabled={loading}
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
            {searchQuery && (
              <p className="text-sm text-gray-500">
                Results for "{searchQuery}"
              </p>
            )}
          </div>
        </div>

        {/* Redeemed Coupons Section */}
        {showRedeemed && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Redeemed Coupons</h2>
            {loadingRedeemed ? (
              <div className="flex items-center justify-center h-32">
                <LoadingSpinner size="lg" />
              </div>
            ) : redeemedCoupons.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {redeemedCoupons.map((redemption) => (
                  <Card key={redemption.id} className="opacity-75">
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{redemption.coupon.title}</h3>
                          <p className="text-sm text-gray-600">{redemption.coupon.description}</p>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-medium text-gray-500">REDEEMED</span>
                          <div className="text-lg font-mono font-bold text-gray-400 bg-gray-100 px-2 py-1 rounded">
                            {redemption.coupon.code}
                          </div>
                        </div>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg mb-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-gray-400 mb-1">
                            {redemption.coupon.discount_type === 'percentage'
                              ? `${redemption.coupon.discount_value}% OFF`
                              : `$${redemption.coupon.discount_value} OFF`}
                          </div>
                          <div className="text-sm text-gray-500">
                            Redeemed on {new Date(redemption.redeemed_at).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <div className="text-center">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          Redeemed
                        </span>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <div className="text-center py-8">
                  <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No redeemed coupons</h3>
                  <p className="text-gray-500">You haven't redeemed any coupons yet.</p>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Coupons Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner size="lg" />
          </div>
        ) : coupons.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {coupons.map((coupon) => (
                <CouponCard
                  key={coupon.id}
                  coupon={coupon}
                  onRedeem={handleRedeem}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center">
                <nav className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>

                  <div className="flex items-center space-x-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      const page = i + 1;
                      return (
                        <button
                          key={page}
                          onClick={() => setCurrentPage(page)}
                          className={`px-3 py-2 text-sm font-medium rounded-md ${
                            currentPage === page
                              ? 'bg-blue-600 text-white'
                              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                          }`}
                        >
                          {page}
                        </button>
                      );
                    })}
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </nav>
              </div>
            )}
          </>
        ) : (
          <Card>
            <div className="text-center py-12">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No coupons found</h3>
              <p className="text-gray-500 mb-4">
                {searchQuery
                  ? `No coupons match your search for "${searchQuery}"`
                  : 'You have redeemed all available coupons! Check back later for new offers.'
                }
              </p>
              {searchQuery && (
                <Button
                  variant="outline"
                  onClick={clearFilters}
                >
                  Clear Search
                </Button>
              )}
            </div>
          </Card>
        )}

        {/* Quick Stats */}
        <div className="mt-8">
          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Coupon Tips</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-2">💡 Best Practices</h3>
                <p className="text-blue-700">
                  Check expiry dates and minimum order requirements before redeeming
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <h3 className="font-medium text-green-900 mb-2">💰 Save More</h3>
                <p className="text-green-700">
                  Combine multiple coupons when possible for maximum savings
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <h3 className="font-medium text-purple-900 mb-2">📱 Stay Updated</h3>
                <p className="text-purple-700">
                  New coupons are added regularly, check back often
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Coupons;
