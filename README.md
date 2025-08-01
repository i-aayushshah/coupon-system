# Coupon Management System

## Project Overview
A comprehensive e-commerce coupon management system with secure authentication, product management, cart/order integration, and advanced coupon features. Built with Flask (backend) and React (frontend), featuring JWT authentication, email verification, admin/user roles, and a complete product-to-order workflow.

## Project Structure
```
coupon-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── coupon.py
│   │   │   ├── redemption.py
│   │   │   ├── product.py
│   │   │   └── order.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── admin.py
│   │   │   ├── coupons.py
│   │   │   ├── user.py
│   │   │   ├── products.py
│   │   │   └── cart.py
│   │   ├── utils/
│   │   └── config.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── run.py
│   ├── create_admin.py
│   ├── verify_admin.py
│   └── migrate_add_last_login.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FormComponents.jsx
│   │   │   ├── AdminLayout.jsx
│   │   │   ├── AdminRoute.jsx
│   │   │   ├── ActivityNotification.jsx
│   │   │   └── CouponCard.jsx
│   │   ├── pages/
│   │   │   ├── admin/
│   │   │   │   ├── AdminDashboard.jsx
│   │   │   │   ├── ManageCoupons.jsx
│   │   │   │   ├── CouponForm.jsx
│   │   │   │   ├── ManageProducts.jsx
│   │   │   │   ├── ProductForm.jsx
│   │   │   │   ├── ImportProducts.jsx
│   │   │   │   ├── Users.jsx
│   │   │   │   ├── Activities.jsx
│   │   │   │   └── Settings.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Profile.jsx
│   │   │   ├── Coupons.jsx
│   │   │   ├── Products.jsx
│   │   │   ├── Cart.jsx
│   │   │   └── RedemptionHistory.jsx
│   │   ├── utils/
│   │   │   └── api.js
│   │   └── hooks/
│   │       └── useAuth.js
│   ├── public/
│   │   └── uploads/
│   ├── package.json
│   └── .env.example
├── sample_products_electronics.csv
├── sample_products_clothing.csv
├── ADMIN_SETUP.md
├── .gitignore
└── README.md
```

## Setup Instructions

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in values (see Environment Variables section)
6. `python run.py` to start Flask server (runs on http://localhost:5000)

### Frontend
1. `cd frontend`
2. `npm install`
3. Copy `.env.example` to `.env` and fill in values
4. `npm start` to run React app (runs on http://localhost:3000)

### Admin Setup
1. Run the admin creation script: `python create_admin.py`
2. Default admin credentials: `aayushshah714@gmail.com` / `Aayush_123!`
3. Admin users will be automatically redirected to `/admin` dashboard

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Mail, Flask-CORS, python-dotenv, bcrypt, SQLite
- **Frontend:** React, TailwindCSS, Axios, React Router DOM, React Hook Form, React Hot Toast

## Features

### 🔐 Authentication & Security
- **JWT-based authentication** with secure token management
- **Email verification** required for login with resend functionality
- **Password reset** with secure token-based flow
- **Role-based access control** (Admin/User)
- **Password hashing** with bcrypt
- **Account deletion** with password verification
- **Last login tracking** for user activity monitoring

### 🏪 Enhanced Product Management System
- **Complete product CRUD** operations (Create, Read, Update, Delete)
- **Product categories** and brand management
- **Stock quantity tracking** with low stock alerts
- **SKU management** with uniqueness validation
- **Bulk product upload** via CSV with enhanced error handling
- **Product images** with local storage and preview
- **Minimum order values** per product
- **Advanced search and filtering** across all product fields
- **Real-time stock status** indicators

### 🛒 Cart & Order System
- **Shopping cart management** with add/update/remove items
- **Stock validation** during cart operations
- **Order processing** with complete checkout flow
- **Order history** and status tracking
- **Order items** with quantity and pricing
- **Shipping address** and payment method tracking
- **Duplicate product prevention** in cart

### 🎫 Enhanced Coupon System
- **Public and private coupons** with visibility controls
- **Advanced coupon validation:**
  - Date range validation (start/end dates)
  - Usage limits (max uses vs current uses)
  - Minimum order value requirements
  - Applicable product categories
  - Maximum discount caps for percentage coupons
  - First-time user restrictions
- **Multiple discount types:** Percentage and fixed amount
- **Double redemption prevention** with database constraints
- **Coupon search and filtering** by code, title, discount type
- **Real-time coupon validation** without redemption
- **Coupon application flow** with redirect to cart

### 👤 User Features
- **Profile management** (view/update personal information)
- **Password change** with current password verification
- **User dashboard** with comprehensive statistics
- **Redemption history** with order details and date filtering
- **Savings tracking** and analytics
- **Favorite categories** and spending patterns
- **Monthly redemption trends**
- **Forgot password** integration

### 👨‍💼 Enhanced Admin Panel
- **Complete coupon management** (CRUD operations)
- **Product management** with bulk operations and advanced search
- **User management** with role and status controls
- **Comprehensive dashboard** with real-time analytics:
  - Total users, active coupons, total redemptions, total revenue
  - Active/inactive statistics
  - Most redeemed coupons
  - Top selling products
  - Recent redemptions with order context
  - Low stock product alerts
- **Activities monitoring** with pagination and filtering
- **Admin settings** with profile and password management
- **Real-time notifications** for system activities
- **Bulk product upload** via CSV with enhanced validation
- **Image upload** functionality for products

### 🔍 Advanced Search & Filtering
- **Product search** across name, description, SKU, brand, category
- **Real-time search** with debounced input
- **Category filtering** with dynamic dropdown
- **Status filtering** (active/inactive)
- **Clear filters** functionality
- **Pagination** with server-side processing

### 📊 Analytics & Reporting
- **User analytics:** Redemption patterns, savings, category preferences
- **Admin analytics:** Revenue tracking, product performance, coupon effectiveness
- **Real-time statistics** for dashboards
- **Historical data** for trend analysis
- **Activity monitoring** with detailed logs

## API Overview

### Authentication Endpoints
- `POST /api/auth/register` — Register new user
- `POST /api/auth/login` — Login (with resend verification support)
- `POST /api/auth/verify-email` — Verify email address
- `POST /api/auth/resend-verification` — Resend verification email
- `POST /api/auth/forgot-password` — Request password reset
- `POST /api/auth/reset-password` — Reset password with token
- `GET /api/auth/me` — Get current user profile (enhanced with phone, email_verified, last_login)

### Admin Endpoints
#### Coupon Management
- `POST /api/admin/coupons` — Create new coupon with enhanced features
- `GET /api/admin/coupons` — List all coupons with pagination and enhanced fields
- `GET /api/admin/coupons/<id>` — Get specific coupon details
- `PUT /api/admin/coupons/<id>` — Update coupon (including enhanced fields)
- `DELETE /api/admin/coupons/<id>` — Delete coupon
- `GET /api/admin/coupons/<id>/redemptions` — View coupon redemption history

#### Product Management
- `POST /api/admin/products` — Create new product
- `GET /api/admin/products` — List all products with pagination, search, and filters
- `GET /api/admin/products/<id>` — Get specific product details
- `PUT /api/admin/products/<id>` — Update product
- `DELETE /api/admin/products/<id>` — Delete product
- `POST /api/admin/products/bulk-upload` — Bulk upload products via CSV with enhanced error handling
- `POST /api/admin/upload-image` — Upload product images

#### User Management
- `GET /api/admin/users` — List all users with pagination and search
- `GET /api/admin/users/<id>` — Get specific user details
- `PUT /api/admin/users/<id>/role` — Update user role
- `PUT /api/admin/users/<id>/status` — Update user status
- `GET /api/admin/users/<id>/stats` — Get user statistics

#### Analytics & Activities
- `GET /api/admin/dashboard` — Comprehensive admin dashboard with enhanced stats
- `GET /api/admin/activities` — Get system activities with pagination and filtering
- `GET /api/admin/categories` — Get unique product categories

#### Admin Profile
- `PUT /api/admin/profile` — Update admin profile
- `PUT /api/admin/profile/password` — Update admin password

### Public Coupon Endpoints
- `GET /api/coupons/public` — List public active coupons with enhanced fields
- `GET /api/coupons/validate/<code>` — Validate coupon without redeeming
- `POST /api/coupons/redeem` — Redeem coupon with enhanced validation
- `GET /api/coupons/search` — Search coupons with filters and enhanced fields
- `GET /api/coupons/user/redemptions` — User's redemption history with order details

### Product Endpoints
- `GET /api/products` — List active products with filters and sorting
- `GET /api/products/<id>` — Get product details
- `GET /api/products/search` — Search products by name, description, brand, SKU
- `GET /api/products/categories` — List unique product categories
- `POST /api/products/calculate-discount` — Calculate discount for cart and coupon

### Cart & Order Endpoints
- `POST /api/cart/add` — Add product to cart
- `GET /api/cart` — Get current cart
- `PUT /api/cart/update` — Update cart quantities
- `DELETE /api/cart/remove/<product_id>` — Remove item from cart
- `POST /api/cart/apply-coupon` — Apply coupon to cart with advanced validation
- `POST /api/cart/checkout` — Complete order with coupon redemption

### User Endpoints
- `GET /api/user/profile` — Get user profile
- `PUT /api/user/profile` — Update profile information
- `POST /api/user/change-password` — Change password with verification
- `POST /api/user/delete-account` — Delete account with password verification
- `GET /api/user/stats` — Enhanced user statistics with order data
- `GET /api/user/dashboard` — Enhanced user dashboard with order context
- `GET /api/user/redemptions` — User redemption history with date filtering

## Enhanced Coupon Features

### Advanced Validation Rules
- **Minimum Order Value:** Coupons can require a minimum cart total
- **Applicable Categories:** Coupons can be restricted to specific product categories
- **Maximum Discount Cap:** Percentage coupons can have a maximum discount limit
- **First-Time User Only:** Coupons can be restricted to new users only
- **Date Range Validation:** Start and end date enforcement
- **Usage Limits:** Maximum uses with current usage tracking
- **Double Redemption Prevention:** Database-level constraints

### Enhanced Response Data
All coupon endpoints now return enhanced fields:
```json
{
  "minimum_order_value": 50.00,
  "applicable_categories": ["Electronics", "Gadgets"],
  "maximum_discount_amount": 25.00,
  "first_time_user_only": false
}
```

## Recent Improvements & Bug Fixes

### 🔧 Enhanced CSV Import System
- **Improved error handling** with detailed row-specific error messages
- **Safe data parsing** for all numeric fields (price, stock_quantity, minimum_order_value)
- **Better validation** for required fields and data formats
- **Database transaction safety** with proper commit/rollback handling
- **Debug logging** for import progress tracking

### 🔍 Advanced Search & Filtering
- **Real-time search** with 500ms debounced input
- **Multi-field search** across product name, description, SKU, brand, category
- **Server-side filtering** for better performance
- **Category and status filters** with dynamic dropdowns
- **Clear filters** functionality for easy reset

### 👨‍💼 Enhanced Admin Panel
- **Activity monitoring** with pagination and filtering
- **Admin settings page** with profile and password management
- **Real-time notifications** for system activities
- **Enhanced user management** with role and status controls
- **Improved dashboard** with accurate statistics

### 🛒 Cart & Checkout Improvements
- **Duplicate product prevention** in cart
- **Enhanced coupon application** flow with redirect to cart
- **Better error handling** for checkout process
- **Improved toast notifications** with proper error messages

### 🔐 Security Enhancements
- **Consistent password hashing** with bcrypt
- **Last login tracking** for user activity
- **Enhanced profile management** with phone number support
- **Forgot password** integration in admin settings

### 📱 UI/UX Improvements
- **Responsive design** for all admin pages
- **Loading states** and error handling
- **Toast notifications** for user feedback
- **Enhanced form validation** and error messages
- **Better pagination** with server-side processing

## Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///coupon.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000
```

## Testing

### PowerShell Testing Commands
```powershell
# Register a new user
$registerData = @{
    username = "testuser"
    email = "test@example.com"
    password = "Password123"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/register" -Method POST -Body $registerData -ContentType "application/json"

# Login
$loginData = @{
    email = "test@example.com"
    password = "Password123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method POST -Body $loginData -ContentType "application/json"
$token = $response.access_token

# Create enhanced coupon (Admin)
$couponData = @{
    code = "SAVE25"
    title = "25% Off Electronics"
    description = "Get 25% off electronics with minimum $100 purchase"
    discount_type = "percentage"
    discount_value = 25
    minimum_order_value = 100
    maximum_discount_amount = 50
    applicable_categories = @("Electronics", "Gadgets")
    first_time_user_only = $false
    is_public = $true
    max_uses = 200
    start_date = "2024-01-01"
    end_date = "2024-12-31"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/admin/coupons" -Method POST -Body $couponData -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"}

# Test enhanced coupon validation
Invoke-RestMethod -Uri "http://localhost:5000/api/coupons/validate/SAVE25" -Method GET

# Test cart operations
$cartData = @{
    product_id = 1
    quantity = 2
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/cart/add" -Method POST -Body $cartData -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"}
```

## Security & Best Practices

### Authentication & Authorization
- **JWT tokens** for all protected routes
- **Role-based access control** with admin middleware
- **Email verification** required for login
- **Password hashing** with bcrypt
- **Token expiration** handling
- **Last login tracking** for security monitoring

### Data Validation
- **Input sanitization** for all user inputs
- **Type validation** for enhanced coupon fields
- **Business rule validation** (date ranges, discount limits)
- **Database constraints** for data integrity
- **CSV import validation** with detailed error reporting

### Error Handling
- **Comprehensive error messages** for validation failures
- **Proper HTTP status codes** for different error types
- **Transaction rollback** for failed operations
- **Graceful degradation** for missing data
- **Enhanced error logging** for debugging

### Production Considerations
- **Rate limiting** recommended for production
- **Database indexing** for performance
- **Logging and monitoring** for system health
- **Backup strategies** for data protection
- **HTTPS enforcement** for security
- **Image upload security** with file validation

## Database Schema

### Core Tables
- **users:** User accounts with authentication data and last_login tracking
- **coupons:** Coupon definitions with enhanced fields
- **redemptions:** Coupon usage tracking with order context
- **products:** Product catalog with inventory management
- **orders:** Order records with totals and status
- **order_items:** Individual items in orders

### Enhanced Fields
- **Coupons:** minimum_order_value, applicable_categories, maximum_discount_amount, first_time_user_only
- **Redemptions:** order_id, original_amount, final_amount, products_applied_to
- **Products:** category, brand, sku, stock_quantity, minimum_order_value, image_url
- **Users:** phone_number, email_verified, last_login

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note:** This system is designed for educational and development purposes. For production use, additional security measures, monitoring, and scalability considerations should be implemented.
