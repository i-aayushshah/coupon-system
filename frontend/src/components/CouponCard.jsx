import React, { useState } from 'react';
import { couponAPI } from '../utils/api';
import { Button, Card } from './FormComponents';
import toast from 'react-hot-toast';

const CouponCard = ({ coupon, onRedeem }) => {
  const [loading, setLoading] = useState(false);

  const handleRedeem = () => {
    // Redirect to cart page with coupon code
    window.location.href = `/cart?coupon=${coupon.code}`;
  };

  const getDiscountText = () => {
    if (coupon.discount_type === 'percentage') {
      return `${coupon.discount_value}% OFF`;
    } else {
      return `$${coupon.discount_value} OFF`;
    }
  };

  const getExpiryStatus = () => {
    // Use days_remaining from backend if available, otherwise calculate
    if (coupon.days_remaining !== undefined) {
      const daysLeft = coupon.days_remaining;
      if (daysLeft < 0) return { text: 'Expired', color: 'text-red-600' };
      if (daysLeft <= 3) return { text: `${daysLeft} days left`, color: 'text-orange-600' };
      return { text: `${daysLeft} days left`, color: 'text-green-600' };
    }

    // Fallback calculation
    const now = new Date();
    const expiry = new Date(coupon.end_date);
    const daysLeft = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));

    if (daysLeft < 0) return { text: 'Expired', color: 'text-red-600' };
    if (daysLeft <= 3) return { text: `${daysLeft} days left`, color: 'text-orange-600' };
    return { text: `${daysLeft} days left`, color: 'text-green-600' };
  };

  const expiryStatus = getExpiryStatus();

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <div className="p-6">
        {/* Coupon Header */}
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{coupon.title}</h3>
            <p className="text-sm text-gray-600">{coupon.description}</p>
          </div>
          <div className="text-right">
            <span className="text-xs font-medium text-gray-500">CODE</span>
            <div className="text-lg font-mono font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded">
              {coupon.code}
            </div>
          </div>
        </div>

        {/* Discount Info */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {getDiscountText()}
            </div>
            {coupon.minimum_order_value && coupon.minimum_order_value > 0 && (
              <div className="text-sm text-gray-600">
                Min. order: ${coupon.minimum_order_value}
              </div>
            )}
          </div>
        </div>

        {/* Coupon Details */}
        <div className="space-y-2 mb-4">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Type:</span>
            <span className="font-medium capitalize">{coupon.discount_type}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Usage Limit:</span>
            <span className="font-medium">
              {coupon.max_uses === -1 ? 'Unlimited' : coupon.max_uses}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Used:</span>
            <span className="font-medium">{coupon.current_uses || 0}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Expires:</span>
            <span className={`font-medium ${expiryStatus.color}`}>
              {expiryStatus.text}
            </span>
          </div>
        </div>

        {/* Categories */}
        {coupon.applicable_categories && Array.isArray(coupon.applicable_categories) && coupon.applicable_categories.length > 0 && (
          <div className="mb-4">
            <div className="text-sm text-gray-600 mb-2">Applicable Categories:</div>
            <div className="flex flex-wrap gap-1">
              {coupon.applicable_categories.map((category, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
                >
                  {category}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action Button */}
        <Button
          onClick={handleRedeem}
          disabled={expiryStatus.text === 'Expired'}
          className="w-full"
          variant={expiryStatus.text === 'Expired' ? 'outline' : 'primary'}
        >
          {expiryStatus.text === 'Expired' ? 'Expired' : 'Use Coupon'}
        </Button>
      </div>
    </Card>
  );
};

export default CouponCard;
