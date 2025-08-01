import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

// Mock the AuthProvider to avoid context issues in tests
jest.mock('./hooks/useAuth', () => ({
  AuthProvider: ({ children }) => <div data-testid="auth-provider">{children}</div>,
}));

// Mock react-hot-toast to avoid toast rendering issues
jest.mock('react-hot-toast', () => ({
  Toaster: () => <div data-testid="toaster" />,
}));

test('renders app with router', () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
  
  // Check that the app renders without crashing
  expect(screen.getByTestId('auth-provider')).toBeInTheDocument();
  expect(screen.getByTestId('toaster')).toBeInTheDocument();
});

test('app has correct structure', () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
  
  // Check that the main app div exists
  const appDiv = screen.getByRole('main') || document.querySelector('.App');
  expect(appDiv).toBeInTheDocument();
});
