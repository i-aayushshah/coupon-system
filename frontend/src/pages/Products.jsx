import React, { useState, useEffect } from 'react';
import { productAPI, cartAPI } from '../utils/api';
import DashboardLayout from '../components/DashboardLayout';
import { Input, Button, Card, LoadingSpinner } from '../components/FormComponents';
import toast from 'react-hot-toast';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [productsInCart, setProductsInCart] = useState(new Set());
  const [checkingCart, setCheckingCart] = useState(false);

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, [searchQuery, selectedCategory, sortBy, currentPage]);

  // Check cart status when component mounts
  useEffect(() => {
    checkProductsInCart();
  }, []);

  const checkProductsInCart = async () => {
    setCheckingCart(true);
    try {
      const response = await cartAPI.getCart();
      const cartItems = response.cart?.items || [];
      const cartProductIds = new Set(cartItems.map(item => item.product_id));
      setProductsInCart(cartProductIds);
    } catch (error) {
      console.error('Error checking cart:', error);
      // If there's an error, assume no products are in cart
      setProductsInCart(new Set());
    } finally {
      setCheckingCart(false);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const response = await productAPI.getProducts(currentPage, 12, selectedCategory, sortBy);
      setProducts(response.products || []);
      setTotalPages(response.total_pages || 1);
    } catch (error) {
      console.error('Error fetching products:', error);
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await productAPI.getCategories();
      setCategories(response.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchProducts();
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('');
    setSortBy('name');
    setCurrentPage(1);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const ProductCard = ({ product }) => (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <div className="p-6">
        {/* Product Image */}
        <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-lg bg-gray-200 mb-4">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="h-48 w-full object-cover object-center"
            />
          ) : (
            <div className="h-48 w-full flex items-center justify-center bg-gray-200">
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 truncate">{product.name}</h3>
            {productsInCart.has(product.id) && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                In Cart
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600 line-clamp-2">{product.description}</p>

          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold text-gray-900">
              {formatCurrency(product.price)}
            </span>
            <span className="text-sm text-gray-500">SKU: {product.sku}</span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Category: {product.category}</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              product.stock_quantity > 0
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {product.stock_quantity > 0 ? 'In Stock' : 'Out of Stock'}
            </span>
          </div>

          {product.brand && (
            <div className="text-sm text-gray-600">
              Brand: {product.brand}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-2 pt-3">
            <Button
              onClick={() => setSelectedProduct(product)}
              variant="outline"
              size="sm"
              className="flex-1"
            >
              View Details
            </Button>
                                     <Button
              onClick={async () => {
                // Check if product is already in cart
                if (productsInCart.has(product.id)) {
                  toast.error(`${product.name} is already in your cart!`);
                  return;
                }

                try {
                  await cartAPI.addToCart(product.id, 1);
                  toast.success(`${product.name} added to cart!`);
                  // Update the products in cart set
                  setProductsInCart(prev => new Set([...prev, product.id]));
                  // Optionally redirect to cart after a short delay
                  setTimeout(() => {
                    if (window.confirm('Item added to cart! Would you like to view your cart?')) {
                      window.location.href = '/cart';
                    }
                  }, 1000);
                } catch (error) {
                  toast.error(error.response?.data?.error || 'Failed to add to cart');
                }
              }}
              disabled={product.stock_quantity <= 0 || checkingCart}
              size="sm"
              className="flex-1"
            >
              {checkingCart ? 'Checking...' : productsInCart.has(product.id) ? 'Already in Cart' : 'Add to Cart'}
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600 mt-2">
            Browse our product catalog and find great deals
          </p>
        </div>

        {/* Search and Filters */}
        <Card className="mb-8">
          <form onSubmit={handleSearch} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-2">
                <Input
                  label="Search Products"
                  placeholder="Search by name, description, or brand..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
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
                  <option value="name">Name</option>
                  <option value="price">Price</option>
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

        {/* Results Summary */}
        <div className="mb-6">
          <div className="flex justify-between items-center">
            <p className="text-gray-600">
              Showing {products.length} product{products.length !== 1 ? 's' : ''}
            </p>
            {searchQuery && (
              <p className="text-sm text-gray-500">
                Results for "{searchQuery}"
              </p>
            )}
          </div>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner size="lg" />
          </div>
        ) : products.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
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
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
              <p className="text-gray-500 mb-4">
                {searchQuery
                  ? `No products match your search for "${searchQuery}"`
                  : 'There are no products available at the moment.'
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

        {/* Product Details Modal */}
        {selectedProduct && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Product Details</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Name:</span>
                    <span className="font-medium">{selectedProduct.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Price:</span>
                    <span className="font-medium">{formatCurrency(selectedProduct.price)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Category:</span>
                    <span className="font-medium">{selectedProduct.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Brand:</span>
                    <span className="font-medium">{selectedProduct.brand || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">SKU:</span>
                    <span className="font-medium">{selectedProduct.sku}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Stock:</span>
                    <span className="font-medium">{selectedProduct.stock_quantity} units</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      selectedProduct.stock_quantity > 0
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {selectedProduct.stock_quantity > 0 ? 'In Stock' : 'Out of Stock'}
                    </span>
                  </div>
                  {selectedProduct.description && (
                    <div className="pt-3 border-t">
                      <span className="text-gray-600 block mb-2">Description:</span>
                      <p className="text-sm text-gray-700">{selectedProduct.description}</p>
                    </div>
                  )}
                </div>
                <div className="flex justify-end mt-6">
                  <Button
                    variant="outline"
                    onClick={() => setSelectedProduct(null)}
                  >
                    Close
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Products;
