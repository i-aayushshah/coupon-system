#!/usr/bin/env python3
"""
Test script for cart functionality
"""

from app import create_app, db
from app.models import Product, User, Coupon
import requests
import json

def test_cart_functionality():
    """Test cart update functionality"""

    # Create app context
    app = create_app()
    with app.app_context():
        # Check if we have products
        products = Product.query.all()
        print(f"Found {len(products)} products in database")

        if not products:
            print("No products found. Creating test product...")
            # Create a test product
            test_product = Product(
                name="Test Product",
                description="A test product for cart testing",
                price=29.99,
                category="Electronics",
                brand="TestBrand",
                sku="TEST001",
                stock_quantity=10,
                is_active=True,
                created_by=1
            )
            db.session.add(test_product)
            db.session.commit()
            print(f"Created test product with ID: {test_product.id}")

        # Check if we have users
        users = User.query.all()
        print(f"Found {len(users)} users in database")

        # Check if we have coupons
        coupons = Coupon.query.all()
        print(f"Found {len(coupons)} coupons in database")

        if not coupons:
            print("No coupons found. Creating test coupon...")
            # Create a test coupon
            test_coupon = Coupon(
                code="TEST10",
                title="Test 10% Off",
                description="10% off test coupon",
                discount_type="percentage",
                discount_value=10,
                max_uses=100,
                current_uses=0,
                is_active=True,
                is_public=True,
                minimum_order_value=20.0
            )
            db.session.add(test_coupon)
            db.session.commit()
            print(f"Created test coupon with code: {test_coupon.code}")

if __name__ == "__main__":
    test_cart_functionality()
