import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ProtectedRoute from '../ProtectedRoute';

// Mock the useAuth hook
jest.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: null,
    loading: false,
    isAuthenticated: false,
  }),
}));

describe('ProtectedRoute', () => {
  test('redirects to login when user is not authenticated', () => {
    render(
      <BrowserRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </BrowserRouter>
    );
    
    // The component should redirect, so we shouldn't see the protected content
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('renders children when user is authenticated', () => {
    // Mock authenticated user
    jest.doMock('../../hooks/useAuth', () => ({
      useAuth: () => ({
        user: { id: 1, email: 'test@example.com' },
        loading: false,
        isAuthenticated: true,
      }),
    }));

    render(
      <BrowserRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </BrowserRouter>
    );
    
    // Should see the protected content
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
}); 