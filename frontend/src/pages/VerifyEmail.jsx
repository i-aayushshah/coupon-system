import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { authAPI } from '../utils/api';
import { Button, Card, Alert, LoadingSpinner } from '../components/FormComponents';
import toast from 'react-hot-toast';

const VerifyEmail = () => {
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [showResend, setShowResend] = useState(false);
  const [resendEmail, setResendEmail] = useState('');
  const [resendLoading, setResendLoading] = useState(false);

  const { token } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  // Verify email token on component mount
  useEffect(() => {
    const verifyEmail = async () => {
      let verificationToken = token;
      let email = '';

      // First try to get token from URL params (new format: /verify-email/:token)
      if (!verificationToken) {
        // If no token in URL params, try query params (old format: ?token=...&email=...)
        const urlParams = new URLSearchParams(location.search);
        verificationToken = urlParams.get('token');
        email = urlParams.get('email') || '';
      } else {
        // If we have token from URL params, get email from query params
        const urlParams = new URLSearchParams(location.search);
        email = urlParams.get('email') || '';
      }

      console.log('Verification token:', verificationToken);
      console.log('Email:', email);

      if (!verificationToken) {
        setError('No verification token provided');
        setLoading(false);
        setVerifying(false);
        return;
      }

      try {
        await authAPI.verifyEmail(verificationToken, email);
        setSuccess(true);
        toast.success('Email verified successfully!');
      } catch (error) {
        const errorMessage = error.response?.data?.error || 'Email verification failed';
        setError(errorMessage);

        // If it's an expired token error, show resend option
        if (errorMessage.includes('expired') || errorMessage.includes('invalid')) {
          setShowResend(true);
          // Set email from URL if available
          if (email) {
            setResendEmail(email);
          }
        }
      } finally {
        setLoading(false);
        setVerifying(false);
      }
    };

    verifyEmail();
  }, [token, location.search]);

  const handleResendVerification = async () => {
    if (!resendEmail) {
      toast.error('Please enter your email address');
      return;
    }

    setResendLoading(true);
    try {
      await authAPI.resendVerification(resendEmail);
      toast.success('Verification email sent! Please check your inbox.');
      setShowResend(false);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to send verification email');
    } finally {
      setResendLoading(false);
    }
  };

  const handleGoToLogin = () => {
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="text-center">
            <LoadingSpinner size="lg" className="mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900">
              Verifying your email...
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Please wait while we verify your email address.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900">
              Email Verified!
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Your email has been successfully verified
            </p>
          </div>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <Card>
            <div className="text-center space-y-4">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                <svg
                  className="h-6 w-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  Verification Complete
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  Your email address has been successfully verified. You can now sign in to your account.
                </p>
              </div>

              <div className="space-y-3">
                <Alert type="success">
                  <p className="text-sm">
                    Welcome! Your account is now fully activated.
                  </p>
                </Alert>

                <Button
                  onClick={handleGoToLogin}
                  className="w-full"
                >
                  Sign In
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900">
              Verification Failed
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              We couldn't verify your email address
            </p>
          </div>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <Card>
            <div className="text-center space-y-4">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg
                  className="h-6 w-6 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  Verification Error
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  {error}
                </p>
              </div>

              {showResend && (
                <div className="space-y-3">
                  <Alert type="info">
                    <p className="text-sm">
                      Verification links expire after 24 hours. You can request a new verification email.
                    </p>
                  </Alert>

                  <div className="space-y-2">
                    <input
                      type="email"
                      placeholder="Enter your email address"
                      value={resendEmail}
                      onChange={(e) => setResendEmail(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <Button
                      onClick={handleResendVerification}
                      loading={resendLoading}
                      disabled={resendLoading}
                      className="w-full"
                    >
                      Resend Verification Email
                    </Button>
                  </div>
                </div>
              )}

              <div className="space-y-3">
                <Link
                  to="/login"
                  className="block w-full text-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Back to Login
                </Link>

                <Link
                  to="/register"
                  className="block w-full text-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Create New Account
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900">
            Processing...
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Please wait while we process your request.
          </p>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmail;
