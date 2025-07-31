# Email Verification Resend Functionality

This document explains the new email verification resend functionality that has been added to the coupon system.

## Overview

When users try to login but haven't verified their email address, the system now provides two ways to resend verification emails:

1. **During Login**: Add a `resend_verification` flag to the login request
2. **Dedicated Endpoint**: Use the `/api/auth/resend-verification` endpoint

## Features Added

### 1. Enhanced Login Endpoint

**Endpoint**: `POST /api/auth/login`

**New Behavior**:
- When a user tries to login with an unverified email, the response now includes helpful information
- Users can request a new verification email by setting `resend_verification: true`

**Request Examples**:

```json
// Normal login (will fail if email not verified)
{
  "email": "user@example.com",
  "password": "password123"
}

// Login with resend verification request
{
  "email": "user@example.com",
  "password": "password123",
  "resend_verification": true
}
```

**Response Examples**:

```json
// When email not verified (without resend flag)
{
  "error": "Email not verified",
  "message": "Please verify your email before logging in. You can request a new verification link by setting resend_verification to true.",
  "resend_verification_available": true
}

// When email not verified (with resend flag)
{
  "error": "Email not verified",
  "message": "A new verification email has been sent to your email address.",
  "resend_verification_sent": true
}
```

### 2. Dedicated Resend Verification Endpoint

**Endpoint**: `POST /api/auth/resend-verification`

**Purpose**: Allows users to request a new verification email without attempting to login

**Request**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "message": "If the email exists, a verification link has been sent."
}
```

**Security Features**:
- Does not reveal whether an email exists in the system
- Only sends verification emails to unverified accounts
- Returns the same message regardless of email existence

### 3. Token Expiration

**New Feature**: Email verification tokens now expire after 24 hours

**Database Changes**:
- Added `email_verification_expires` column to the `users` table
- Tokens are automatically invalidated after expiration

**Benefits**:
- Enhanced security
- Forces users to request new tokens if they don't verify promptly
- Prevents use of old verification links

## Database Migration

The system includes a migration script to add the new column:

```bash
cd backend
python -m app.utils.migrate_add_verification_expires
```

## Testing

Use the provided test script to verify functionality:

```bash
cd backend
python test_resend_verification.py
```

## Frontend Integration

To integrate this with your frontend, you can:

1. **Show resend option**: When login fails with "Email not verified", show a "Resend Verification Email" button
2. **Dedicated page**: Create a "Resend Verification" page for users who lost their original email
3. **Automatic resend**: Automatically request a new verification email when users try to login with unverified accounts

## Example Frontend Flow

```javascript
// When login fails with email not verified
if (response.error === 'Email not verified') {
  if (response.resend_verification_available) {
    // Show option to resend verification
    showResendVerificationOption();
  }
}

// Resend verification function
async function resendVerification(email) {
  const response = await fetch('/api/auth/resend-verification', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });

  if (response.ok) {
    showMessage('Verification email sent!');
  }
}
```

## Security Considerations

1. **Rate Limiting**: Consider implementing rate limiting on the resend endpoint
2. **Token Rotation**: Each resend generates a new token, invalidating the old one
3. **Expiration**: Tokens expire after 24 hours for security
4. **Privacy**: The resend endpoint doesn't reveal email existence

## Error Handling

Common error scenarios:

- **Expired Token**: "Verification token has expired. Please request a new one."
- **Invalid Token**: "Invalid verification token"
- **Already Verified**: "Email is already verified."
- **Missing Email**: "Missing email"

## Future Enhancements

Potential improvements:

1. **Configurable Expiration**: Make token expiration time configurable
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **Email Templates**: Improve email templates with better styling
4. **Analytics**: Track verification success rates and resend frequency
