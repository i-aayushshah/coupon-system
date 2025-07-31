# Coupon Management System API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Error Responses
All endpoints may return the following error responses:

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server error

## Authentication Endpoints

### Register User
**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "Password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully. Please check your email to verify your account.",
  "user_id": 1
}
```

### Login
**POST** `/auth/login`

Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "Password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_admin": false,
    "email_verified": true
  }
}
```

### Verify Email
**POST** `/auth/verify-email`

Verify user's email address.

**Request Body:**
```json
{
  "token": "verification-token-from-email"
}
```

**Response (200 OK):**
```json
{
  "message": "Email verified successfully"
}
```

### Resend Verification Email
**POST** `/auth/resend-verification`

Resend email verification link.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Verification email sent"
}
```

### Forgot Password
**POST** `/auth/forgot-password`

Request password reset email.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset email sent"
}
```

### Reset Password
**POST** `/auth/reset-password`

Reset password using token from email.

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "NewPassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

### Get User Profile
**GET** `/auth/me`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "1234567890",
    "is_admin": false,
    "email_verified": true,
    "last_login": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

## Coupon Endpoints

### Get Public Coupons
**GET** `/coupons/public`

Get all public coupons available to users.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)

**Response (200 OK):**
```json
{
  "coupons": [
    {
      "id": 1,
      "code": "SAVE20",
      "title": "20% Off",
      "description": "Get 20% off your purchase",
      "discount_type": "percentage",
      "discount_value": 20,
      "minimum_order_value": 50.0,
      "applicable_categories": ["Electronics", "Clothing"],
      "maximum_discount_amount": 25.0,
      "first_time_user_only": false,
      "max_uses": 100,
      "current_uses": 0,
      "days_remaining": 30
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1
  }
}
```

### Validate Coupon
**GET** `/coupons/validate/{code}`

Validate a coupon code.

**Response (200 OK):**
```json
{
  "valid": true,
  "coupon": {
    "id": 1,
    "code": "SAVE20",
    "title": "20% Off",
    "description": "Get 20% off your purchase",
    "discount_type": "percentage",
    "discount_value": 20,
    "minimum_order_value": 50.0,
    "applicable_categories": ["Electronics", "Clothing"],
    "maximum_discount_amount": 25.0,
    "first_time_user_only": false
  }
}
```

### Search Coupons
**GET** `/coupons/search`

Search for coupons.

**Query Parameters:**
- `q` (optional): Search query
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)

**Response (200 OK):**
```json
{
  "coupons": [
    {
      "id": 1,
      "code": "SAVE20",
      "title": "20% Off Electronics",
      "description": "Get 20% off electronics",
      "discount_type": "percentage",
      "discount_value": 20,
      "minimum_order_value": 50.0,
      "applicable_categories": ["Electronics"],
      "maximum_discount_amount": 25.0,
      "first_time_user_only": false,
      "max_uses": 100,
      "current_uses": 0,
      "days_remaining": 30
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1
  }
}
```

### Redeem Coupon
**POST** `/coupons/redeem`

Redeem a coupon for an order.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "coupon_code": "SAVE20",
  "order_id": 1
}
```

**Response (200 OK):**
```json
{
  "redemption": {
    "id": 1,
    "user_id": 1,
    "coupon_id": 1,
    "order_id": 1,
    "original_amount": 100.0,
    "final_amount": 80.0,
    "discount_amount": 20.0,
    "products_applied_to": ["Electronics"],
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### Get User Redemptions
**GET** `/coupons/user/redemptions`

Get current user's coupon redemptions.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)

**Response (200 OK):**
```json
{
  "redemptions": [
    {
      "id": 1,
      "coupon_code": "SAVE20",
      "coupon_title": "20% Off",
      "original_amount": 100.0,
      "final_amount": 80.0,
      "discount_amount": 20.0,
      "products_applied_to": ["Electronics"],
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1
  }
}
```

## Product Endpoints

### Get Products
**GET** `/products`

Get all products.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `category` (optional): Filter by category
- `sort_by` (optional): Sort field (name, price, created_at)
- `sort_order` (optional): Sort order (asc, desc)

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": 1,
      "name": "iPhone 13",
      "description": "Latest iPhone with advanced features",
      "price": 999.99,
      "category": "Electronics",
      "brand": "Apple",
      "sku": "IPHONE13-001",
      "stock_quantity": 50,
      "is_active": true,
      "image_url": "/uploads/iphone13.jpg",
      "minimum_order_value": 10.0,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1
  }
}
```

### Get Product
**GET** `/products/{id}`

Get a specific product.

**Response (200 OK):**
```json
{
  "product": {
    "id": 1,
    "name": "iPhone 13",
    "description": "Latest iPhone with advanced features",
    "price": 999.99,
    "category": "Electronics",
    "brand": "Apple",
    "sku": "IPHONE13-001",
    "stock_quantity": 50,
    "is_active": true,
    "image_url": "/uploads/iphone13.jpg",
    "minimum_order_value": 10.0,
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### Search Products
**GET** `/products/search`

Search for products.

**Query Parameters:**
- `q` (required): Search query
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": 1,
      "name": "iPhone 13",
      "description": "Latest iPhone with advanced features",
      "price": 999.99,
      "category": "Electronics",
      "brand": "Apple",
      "sku": "IPHONE13-001",
      "stock_quantity": 50,
      "is_active": true,
      "image_url": "/uploads/iphone13.jpg",
      "minimum_order_value": 10.0,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1
  }
}
```

### Get Categories
**GET** `/products/categories`

Get all product categories.

**Response (200 OK):**
```json
{
  "categories": ["Electronics", "Clothing", "Books", "Home & Garden"]
}
```

## Cart Endpoints

### Add to Cart
**POST** `/cart/add`

Add a product to cart.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response (200 OK):**
```json
{
  "message": "Product added to cart",
  "cart": {
    "items": [
      {
        "product_id": 1,
        "product_name": "iPhone 13",
        "product_price": 999.99,
        "quantity": 2,
        "total_price": 1999.98
      }
    ],
    "total_items": 2,
    "subtotal": 1999.98,
    "applied_coupon": null,
    "discount_amount": 0,
    "total_amount": 1999.98
  }
}
```

### Get Cart
**GET** `/cart`

Get current user's cart.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "cart": {
    "items": [
      {
        "product_id": 1,
        "product_name": "iPhone 13",
        "product_price": 999.99,
        "quantity": 2,
        "total_price": 1999.98
      }
    ],
    "total_items": 2,
    "subtotal": 1999.98,
    "applied_coupon": null,
    "discount_amount": 0,
    "total_amount": 1999.98
  }
}
```

### Update Cart
**PUT** `/cart/update`

Update cart items.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "updates": [
    {
      "product_id": 1,
      "quantity": 3
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "message": "Cart updated successfully",
  "cart": {
    "items": [
      {
        "product_id": 1,
        "product_name": "iPhone 13",
        "product_price": 999.99,
        "quantity": 3,
        "total_price": 2999.97
      }
    ],
    "total_items": 3,
    "subtotal": 2999.97,
    "applied_coupon": null,
    "discount_amount": 0,
    "total_amount": 2999.97
  }
}
```

### Remove from Cart
**DELETE** `/cart/remove/{product_id}`

Remove a product from cart.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Product removed from cart"
}
```

### Apply Coupon to Cart
**POST** `/cart/apply-coupon`

Apply a coupon to the cart.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "coupon_code": "SAVE20"
}
```

**Response (200 OK):**
```json
{
  "message": "Coupon applied successfully",
  "cart": {
    "items": [
      {
        "product_id": 1,
        "product_name": "iPhone 13",
        "product_price": 999.99,
        "quantity": 2,
        "total_price": 1999.98
      }
    ],
    "total_items": 2,
    "subtotal": 1999.98,
    "applied_coupon": {
      "code": "SAVE20",
      "title": "20% Off",
      "discount_amount": 399.96
    },
    "discount_amount": 399.96,
    "total_amount": 1599.98
  }
}
```

### Checkout
**POST** `/cart/checkout`

Complete the checkout process.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "shipping_address": "123 Main St, City, State 12345",
  "payment_method": "credit_card"
}
```

**Response (200 OK):**
```json
{
  "message": "Order placed successfully",
  "order": {
    "id": 1,
    "user_id": 1,
    "total_amount": 1599.98,
    "status": "pending",
    "shipping_address": "123 Main St, City, State 12345",
    "payment_method": "credit_card",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

## Admin Endpoints

### Get Dashboard Stats
**GET** `/admin/dashboard`

Get admin dashboard statistics.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "stats": {
    "total_users": 100,
    "total_coupons": 50,
    "total_products": 200,
    "total_orders": 150,
    "total_revenue": 15000.00,
    "total_redemptions": 75,
    "total_discounts_given": 1500.00,
    "active_coupons": 25,
    "recent_activities": [
      {
        "id": 1,
        "type": "user_registration",
        "description": "New user registered: john@example.com",
        "created_at": "2024-01-01T12:00:00Z"
      }
    ]
  }
}
```

### Get Users
**GET** `/admin/users`

Get all users (admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `search` (optional): Search query
- `status` (optional): Filter by status (active, inactive)

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "1234567890",
      "is_admin": false,
      "email_verified": true,
      "last_login": "2024-01-01T12:00:00Z",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1
  }
}
```

### Update User Status
**PUT** `/admin/users/{id}/status`

Update user status (admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "email_verified": true
}
```

**Response (200 OK):**
```json
{
  "message": "User status updated successfully"
}
```

### Get Activities
**GET** `/admin/activities`

Get system activities (admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `type` (optional): Filter by activity type
- `start_date` (optional): Filter from date
- `end_date` (optional): Filter to date

**Response (200 OK):**
```json
{
  "activities": [
    {
      "id": 1,
      "type": "user_registration",
      "description": "New user registered: john@example.com",
      "user_id": 1,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 10,
    "total": 1
  }
}
```

### Get Admin Profile
**GET** `/admin/profile`

Get admin profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "profile": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "phone_number": "1234567890",
    "is_admin": true,
    "email_verified": true,
    "last_login": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### Update Admin Profile
**PUT** `/admin/profile`

Update admin profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "first_name": "Admin",
  "last_name": "User",
  "phone_number": "1234567890"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "profile": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "phone_number": "1234567890",
    "is_admin": true,
    "email_verified": true,
    "last_login": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### Update Admin Password
**PUT** `/admin/profile/password`

Update admin password.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "current_password": "OldPassword123",
  "new_password": "NewPassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password updated successfully"
}
```

## File Upload Endpoints

### Upload Product Image
**POST** `/admin/products/upload-image`

Upload product image (admin only).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body:**
```
image: <file>
```

**Response (200 OK):**
```json
{
  "message": "Image uploaded successfully",
  "image_url": "/uploads/product_123.jpg"
}
```

### Bulk Upload Products
**POST** `/admin/products/bulk-upload`

Upload products via CSV (admin only).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <csv-file>
```

**Response (200 OK):**
```json
{
  "message": "Products uploaded successfully",
  "success_count": 10,
  "error_count": 0,
  "errors": []
}
```

## Health Check

### Health Check
**GET** `/health`

Check API health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 5 requests per minute
- **General endpoints**: 100 requests per minute
- **Admin endpoints**: 50 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

Most list endpoints support pagination with the following parameters:

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 10,
    "total": 50
  }
}
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

Common error codes:
- `VALIDATION_ERROR`: Invalid request data
- `AUTHENTICATION_ERROR`: Invalid credentials
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource already exists
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error
