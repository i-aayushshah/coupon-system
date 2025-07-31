import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { adminAPI } from '../../utils/api';
import { Input, Button, Card, LoadingSpinner, Textarea, Select, Checkbox } from '../../components/FormComponents';
import toast from 'react-hot-toast';

const CouponForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const isEditing = !!id && location.pathname.includes('/edit');

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [categories, setCategories] = useState([]);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
    reset
  } = useForm();

  const watchedValues = watch();

  useEffect(() => {
    fetchCategories();
    if (isEditing) {
      fetchCoupon();
    } else if (id && !location.pathname.includes('/edit')) {
      // Redirect to view page if accessing form without /edit
      navigate(`/admin/coupons/${id}`, { replace: true });
    }
  }, [isEditing, id, location.pathname, navigate]);

  const fetchCategories = async () => {
    try {
      const response = await adminAPI.getCategories();
      setCategories(response.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchCoupon = async () => {
    setLoading(true);
    try {
      const response = await adminAPI.getCoupon(id);
      const coupon = response.coupon;

      // Set form values
      Object.keys(coupon).forEach(key => {
        if (key === 'applicable_categories') {
          // Set individual category checkboxes
          const selectedCategories = coupon[key] || [];
          categories.forEach(category => {
            setValue(`category_${category}`, selectedCategories.includes(category));
          });
        } else {
          setValue(key, coupon[key]);
        }
      });
    } catch (error) {
      console.error('Error fetching coupon:', error);
      toast.error('Failed to load coupon');
    } finally {
      setLoading(false);
    }
  };

  const generateCouponCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < 8; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setValue('code', result);
  };

  const onSubmit = async (data) => {
    setSaving(true);
    try {
      // Collect selected categories
      const selectedCategories = categories.filter(category =>
        data[`category_${category}`] === true
      );

      // Prepare data
      const couponData = {
        ...data,
        applicable_categories: selectedCategories.length > 0 ? selectedCategories : [],
        discount_value: parseFloat(data.discount_value),
        max_uses: data.max_uses ? parseInt(data.max_uses) : null,
        minimum_order_value: data.minimum_order_value ? parseFloat(data.minimum_order_value) : null,
        maximum_discount_amount: data.maximum_discount_amount ? parseFloat(data.maximum_discount_amount) : null,
        is_public: data.is_public || false,
        first_time_user_only: data.first_time_user_only || false,
        is_active: true // Make it active when saving normally
      };

      if (isEditing) {
        await adminAPI.updateCoupon(id, couponData);
        toast.success('Coupon updated successfully!');
      } else {
        await adminAPI.createCoupon(couponData);
        toast.success('Coupon created successfully!');
      }

      navigate('/admin/coupons');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save coupon');
    } finally {
      setSaving(false);
    }
  };

  const saveAsDraft = async () => {
    setSaving(true);
    try {
      const data = watch();

      // Collect selected categories
      const selectedCategories = categories.filter(category =>
        data[`category_${category}`] === true
      );

      const couponData = {
        ...data,
        is_active: false, // Draft status
        applicable_categories: selectedCategories.length > 0 ? selectedCategories : [],
        discount_value: parseFloat(data.discount_value) || 0,
        max_uses: data.max_uses ? parseInt(data.max_uses) : null,
        minimum_order_value: data.minimum_order_value ? parseFloat(data.minimum_order_value) : null,
        maximum_discount_amount: data.maximum_discount_amount ? parseFloat(data.maximum_discount_amount) : null,
        is_public: data.is_public || false,
        first_time_user_only: data.first_time_user_only || false
      };

      if (isEditing) {
        await adminAPI.updateCoupon(id, couponData);
        toast.success('Coupon saved as draft!');
      } else {
        await adminAPI.createCoupon(couponData);
        toast.success('Coupon saved as draft!');
      }

      navigate('/admin/coupons');
    } catch (error) {
      toast.error('Failed to save draft');
    } finally {
      setSaving(false);
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
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {isEditing ? 'Edit Coupon' : 'Create New Coupon'}
            </h1>
            <p className="text-gray-600 mt-2">
              {isEditing ? 'Update your coupon details' : 'Create a new coupon campaign'}
            </p>
          </div>
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={() => setShowPreview(!showPreview)}
            >
              {showPreview ? 'Hide Preview' : 'Show Preview'}
            </Button>
            <Button
              variant="outline"
              onClick={saveAsDraft}
              loading={saving}
              disabled={saving}
            >
              Save as Draft
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2">
          <Card>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Basic Information */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Coupon Title"
                    error={errors.title?.message}
                    {...register('title', {
                      required: 'Coupon title is required',
                      minLength: {
                        value: 3,
                        message: 'Title must be at least 3 characters'
                      }
                    })}
                  />
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Coupon Code
                    </label>
                    <div className="flex space-x-2">
                      <Input
                        error={errors.code?.message}
                        {...register('code', {
                          required: 'Coupon code is required',
                          pattern: {
                            value: /^[A-Z0-9]+$/,
                            message: 'Code must contain only uppercase letters and numbers'
                          }
                        })}
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={generateCouponCode}
                      >
                        Generate
                      </Button>
                    </div>
                  </div>
                </div>

                <Textarea
                  label="Description"
                  error={errors.description?.message}
                  {...register('description', {
                    required: 'Description is required',
                    minLength: {
                      value: 10,
                      message: 'Description must be at least 10 characters'
                    }
                  })}
                />
              </div>

              {/* Discount Settings */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Discount Settings</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Select
                    label="Discount Type"
                    error={errors.discount_type?.message}
                    options={[
                      { value: '', label: 'Select Type' },
                      { value: 'percentage', label: 'Percentage' },
                      { value: 'fixed', label: 'Fixed Amount' }
                    ]}
                    {...register('discount_type', {
                      required: 'Discount type is required'
                    })}
                  />

                  <Input
                    label="Discount Value"
                    type="number"
                    step="0.01"
                    error={errors.discount_value?.message}
                    {...register('discount_value', {
                      required: 'Discount value is required',
                      min: {
                        value: 0,
                        message: 'Discount value must be positive'
                      }
                    })}
                  />

                  <Input
                    label="Minimum Order Value"
                    type="number"
                    step="0.01"
                    error={errors.minimum_order_value?.message}
                    {...register('minimum_order_value', {
                      min: {
                        value: 0,
                        message: 'Minimum order value must be positive'
                      }
                    })}
                  />

                  <Input
                    label="Maximum Discount Amount"
                    type="number"
                    step="0.01"
                    error={errors.maximum_discount_amount?.message}
                    {...register('maximum_discount_amount', {
                      min: {
                        value: 0,
                        message: 'Maximum discount amount must be positive'
                      }
                    })}
                  />
                </div>
              </div>

              {/* Usage Settings */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Usage Settings</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Maximum Uses"
                    type="number"
                    error={errors.max_uses?.message}
                    {...register('max_uses', {
                      min: {
                        value: 1,
                        message: 'Maximum uses must be at least 1'
                      }
                    })}
                  />

                  <Input
                    label="Start Date"
                    type="datetime-local"
                    error={errors.start_date?.message}
                    {...register('start_date', {
                      required: 'Start date is required'
                    })}
                  />

                  <Input
                    label="End Date"
                    type="datetime-local"
                    error={errors.end_date?.message}
                    {...register('end_date', {
                      required: 'End date is required'
                    })}
                  />
                </div>
              </div>

              {/* Restrictions */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Restrictions</h3>
                <div className="space-y-4">
                  <Checkbox
                    label="Public Coupon (visible to all users)"
                    {...register('is_public')}
                  />

                  <Checkbox
                    label="First-time users only"
                    {...register('first_time_user_only')}
                  />

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Applicable Categories
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {categories.map((category) => (
                        <label key={category} className="flex items-center">
                          <input
                            type="checkbox"
                            {...register(`category_${category}`)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="ml-2 text-sm text-gray-700">{category}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="flex justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/admin/coupons')}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  loading={saving}
                  disabled={saving}
                >
                  {isEditing ? 'Update Coupon' : 'Create Coupon'}
                </Button>
              </div>
            </form>
          </Card>
        </div>

        {/* Preview */}
        {showPreview && (
          <div className="lg:col-span-1">
            <Card>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Coupon Preview</h3>
              <div className="space-y-4">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
                  <div className="text-center">
                    <h4 className="text-xl font-bold mb-2">{watchedValues.title || 'Coupon Title'}</h4>
                    <div className="text-3xl font-bold mb-2">
                      {watchedValues.code || 'COUPON123'}
                    </div>
                    <p className="text-blue-100 mb-4">
                      {watchedValues.description || 'Coupon description will appear here'}
                    </p>
                    <div className="bg-white bg-opacity-20 rounded-lg p-3">
                      <div className="text-2xl font-bold">
                        {watchedValues.discount_type === 'percentage'
                          ? `${watchedValues.discount_value || 0}% OFF`
                          : `${formatCurrency(watchedValues.discount_value || 0)} OFF`
                        }
                      </div>
                      {watchedValues.minimum_order_value && (
                        <div className="text-sm">
                          Min. order: {formatCurrency(watchedValues.minimum_order_value)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium">{watchedValues.discount_type || 'Not set'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Public:</span>
                    <span className="font-medium">{watchedValues.is_public ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">First-time only:</span>
                    <span className="font-medium">{watchedValues.first_time_user_only ? 'Yes' : 'No'}</span>
                  </div>
                  {watchedValues.start_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Valid from:</span>
                      <span className="font-medium">{new Date(watchedValues.start_date).toLocaleDateString()}</span>
                    </div>
                  )}
                  {watchedValues.end_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Valid until:</span>
                      <span className="font-medium">{new Date(watchedValues.end_date).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default CouponForm;
