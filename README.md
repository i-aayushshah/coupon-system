# Coupon Management System

## Project Overview
A full-featured coupon management system with secure authentication, admin and user roles, public/private coupons, redemption tracking, email verification (with resend), user dashboard, and robust validation. Built with Flask (backend) and React (frontend).

## Project Structure
```
coupon-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── utils/
│   │   └── config.py
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── utils/
│   │   └── hooks/
│   ├── package.json
│   └── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in values (see below)
6. `python run.py` to start Flask server

### Frontend
1. `cd frontend`
2. `npm install`
3. Copy `.env.example` to `.env` and fill in values
4. `npm start` to run React app

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Mail, Flask-CORS, python-dotenv, bcrypt, SQLite
- **Frontend:** React, TailwindCSS, Axios, React Router DOM, React Hook Form, React Hot Toast

## Features
- **Authentication:** JWT-based login, registration, password reset, and email verification (with resend support)
- **Role Management:** Admin and regular user separation
- **Email Verification:** Required for login, with resend and expiry handling
- **Admin Features:**
  - Create, update, delete, and list coupons (public/private)
  - View coupon redemption history
  - Dashboard with stats (total/active/inactive coupons, most redeemed, recent redemptions)
- **Coupon System:**
  - Public and private coupons
  - Coupon validation (date, usage, code uniqueness)
  - Redemption with order amount and discount calculation
  - Double redemption prevention
  - Search and filter coupons
- **User Features:**
  - Profile management (view/update info, change password, delete account)
  - User dashboard (total redemptions, savings, recent redemptions, available coupons)
  - Redemption history and stats (monthly trends, favorite coupon types)
- **Security:**
  - Passwords hashed with bcrypt
  - JWT tokens for all protected routes
  - No user enumeration in auth endpoints
  - Email verification required for login
  - Account deletion requires password

## API Overview
- **Auth:**
  - `POST /api/auth/register` — Register new user
  - `POST /api/auth/login` — Login (with resend verification support)
  - `POST /api/auth/verify-email` — Verify email
  - `POST /api/auth/resend-verification` — Resend verification email
  - `POST /api/auth/forgot-password` — Request password reset
  - `POST /api/auth/reset-password` — Reset password
  - `GET /api/auth/me` — Get current user profile
- **Admin:**
  - `POST /api/admin/coupons` — Create coupon
  - `GET /api/admin/coupons` — List all coupons (pagination)
  - `GET /api/admin/coupons/<id>` — Get coupon details
  - `PUT /api/admin/coupons/<id>` — Update coupon
  - `DELETE /api/admin/coupons/<id>` — Delete coupon
  - `GET /api/admin/coupons/<id>/redemptions` — Coupon redemption history
  - `GET /api/admin/dashboard` — Admin dashboard stats
- **Coupons/Public:**
  - `GET /api/coupons/public` — List public coupons
  - `GET /api/coupons/validate/<code>` — Validate coupon
  - `POST /api/coupons/redeem` — Redeem coupon
  - `GET /api/coupons/search` — Search coupons
- **User:**
  - `GET /api/user/profile` — Get user profile
  - `PUT /api/user/profile` — Update profile
  - `POST /api/user/change-password` — Change password
  - `POST /api/user/delete-account` — Delete account (with password)
  - `GET /api/user/stats` — User stats (redemptions, savings, trends)
  - `GET /api/user/dashboard` — User dashboard
  - `GET /api/coupons/user/redemptions` — Redemption history

## Environment Variables
- **Backend:**
  - `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_USE_TLS`, `MAIL_USE_SSL`
- **Frontend:**
  - `REACT_APP_API_URL`, etc.

## Testing
- Use Postman, curl, or PowerShell `Invoke-RestMethod` to test endpoints
- Test flows: registration, email verification, login, resend verification, password reset, coupon creation, redemption, admin/user dashboards

## Security & Best Practices
- All sensitive routes require JWT authentication
- Passwords are never stored in plain text
- Email verification is enforced for all users
- No user enumeration in auth flows
- Rate limiting recommended for production (not enabled by default)

---

For detailed API usage and frontend integration, see the codebase and comments. This README covers all major features and flows as implemented.
