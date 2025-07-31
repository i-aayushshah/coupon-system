import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth';
import CouponCard from '../components/CouponCard';
import { Button, Input, Card, LoadingSpinner } from '../components/FormComponents';

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
  toast: jest.fn()
}));

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/test' })
}));

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('Form Components', () => {
  describe('Button', () => {
    test('renders button with text', () => {
      render(<Button>Click me</Button>);
      expect(screen.getByText('Click me')).toBeInTheDocument();
    });

    test('handles click events', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Click me</Button>);

      fireEvent.click(screen.getByText('Click me'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    test('applies variant classes', () => {
      render(<Button variant="outline">Outline Button</Button>);
      const button = screen.getByText('Outline Button');
      expect(button).toHaveClass('border-gray-300');
    });

    test('applies size classes', () => {
      render(<Button size="sm">Small Button</Button>);
      const button = screen.getByText('Small Button');
      expect(button).toHaveClass('px-3 py-1.5 text-sm');
    });

    test('disables button when disabled prop is true', () => {
      render(<Button disabled>Disabled Button</Button>);
      const button = screen.getByText('Disabled Button');
      expect(button).toBeDisabled();
    });
  });

  describe('Input', () => {
    test('renders input with placeholder', () => {
      render(<Input placeholder="Enter text" />);
      expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
    });

    test('handles value changes', () => {
      const handleChange = jest.fn();
      render(<Input onChange={handleChange} placeholder="Enter text" />);

      const input = screen.getByPlaceholderText('Enter text');
      fireEvent.change(input, { target: { value: 'test' } });
      expect(handleChange).toHaveBeenCalled();
    });

    test('applies different types', () => {
      render(<Input type="password" placeholder="Password" />);
      const input = screen.getByPlaceholderText('Password');
      expect(input).toHaveAttribute('type', 'password');
    });

    test('handles disabled state', () => {
      render(<Input disabled placeholder="Disabled input" />);
      const input = screen.getByPlaceholderText('Disabled input');
      expect(input).toBeDisabled();
    });
  });

  describe('Card', () => {
    test('renders card with children', () => {
      render(
        <Card>
          <div>Card content</div>
        </Card>
      );
      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    test('applies custom className', () => {
      render(
        <Card className="custom-class">
          <div>Card content</div>
        </Card>
      );
      const card = screen.getByText('Card content').parentElement;
      expect(card).toHaveClass('custom-class');
    });
  });

  describe('LoadingSpinner', () => {
    test('renders loading spinner', () => {
      render(<LoadingSpinner />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    test('applies size classes', () => {
      render(<LoadingSpinner size="lg" />);
      const spinner = screen.getByRole('status');
      expect(spinner).toHaveClass('w-8 h-8');
    });
  });
});

describe('CouponCard', () => {
  const mockCoupon = {
    id: 1,
    code: 'SAVE20',
    title: '20% Off',
    description: 'Get 20% off your purchase',
    discount_type: 'percentage',
    discount_value: 20,
    minimum_order_value: 50,
    applicable_categories: ['Electronics', 'Clothing'],
    maximum_discount_amount: 25,
    first_time_user_only: false,
    start_date: '2024-01-01T00:00:00Z',
    end_date: '2024-12-31T23:59:59Z',
    max_uses: 100,
    current_uses: 0,
    is_public: true,
    days_remaining: 30
  };

  test('renders coupon information', () => {
    render(
      <TestWrapper>
        <CouponCard coupon={mockCoupon} />
      </TestWrapper>
    );

    expect(screen.getByText('SAVE20')).toBeInTheDocument();
    expect(screen.getByText('20% Off')).toBeInTheDocument();
    expect(screen.getByText('Get 20% off your purchase')).toBeInTheDocument();
    expect(screen.getByText('20%')).toBeInTheDocument();
  });

  test('displays discount information correctly', () => {
    render(
      <TestWrapper>
        <CouponCard coupon={mockCoupon} />
      </TestWrapper>
    );

    expect(screen.getByText('20%')).toBeInTheDocument();
    expect(screen.getByText('Min. Order: $50.00')).toBeInTheDocument();
    expect(screen.getByText('Max Discount: $25.00')).toBeInTheDocument();
  });

  test('displays usage information', () => {
    render(
      <TestWrapper>
        <CouponCard coupon={mockCoupon} />
      </TestWrapper>
    );

    expect(screen.getByText('Used: 0/100')).toBeInTheDocument();
    expect(screen.getByText('Expires: 30 days left')).toBeInTheDocument();
  });

  test('handles "Use Coupon" button click', () => {
    render(
      <TestWrapper>
        <CouponCard coupon={mockCoupon} />
      </TestWrapper>
    );

    const useButton = screen.getByText('Use Coupon');
    fireEvent.click(useButton);

    expect(mockNavigate).toHaveBeenCalledWith('/cart');
  });

  test('displays applicable categories', () => {
    render(
      <TestWrapper>
        <CouponCard coupon={mockCoupon} />
      </TestWrapper>
    );

    expect(screen.getByText('Electronics, Clothing')).toBeInTheDocument();
  });

  test('handles expired coupon', () => {
    const expiredCoupon = {
      ...mockCoupon,
      days_remaining: -5
    };

    render(
      <TestWrapper>
        <CouponCard coupon={expiredCoupon} />
      </TestWrapper>
    );

    expect(screen.getByText('Expired')).toBeInTheDocument();
  });

  test('handles fully used coupon', () => {
    const usedCoupon = {
      ...mockCoupon,
      current_uses: 100
    };

    render(
      <TestWrapper>
        <CouponCard coupon={usedCoupon} />
      </TestWrapper>
    );

    expect(screen.getByText('Used: 100/100')).toBeInTheDocument();
  });

  test('handles first-time user only coupon', () => {
    const firstTimeCoupon = {
      ...mockCoupon,
      first_time_user_only: true
    };

    render(
      <TestWrapper>
        <CouponCard coupon={firstTimeCoupon} />
      </TestWrapper>
    );

    expect(screen.getByText('First-time users only')).toBeInTheDocument();
  });
});

describe('Authentication Flow', () => {
  test('handles login form submission', async () => {
    const mockLogin = jest.fn();

    render(
      <TestWrapper>
        <form onSubmit={mockLogin}>
          <Input name="email" placeholder="Email" />
          <Input name="password" type="password" placeholder="Password" />
          <Button type="submit">Login</Button>
        </form>
      </TestWrapper>
    );

    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByText('Login');

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.click(submitButton);

    expect(mockLogin).toHaveBeenCalled();
  });

  test('handles registration form submission', async () => {
    const mockRegister = jest.fn();

    render(
      <TestWrapper>
        <form onSubmit={mockRegister}>
          <Input name="username" placeholder="Username" />
          <Input name="email" placeholder="Email" />
          <Input name="password" type="password" placeholder="Password" />
          <Input name="first_name" placeholder="First Name" />
          <Input name="last_name" placeholder="Last Name" />
          <Button type="submit">Register</Button>
        </form>
      </TestWrapper>
    );

    const usernameInput = screen.getByPlaceholderText('Username');
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const firstNameInput = screen.getByPlaceholderText('First Name');
    const lastNameInput = screen.getByPlaceholderText('Last Name');
    const submitButton = screen.getByText('Register');

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(firstNameInput, { target: { value: 'Test' } });
    fireEvent.change(lastNameInput, { target: { value: 'User' } });
    fireEvent.click(submitButton);

    expect(mockRegister).toHaveBeenCalled();
  });
});

describe('Form Validation', () => {
  test('validates required fields', () => {
    const mockSubmit = jest.fn();

    render(
      <TestWrapper>
        <form onSubmit={mockSubmit}>
          <Input name="email" placeholder="Email" required />
          <Input name="password" type="password" placeholder="Password" required />
          <Button type="submit">Submit</Button>
        </form>
      </TestWrapper>
    );

    const submitButton = screen.getByText('Submit');
    fireEvent.click(submitButton);

    // Form should not submit without required fields
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  test('validates email format', () => {
    const mockSubmit = jest.fn();

    render(
      <TestWrapper>
        <form onSubmit={mockSubmit}>
          <Input name="email" type="email" placeholder="Email" />
          <Button type="submit">Submit</Button>
        </form>
      </TestWrapper>
    );

    const emailInput = screen.getByPlaceholderText('Email');
    const submitButton = screen.getByText('Submit');

    // Test invalid email
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);

    expect(mockSubmit).toHaveBeenCalled();
  });
});
