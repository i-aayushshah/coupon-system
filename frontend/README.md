# Coupon System Frontend

A React-based frontend for the Coupon Management System with complete authentication flow.

## Features

### 🔐 Authentication System
- **Login Page** - Email/password authentication with remember me option
- **Register Page** - Complete user registration with form validation
- **Forgot Password** - Password reset via email
- **Reset Password** - Token-based password reset
- **Email Verification** - Email verification with resend functionality
- **Protected Routes** - Route protection with authentication checks

### 🎨 UI Components
- **Modern Design** - Clean, responsive design with TailwindCSS
- **Form Components** - Reusable form elements with validation
- **Loading States** - Loading spinners and states throughout the app
- **Toast Notifications** - User feedback with react-hot-toast
- **Responsive Layout** - Mobile-first responsive design

### 🔧 Technical Features
- **React Hook Form** - Form validation and management
- **React Router** - Client-side routing with protected routes
- **Axios Interceptors** - Automatic token management and error handling
- **Context API** - Global authentication state management
- **Local Storage** - Persistent authentication state

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Backend server running on http://localhost:5000

### Installation
1. Install dependencies:
   ```bash
   npm install
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```

3. Configure environment variables in `.env`:
   ```env
   REACT_APP_API_URL=http://localhost:5000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

The app will be available at http://localhost:3000

## Project Structure

```
src/
├── components/
│   ├── FormComponents.jsx    # Reusable form components
│   └── ProtectedRoute.jsx    # Route protection component
├── hooks/
│   └── useAuth.js           # Authentication context and hook
├── pages/
│   ├── Login.jsx            # Login page
│   ├── Register.jsx         # Registration page
│   ├── ForgotPassword.jsx   # Password reset request
│   ├── ResetPassword.jsx    # Password reset form
│   ├── VerifyEmail.jsx      # Email verification
│   └── Dashboard.jsx        # Main dashboard
├── utils/
│   └── api.js              # API service functions
├── App.js                  # Main app with routing
└── index.js               # App entry point
```

## Authentication Flow

### 1. Registration
1. User fills out registration form
2. Form validation ensures data integrity
3. Account created with email verification required
4. User redirected to email verification notice

### 2. Email Verification
1. User clicks verification link from email
2. Token validated on verification page
3. Account activated upon successful verification
4. Option to resend verification if token expired

### 3. Login
1. User enters email and password
2. System checks email verification status
3. If not verified, shows resend verification option
4. JWT token stored in localStorage upon successful login

### 4. Password Reset
1. User requests password reset via forgot password page
2. Reset email sent with secure token
3. User clicks link and sets new password
4. Token validated and password updated

### 5. Protected Routes
1. All protected routes check authentication status
2. Unauthenticated users redirected to login
3. Admin routes check for admin privileges
4. Loading states shown during authentication checks

## API Integration

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/verify-email` - Email verification
- `POST /api/auth/resend-verification` - Resend verification email
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password
- `GET /api/auth/me` - Get current user profile

### Error Handling
- Automatic token refresh and management
- Global error handling with toast notifications
- Network error handling and retry logic
- Form validation with detailed error messages

## Form Validation

### Registration Form
- **Username**: 3+ characters, alphanumeric + underscore
- **Email**: Valid email format
- **Password**: 8+ characters, uppercase, lowercase, number
- **Phone**: Valid phone number format
- **Terms**: Must accept terms and conditions

### Login Form
- **Email**: Valid email format
- **Password**: Required, 6+ characters

### Password Reset
- **New Password**: 8+ characters, uppercase, lowercase, number
- **Confirm Password**: Must match new password

## Styling

### TailwindCSS Classes
- Responsive design with mobile-first approach
- Consistent color scheme and spacing
- Modern UI components with hover and focus states
- Loading animations and transitions

### Component Styling
- Reusable form components with consistent styling
- Error states with red borders and messages
- Success states with green indicators
- Loading states with spinners

## Security Features

### Client-Side Security
- JWT token storage in localStorage
- Automatic token refresh and validation
- Protected route implementation
- Form validation and sanitization

### Best Practices
- HTTPS enforcement for production
- Secure token handling
- Input validation and sanitization
- Error message security (no sensitive data exposure)

## Development

### Available Scripts
- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Code Quality
- ESLint configuration for code quality
- Prettier for code formatting
- React Hook Form for form management
- TypeScript-ready structure

## Production Deployment

### Build Process
1. Set production environment variables
2. Run `npm run build`
3. Deploy `build/` folder to web server
4. Configure server for client-side routing

### Environment Variables
- `REACT_APP_API_URL` - Backend API URL
- `REACT_APP_ENABLE_DEBUG` - Enable debug mode
- `REACT_APP_ENABLE_ANALYTICS` - Enable analytics

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure backend CORS is configured
2. **API Connection**: Check `REACT_APP_API_URL` in `.env`
3. **Build Errors**: Clear `node_modules` and reinstall
4. **Routing Issues**: Ensure server supports client-side routing

### Debug Mode
Enable debug mode by setting `REACT_APP_ENABLE_DEBUG=true` in `.env`

## Contributing

1. Follow the existing code structure
2. Use the provided form components
3. Implement proper error handling
4. Add loading states for async operations
5. Test all authentication flows
6. Ensure responsive design

## License

This project is part of the Coupon Management System.
