import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

const AdminRedirect = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // If user is admin, redirect to admin dashboard
  if (user?.is_admin) {
    toast('Redirecting to admin dashboard...', {
      icon: '🔄',
      duration: 2000,
    });
    return <Navigate to="/admin" replace />;
  }

  // If not admin, render the children (regular user content)
  return children;
};

export default AdminRedirect;
