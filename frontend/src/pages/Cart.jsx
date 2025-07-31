import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { cartAPI, couponAPI } from '../utils/api';
import DashboardLayout from '../components/DashboardLayout';
import { Input, Button, Card, LoadingSpinner } from '../components/FormComponents';
import toast from 'react-hot-toast';

const Cart = () => {
  const location = useLocation();
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updatingItem, setUpdatingItem] = useState(null);
  const [removingItem, setRemovingItem] = useState(null);
  const [couponCode, setCouponCode] = useState('');
  const [applyingCoupon, setApplyingCoupon] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const shownErrors = useRef(new Set());

  useEffect(() => {
    fetchCart();
  }, []);

          // Handle coupon code from URL parameter - just populate the input field
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const couponFromUrl = urlParams.get('coupon');

    if (couponFromUrl && !couponCode) {
      setCouponCode(couponFromUrl);
    }
  }, [location.search, couponCode]);



  const fetchCart = async () => {
    setLoading(true);
    try {
      const response = await cartAPI.getCart();
      setCart(response.cart);
    } catch (error) {
      console.error('Error fetching cart:', error);
      toast.error('Failed to load cart');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateQuantity = async (productId, newQuantity) => {
    if (newQuantity <= 0) return;

    setUpdatingItem(productId);
    try {
      await cartAPI.updateCart(productId, newQuantity);
      await fetchCart(); // Refresh cart
      toast.success('Cart updated successfully');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update cart');
    } finally {
      setUpdatingItem(null);
    }
  };

  const handleRemoveItem = async (productId) => {
    setRemovingItem(productId);
    try {
      await cartAPI.removeFromCart(productId);
      await fetchCart(); // Refresh cart
      toast.success('Item removed from cart');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to remove item');
    } finally {
      setRemovingItem(null);
    }
  };

  const handleApplyCoupon = async () => {
    if (!couponCode.trim()) {
      toast.error('Please enter a coupon code');
      return;
    }

    // Check if this coupon is already applied
    if (cart.applied_coupon && cart.applied_coupon.code === couponCode.trim().toUpperCase()) {
      toast.error('This coupon is already applied to your cart');
      setCouponCode('');
      return;
    }

    setApplyingCoupon(true);
    try {
      await cartAPI.applyCoupon(couponCode.trim());
      await fetchCart(); // Refresh cart to get updated totals
      toast.success('Coupon applied successfully!');
      setCouponCode('');
        } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to apply coupon';

      // Only show error if we haven't shown it before for this specific error
      if (!shownErrors.current.has(errorMessage)) {
        toast.error(errorMessage);
        shownErrors.current.add(errorMessage);
      }

      // If coupon is already applied, don't show it as an error
      if (errorMessage.includes('already applied')) {
        setCouponCode(''); // Clear the input
      }
    } finally {
      setApplyingCoupon(false);
    }
  };

  const handleRemoveCoupon = async () => {
    try {
      await cartAPI.removeCoupon();
      await fetchCart(); // Refresh cart to get updated totals
      toast.success('Coupon removed successfully!');
      shownErrors.current.clear(); // Clear shown errors
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to remove coupon');
    }
  };

  const handleCheckout = async () => {
    if (!cart || cart.items.length === 0) {
      toast.error('Your cart is empty');
      return;
    }

    setCheckoutLoading(true);
    try {
      const checkoutData = {
        shipping_address: {
          street: '123 Main St',
          city: 'New York',
          state: 'NY',
          zip_code: '10001',
          country: 'USA'
        },
        payment_method: 'credit_card',
        billing_address: {
          street: '123 Main St',
          city: 'New York',
          state: 'NY',
          zip_code: '10001',
          country: 'USA'
        }
      };

      await cartAPI.checkout(checkoutData);
      const successMessage = cart.applied_coupon
        ? `Order placed successfully! Coupon ${cart.applied_coupon.code} has been redeemed.`
        : 'Order placed successfully!';
      toast.success(successMessage);
      setCart(null); // Clear cart after successful checkout

      // If a coupon was redeemed, redirect to coupons page to show updated list
      if (cart.applied_coupon) {
        setTimeout(() => {
          window.location.href = '/coupons';
        }, 1500);
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to complete checkout');
    } finally {
      setCheckoutLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
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

  if (!cart || cart.items.length === 0) {
    return (
      <DashboardLayout>
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Your cart is empty</h3>
            <p className="text-gray-500 mb-6">
              Looks like you haven't added any items to your cart yet.
            </p>
            <Button onClick={() => window.location.href = '/products'}>
              Continue Shopping
            </Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
          <p className="text-gray-600 mt-2">
            Review your items and proceed to checkout
          </p>

          {/* Coupon Applied Indicator */}
          {cart.applied_coupon && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-green-800">
                    Coupon Applied: {cart.applied_coupon.code}
                  </p>
                  <p className="text-xs text-green-700">
                    {cart.applied_coupon.title} - {formatCurrency(cart.discount_amount)} discount
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <Card>
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Cart Items ({cart.items.length})</h2>

                <div className="space-y-4">
                  {cart.items.map((item) => (
                    <div key={item.product_id} className="flex items-center space-x-4 p-4 border rounded-lg">
                      {/* Product Image */}
                      <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
                        <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>

                      {/* Product Info */}
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{item.product_name}</h3>
                        <p className="text-sm text-gray-600">Price: {formatCurrency(item.product_price)}</p>
                      </div>

                      {/* Quantity Controls */}
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleUpdateQuantity(item.product_id, item.quantity - 1)}
                          disabled={updatingItem === item.product_id || item.quantity <= 1}
                        >
                          -
                        </Button>
                        <span className="w-12 text-center font-medium">{item.quantity}</span>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleUpdateQuantity(item.product_id, item.quantity + 1)}
                          disabled={updatingItem === item.product_id}
                        >
                          +
                        </Button>
                      </div>

                      {/* Line Total */}
                      <div className="text-right">
                        <p className="font-medium text-gray-900">{formatCurrency(item.line_total)}</p>
                      </div>

                      {/* Remove Button */}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRemoveItem(item.product_id)}
                        disabled={removingItem === item.product_id}
                        className="text-red-600 hover:text-red-700"
                      >
                        {removingItem === item.product_id ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <Card>
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Order Summary</h2>

                                 {/* Coupon Section */}
                                   <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Apply Coupon</h3>
                    <div className="flex space-x-2">
                      <Input
                        placeholder="Enter coupon code"
                        value={couponCode}
                        onChange={(e) => setCouponCode(e.target.value)}
                        className="flex-1"
                        disabled={cart.applied_coupon}
                      />
                      <Button
                        onClick={handleApplyCoupon}
                        loading={applyingCoupon}
                        disabled={applyingCoupon || !couponCode.trim() || cart.applied_coupon}
                        size="sm"
                      >
                        Apply
                      </Button>
                    </div>
                    {!cart.applied_coupon && (
                      <p className="text-xs text-gray-500 mt-1">
                        Enter a coupon code and click Apply to redeem
                      </p>
                    )}
                    {cart.applied_coupon && (
                      <p className="text-xs text-gray-500 mt-1">
                        Remove the current coupon to apply a different one
                      </p>
                    )}
                  {cart.applied_coupon && (
                    <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded-md">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-green-800">
                            Coupon applied: {cart.applied_coupon.code}
                          </p>
                          {cart.applied_coupon.title && (
                            <p className="text-xs text-green-700 mt-1">
                              {cart.applied_coupon.title}
                            </p>
                          )}
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={handleRemoveCoupon}
                          className="text-red-600 hover:text-red-700"
                        >
                          Remove
                        </Button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Totals */}
                <div className="space-y-3 border-t pt-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Subtotal:</span>
                    <span className="font-medium">{formatCurrency(cart.subtotal)}</span>
                  </div>

                  {cart.discount_amount > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Discount:</span>
                      <span className="font-medium text-green-600">-{formatCurrency(cart.discount_amount)}</span>
                    </div>
                  )}

                  <div className="flex justify-between text-lg font-semibold border-t pt-3">
                    <span>Total:</span>
                    <span>{formatCurrency(cart.final_total)}</span>
                  </div>
                </div>

                {/* Checkout Button */}
                <Button
                  onClick={handleCheckout}
                  loading={checkoutLoading}
                  disabled={checkoutLoading || cart.items.length === 0}
                  className="w-full mt-6"
                  size="lg"
                >
                  {checkoutLoading ? 'Processing...' : 'Proceed to Checkout'}
                </Button>

                {/* Continue Shopping */}
                <Button
                  variant="outline"
                  onClick={() => window.location.href = '/products'}
                  className="w-full mt-3"
                >
                  Continue Shopping
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Cart;
