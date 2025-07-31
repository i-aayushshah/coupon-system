import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import { adminAPI } from '../../utils/api';
import { Input, Button, Card, LoadingSpinner, Textarea, Select, Checkbox } from '../../components/FormComponents';
import toast from 'react-hot-toast';

const ProductForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = !!id;

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [categories, setCategories] = useState([]);
  const [imagePreview, setImagePreview] = useState('');

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
      fetchProduct();
    }
  }, [isEditing, id]);

  const fetchCategories = async () => {
    try {
      const response = await adminAPI.getCategories();
      setCategories(response.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchProduct = async () => {
    setLoading(true);
    try {
      const response = await adminAPI.getProduct(id);
      const product = response.product;

      // Set form values
      Object.keys(product).forEach(key => {
        setValue(key, product[key]);
      });

      if (product.image_url) {
        setImagePreview(product.image_url);
      }
    } catch (error) {
      console.error('Error fetching product:', error);
      toast.error('Failed to load product');
    } finally {
      setLoading(false);
    }
  };

  const generateSKU = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < 8; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setValue('sku', result);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const onSubmit = async (data) => {
    setSaving(true);
    try {
      // Prepare data
      const productData = {
        ...data,
        price: parseFloat(data.price),
        stock_quantity: parseInt(data.stock_quantity),
        minimum_order_value: data.minimum_order_value ? parseFloat(data.minimum_order_value) : null,
        is_active: data.is_active || false
      };

      if (isEditing) {
        await adminAPI.updateProduct(id, productData);
        toast.success('Product updated successfully!');
      } else {
        await adminAPI.createProduct(productData);
        toast.success('Product created successfully!');
      }

      navigate('/admin/products');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save product');
    } finally {
      setSaving(false);
    }
  };

  const saveAsDraft = async () => {
    setSaving(true);
    try {
      const data = watch();
      const productData = {
        ...data,
        is_active: false, // Draft status
        price: parseFloat(data.price) || 0,
        stock_quantity: parseInt(data.stock_quantity) || 0,
        minimum_order_value: data.minimum_order_value ? parseFloat(data.minimum_order_value) : null,
        is_active: false
      };

      if (isEditing) {
        await adminAPI.updateProduct(id, productData);
        toast.success('Product saved as draft!');
      } else {
        await adminAPI.createProduct(productData);
        toast.success('Product saved as draft!');
      }

      navigate('/admin/products');
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
              {isEditing ? 'Edit Product' : 'Create New Product'}
            </h1>
            <p className="text-gray-600 mt-2">
              {isEditing ? 'Update your product details' : 'Add a new product to your catalog'}
            </p>
          </div>
          <div className="flex space-x-3">
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
                    label="Product Name"
                    error={errors.name?.message}
                    {...register('name', {
                      required: 'Product name is required',
                      minLength: {
                        value: 3,
                        message: 'Name must be at least 3 characters'
                      }
                    })}
                  />
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      SKU
                    </label>
                    <div className="flex space-x-2">
                      <Input
                        error={errors.sku?.message}
                        {...register('sku', {
                          required: 'SKU is required',
                          pattern: {
                            value: /^[A-Z0-9]+$/,
                            message: 'SKU must contain only uppercase letters and numbers'
                          }
                        })}
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={generateSKU}
                      >
                        Generate
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <Input
                    label="Brand"
                    error={errors.brand?.message}
                    {...register('brand', {
                      required: 'Brand is required'
                    })}
                  />
                  <Select
                    label="Category"
                    error={errors.category?.message}
                    {...register('category', {
                      required: 'Category is required'
                    })}
                  >
                    <option value="">Select Category</option>
                    {categories.map((category) => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </Select>
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

              {/* Pricing */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Pricing & Inventory</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Input
                    label="Price"
                    type="number"
                    step="0.01"
                    error={errors.price?.message}
                    {...register('price', {
                      required: 'Price is required',
                      min: {
                        value: 0,
                        message: 'Price must be positive'
                      }
                    })}
                  />
                  <Input
                    label="Stock Quantity"
                    type="number"
                    error={errors.stock_quantity?.message}
                    {...register('stock_quantity', {
                      required: 'Stock quantity is required',
                      min: {
                        value: 0,
                        message: 'Stock quantity must be non-negative'
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
                </div>
              </div>

              {/* Image Upload */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Product Image</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Product Image URL
                    </label>
                    <Input
                      type="url"
                      placeholder="https://example.com/image.jpg"
                      error={errors.image_url?.message}
                      {...register('image_url', {
                        pattern: {
                          value: /^https?:\/\/.+/,
                          message: 'Please enter a valid URL'
                        }
                      })}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Or Upload Image
                    </label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                  </div>

                  {imagePreview && (
                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Image Preview
                      </label>
                      <div className="w-32 h-32 border-2 border-gray-300 rounded-lg overflow-hidden">
                        <img
                          src={imagePreview}
                          alt="Product preview"
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Settings */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Product Settings</h3>
                <div className="space-y-4">
                  <Checkbox
                    label="Active Product (visible to customers)"
                    {...register('is_active')}
                  />

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Product Status
                    </label>
                    <div className="text-sm text-gray-600">
                      {watchedValues.is_active ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Active - Product is visible to customers
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Draft - Product is not visible to customers
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="flex justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/admin/products')}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  loading={saving}
                  disabled={saving}
                >
                  {isEditing ? 'Update Product' : 'Create Product'}
                </Button>
              </div>
            </form>
          </Card>
        </div>

        {/* Preview */}
        <div className="lg:col-span-1">
          <Card>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Product Preview</h3>
            <div className="space-y-4">
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-lg bg-gray-200 mb-4">
                  {imagePreview ? (
                    <img
                      src={imagePreview}
                      alt="Product preview"
                      className="w-full h-48 object-cover rounded-lg"
                    />
                  ) : (
                    <div className="w-full h-48 bg-gray-200 rounded-lg flex items-center justify-center">
                      <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <h4 className="text-lg font-semibold text-gray-900">
                    {watchedValues.name || 'Product Name'}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {watchedValues.description || 'Product description will appear here'}
                  </p>

                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-gray-900">
                      {watchedValues.price ? formatCurrency(watchedValues.price) : '$0.00'}
                    </span>
                    <span className="text-sm text-gray-500">
                      SKU: {watchedValues.sku || 'N/A'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Brand: {watchedValues.brand || 'N/A'}</span>
                    <span className="text-gray-600">Category: {watchedValues.category || 'N/A'}</span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Stock: {watchedValues.stock_quantity || 0}</span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      watchedValues.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {watchedValues.is_active ? 'Active' : 'Draft'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="font-medium">{watchedValues.is_active ? 'Active' : 'Draft'}</span>
                </div>
                {watchedValues.minimum_order_value && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Min. Order:</span>
                    <span className="font-medium">{formatCurrency(watchedValues.minimum_order_value)}</span>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ProductForm;
