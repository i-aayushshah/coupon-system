# Admin User Setup

## Admin Credentials

The system has been configured with a default admin user:

- **Email**: `aayushshah714@gmail.com`
- **Password**: `Aayush_123!`
- **Username**: `aayushshah`
- **Name**: Aayush Shah
- **Role**: Administrator

## Admin User Behavior

When the admin user logs in:

1. **Automatic Redirect**: They are automatically redirected to `/admin` (Admin Dashboard)
2. **Restricted Access**: They cannot access regular user pages (Dashboard, Profile, Coupons, etc.)
3. **Admin-Only Routes**: They can only access admin routes:
   - `/admin` - Admin Dashboard
   - `/admin/coupons` - Manage Coupons
   - `/admin/coupons/create` - Create New Coupon
   - `/admin/coupons/:id/edit` - Edit Coupon
   - `/admin/products` - Manage Products
   - `/admin/products/create` - Create New Product
   - `/admin/products/:id/edit` - Edit Product
   - `/admin/users` - User Management

## Admin User Management

### Creating/Updating Admin User

To create or update the admin user, run:

```bash
cd backend
python create_admin.py
```

### Verifying Admin User

To verify the admin user exists and check their details:

```bash
cd backend
python verify_admin.py
```

### Making Any User an Admin

To make any existing user an admin, use the test endpoint:

```bash
curl -X POST http://localhost:5000/api/test/make-admin/{user_id}
```

Replace `{user_id}` with the actual user ID.

## Security Notes

- The admin user has email verification bypassed for convenience
- Admin users are automatically redirected away from regular user pages
- The admin panel is protected by the `@admin_required` decorator
- Admin routes are wrapped with `AdminRoute` component for frontend protection

## Login Flow

1. Admin user enters credentials on login page
2. Backend validates credentials and returns `redirect_to: '/admin'`
3. Frontend automatically redirects to admin dashboard
4. Admin user can only access admin routes
5. If admin user tries to access regular user routes, they are redirected to admin dashboard
