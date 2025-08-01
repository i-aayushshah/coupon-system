-- Database initialization script for Coupon Management System

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables (these will be created by SQLAlchemy, but we'll create them here for Docker setup)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    first_name VARCHAR(80),
    last_name VARCHAR(80),
    phone VARCHAR(20),
    is_admin BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(128),
    email_verification_expires TIMESTAMP,
    password_reset_token VARCHAR(128),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed')),
    discount_value DECIMAL(10,2) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    max_uses INTEGER DEFAULT 1,
    current_uses INTEGER DEFAULT 0,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    minimum_order_value DECIMAL(10,2) DEFAULT 0,
    applicable_categories TEXT[],
    maximum_discount_amount DECIMAL(10,2),
    first_time_user_only BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50),
    brand VARCHAR(50),
    sku VARCHAR(50) UNIQUE,
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    image_url VARCHAR(255),
    minimum_order_value DECIMAL(10,2) DEFAULT 0,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    final_total DECIMAL(10,2) NOT NULL,
    coupon_code_used VARCHAR(50),
    coupon_id INTEGER REFERENCES coupons(id),
    order_status VARCHAR(20) DEFAULT 'pending',
    shipping_address TEXT,
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS redemptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    coupon_id INTEGER NOT NULL REFERENCES coupons(id),
    order_id INTEGER REFERENCES orders(id),
    original_amount DECIMAL(10,2) NOT NULL,
    final_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL,
    discount_applied DECIMAL(10,2) NOT NULL,
    products_applied_to TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_coupons_code ON coupons(code);
CREATE INDEX IF NOT EXISTS idx_coupons_is_public ON coupons(is_public);
CREATE INDEX IF NOT EXISTS idx_coupons_start_date ON coupons(start_date);
CREATE INDEX IF NOT EXISTS idx_coupons_end_date ON coupons(end_date);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_redemptions_user_id ON redemptions(user_id);
CREATE INDEX IF NOT EXISTS idx_redemptions_coupon_id ON redemptions(coupon_id);

-- Create views for common queries
CREATE OR REPLACE VIEW active_coupons AS
SELECT * FROM coupons
WHERE is_public = true
  AND start_date <= CURRENT_TIMESTAMP
  AND end_date >= CURRENT_TIMESTAMP
  AND current_uses < max_uses;

CREATE OR REPLACE VIEW user_dashboard_stats AS
SELECT
    u.id,
    u.username,
    COUNT(DISTINCT o.id) as total_orders,
    COALESCE(SUM(o.final_total), 0) as total_spent,
    COUNT(DISTINCT r.id) as total_redemptions,
    COALESCE(SUM(r.discount_amount), 0) as total_savings
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN redemptions r ON u.id = r.user_id
GROUP BY u.id, u.username;

CREATE OR REPLACE VIEW admin_dashboard_stats AS
SELECT
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT c.id) as total_coupons,
    COUNT(DISTINCT p.id) as total_products,
    COUNT(DISTINCT o.id) as total_orders,
    COALESCE(SUM(o.final_total), 0) as total_revenue,
    COUNT(DISTINCT r.id) as total_redemptions,
    COALESCE(SUM(r.discount_amount), 0) as total_discounts_given
FROM users u
CROSS JOIN (SELECT 1) as dummy
LEFT JOIN coupons c ON true
LEFT JOIN products p ON true
LEFT JOIN orders o ON true
LEFT JOIN redemptions r ON true;

-- Create functions for common operations
CREATE OR REPLACE FUNCTION update_coupon_usage()
RETURNS TRIGGER AS $$
BEGIN
    -- Update coupon usage count
    UPDATE coupons
    SET current_uses = current_uses + 1
    WHERE id = NEW.coupon_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for coupon usage tracking
DROP TRIGGER IF EXISTS trigger_update_coupon_usage ON redemptions;
CREATE TRIGGER trigger_update_coupon_usage
    AFTER INSERT ON redemptions
    FOR EACH ROW
    EXECUTE FUNCTION update_coupon_usage();

-- Create function to check coupon validity
CREATE OR REPLACE FUNCTION is_coupon_valid(
    p_coupon_code VARCHAR(50),
    p_user_id INTEGER,
    p_order_amount DECIMAL(10,2)
)
RETURNS BOOLEAN AS $$
DECLARE
    v_coupon RECORD;
    v_user_orders INTEGER;
BEGIN
    -- Get coupon details
    SELECT * INTO v_coupon
    FROM coupons
    WHERE code = p_coupon_code
      AND is_public = true;

    -- Check if coupon exists and is active
    IF v_coupon IS NULL THEN
        RETURN FALSE;
    END IF;

    -- Check if coupon is expired
    IF CURRENT_TIMESTAMP < v_coupon.start_date OR CURRENT_TIMESTAMP > v_coupon.end_date THEN
        RETURN FALSE;
    END IF;

    -- Check if coupon is fully used
    IF v_coupon.current_uses >= v_coupon.max_uses THEN
        RETURN FALSE;
    END IF;

    -- Check minimum order value
    IF p_order_amount < COALESCE(v_coupon.minimum_order_value, 0) THEN
        RETURN FALSE;
    END IF;

    -- Check if user is first-time user (if coupon requires it)
    IF v_coupon.first_time_user_only THEN
        SELECT COUNT(*) INTO v_user_orders
        FROM orders
        WHERE user_id = p_user_id;

        IF v_user_orders > 0 THEN
            RETURN FALSE;
        END IF;
    END IF;

    -- Check if user has already used this coupon
    IF EXISTS (
        SELECT 1 FROM redemptions
        WHERE user_id = p_user_id AND coupon_id = v_coupon.id
    ) THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Create function to calculate discount amount
CREATE OR REPLACE FUNCTION calculate_discount_amount(
    p_coupon_code VARCHAR(50),
    p_order_amount DECIMAL(10,2)
)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    v_coupon RECORD;
    v_discount_amount DECIMAL(10,2);
BEGIN
    -- Get coupon details
    SELECT * INTO v_coupon
    FROM coupons
    WHERE code = p_coupon_code;

    IF v_coupon IS NULL THEN
        RETURN 0;
    END IF;

    -- Calculate discount based on type
    IF v_coupon.discount_type = 'percentage' THEN
        v_discount_amount := p_order_amount * (v_coupon.discount_value / 100.0);
    ELSE
        v_discount_amount := v_coupon.discount_value;
    END IF;

    -- Apply maximum discount limit
    IF v_coupon.maximum_discount_amount IS NOT NULL AND v_discount_amount > v_coupon.maximum_discount_amount THEN
        v_discount_amount := v_coupon.maximum_discount_amount;
    END IF;

    -- Ensure discount doesn't exceed order amount
    IF v_discount_amount > p_order_amount THEN
        v_discount_amount := p_order_amount;
    END IF;

    RETURN v_discount_amount;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data for testing
INSERT INTO users (username, email, first_name, last_name, password_hash, email_verified, is_admin, created_at)
VALUES
    ('admin', 'admin@example.com', 'Admin', 'User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.gSJmW', true, true, CURRENT_TIMESTAMP),
    ('testuser', 'test@example.com', 'Test', 'User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.gSJmW', true, false, CURRENT_TIMESTAMP)
ON CONFLICT (email) DO NOTHING;

-- Insert sample coupons
INSERT INTO coupons (code, title, description, discount_type, discount_value, is_public, max_uses, current_uses, start_date, end_date, minimum_order_value, applicable_categories, maximum_discount_amount, first_time_user_only, created_by, created_at)
VALUES
    ('SAVE20', '20% Off', 'Get 20% off your purchase', 'percentage', 20, true, 100, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1 year', 50.00, ARRAY['Electronics', 'Clothing'], 25.00, false, 1, CURRENT_TIMESTAMP),
    ('SAVE10', '10% Off', 'Get 10% off your purchase', 'percentage', 10, true, 50, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '6 months', 25.00, ARRAY['Electronics'], 15.00, false, 1, CURRENT_TIMESTAMP),
    ('FIRST10', 'First Time 10%', '10% off for first-time users', 'percentage', 10, true, 200, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1 year', 20.00, ARRAY['All'], 10.00, true, 1, CURRENT_TIMESTAMP)
ON CONFLICT (code) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, description, price, category, brand, sku, stock_quantity, is_active, image_url, minimum_order_value, created_by, created_at)
VALUES
    ('iPhone 13', 'Latest iPhone with advanced features', 999.99, 'Electronics', 'Apple', 'IPHONE13-001', 50, true, '/uploads/iphone13.jpg', 10.00, 1, CURRENT_TIMESTAMP),
    ('Samsung TV', '4K Smart TV with amazing picture quality', 799.99, 'Electronics', 'Samsung', 'TV-SAMSUNG-001', 25, true, '/uploads/samsung-tv.jpg', 10.00, 1, CURRENT_TIMESTAMP)
ON CONFLICT (sku) DO NOTHING;
