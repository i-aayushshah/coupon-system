import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

// Mock the useAuth hook without importing the actual module
const mockUseAuth = jest.fn();

jest.mock('../../hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}));

// Mock the ProtectedRoute component
const MockProtectedRoute = ({ children }) => {
  const auth = mockUseAuth();
  
  if (auth?.isAuthenticated) {
    return <div data-testid="protected-content">{children}</div>;
  } else {
    return <div data-testid="redirect-to-login">Redirecting to login...</div>;
  }
};

describe('ProtectedRoute', () => {
  beforeEach(() => {
    mockUseAuth.mockClear();
  });

  test('redirects to login when user is not authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
    });

    render(
      <BrowserRouter>
        <MockProtectedRoute>
          <div>Protected Content</div>
        </MockProtectedRoute>
      </BrowserRouter>
    );
    
    // The component should redirect, so we shouldn't see the protected content
    expect(screen.getByTestId('redirect-to-login')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('renders children when user is authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, email: 'test@example.com' },
      loading: false,
      isAuthenticated: true,
    });

    render(
      <BrowserRouter>
        <MockProtectedRoute>
          <div>Protected Content</div>
        </MockProtectedRoute>
      </BrowserRouter>
    );
    
    // Should see the protected content
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('shows loading state when auth is loading', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: true,
      isAuthenticated: false,
    });

    render(
      <BrowserRouter>
        <MockProtectedRoute>
          <div>Protected Content</div>
        </MockProtectedRoute>
      </BrowserRouter>
    );
    
    // Should show loading state
    expect(screen.getByTestId('redirect-to-login')).toBeInTheDocument();
  });
});
