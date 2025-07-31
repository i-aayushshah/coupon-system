from flask import Blueprint, request, jsonify
from app import db
from app.models import Product, User, Order, OrderItem, Coupon, Redemption
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
import json

bp = Blueprint('cart', __name__, url_prefix='/api/cart')

# In-memory cart storage (in production, use Redis or database)
# This is a simple implementation for demo purposes
user_carts = {}

def get_user_cart(user_id):
    """Get or create user cart"""
    if user_id not in user_carts:
        user_carts[user_id] = {
            'items': [],
            'applied_coupon': None,
            'subtotal': 0,
            'discount_amount': 0,
            'final_total': 0
        }
    return user_carts[user_id]

def calculate_cart_totals(cart):
    """Calculate cart totals"""
    subtotal = sum(item['line_total'] for item in cart['items'])
    cart['subtotal'] = subtotal
    cart['discount_amount'] = 0
    cart['final_total'] = subtotal
    return cart

# POST /api/cart/add - Add product to cart
@bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()

    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than 0'}), 400

    # Get product
    product = Product.query.get(product_id)
    if not product or not product.is_active:
        return jsonify({'error': 'Product not found or inactive'}), 404

    if product.stock_quantity < quantity:
        return jsonify({'error': f'Insufficient stock. Available: {product.stock_quantity}'}), 400

    # Get user cart
    cart = get_user_cart(user_id)

    # Check if product already in cart
    existing_item = None
    for item in cart['items']:
        if item['product_id'] == product_id:
            existing_item = item
            break

    if existing_item:
        # Update quantity
        new_quantity = existing_item['quantity'] + quantity
        if product.stock_quantity < new_quantity:
            return jsonify({'error': f'Insufficient stock. Available: {product.stock_quantity}'}), 400

        existing_item['quantity'] = new_quantity
        existing_item['line_total'] = float(product.price) * new_quantity
    else:
        # Add new item
        cart['items'].append({
            'product_id': product_id,
            'product_name': product.name,
            'product_price': float(product.price),
            'quantity': quantity,
            'line_total': float(product.price) * quantity
        })

    # Recalculate totals
    cart = calculate_cart_totals(cart)

    return jsonify({
        'message': 'Product added to cart',
        'cart': cart
    }), 200

# GET /api/cart - Get current cart
@bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cart = get_user_cart(user_id)

    return jsonify({
        'cart': cart
    }), 200

# PUT /api/cart/update - Update cart quantities
@bp.route('/update', methods=['PUT'])
@jwt_required()
def update_cart():
    user_id = get_jwt_identity()
    data = request.get_json()

    updates = data.get('updates', [])  # List of {product_id, quantity}

    if not updates:
        return jsonify({'error': 'No updates provided'}), 400

    cart = get_user_cart(user_id)

    for update in updates:
        product_id = update.get('product_id')
        quantity = update.get('quantity', 0)

        if quantity <= 0:
            # Remove item
            cart['items'] = [item for item in cart['items'] if item['product_id'] != product_id]
        else:
            # Update quantity
            for item in cart['items']:
                if item['product_id'] == product_id:
                    # Check stock
                    product = Product.query.get(product_id)
                    if not product or not product.is_active:
                        return jsonify({'error': f'Product {product_id} not found'}), 404

                    if product.stock_quantity < quantity:
                        return jsonify({'error': f'Insufficient stock for {product.name}'}), 400

                    item['quantity'] = quantity
                    item['line_total'] = float(product.price) * quantity
                    break

    # Recalculate totals
    cart = calculate_cart_totals(cart)

    return jsonify({
        'message': 'Cart updated',
        'cart': cart
    }), 200

# DELETE /api/cart/remove/<product_id> - Remove from cart
@bp.route('/remove/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    user_id = get_jwt_identity()
    cart = get_user_cart(user_id)

    # Remove item
    cart['items'] = [item for item in cart['items'] if item['product_id'] != product_id]

    # Recalculate totals
    cart = calculate_cart_totals(cart)

    return jsonify({
        'message': 'Product removed from cart',
        'cart': cart
    }), 200

# POST /api/cart/apply-coupon - Apply coupon to cart
@bp.route('/apply-coupon', methods=['POST'])
@jwt_required()
def apply_coupon():
    user_id = get_jwt_identity()
    data = request.get_json()

    coupon_code = data.get('coupon_code', '').strip()

    if not coupon_code:
        return jsonify({'error': 'Coupon code is required'}), 400

    cart = get_user_cart(user_id)

    if not cart['items']:
        return jsonify({'error': 'Cart is empty'}), 400

    # Find coupon
    coupon = Coupon.query.filter_by(code=coupon_code.upper()).first()
    if not coupon:
        return jsonify({'error': 'Invalid coupon code'}), 404

    if not coupon.is_active:
        return jsonify({'error': 'Coupon is inactive'}), 400

    # Check date validity
    now = datetime.datetime.utcnow()
    if coupon.start_date and coupon.start_date > now:
        return jsonify({'error': 'Coupon has not started yet'}), 400
    if coupon.end_date and coupon.end_date < now:
        return jsonify({'error': 'Coupon has expired'}), 400

    # Check usage limits
    if coupon.current_uses >= coupon.max_uses:
        return jsonify({'error': 'Coupon usage limit reached'}), 400

    # Check minimum order value
    if coupon.minimum_order_value and cart['subtotal'] < float(coupon.minimum_order_value):
        return jsonify({
            'error': f'Minimum order value of ${coupon.minimum_order_value} required',
            'current_total': cart['subtotal'],
            'minimum_required': float(coupon.minimum_order_value)
        }), 400

    # Check applicable categories
    if coupon.get_applicable_categories():
        cart_categories = set()
        for item in cart['items']:
            product = Product.query.get(item['product_id'])
            if product:
                cart_categories.add(product.category)

        applicable_categories = set(coupon.get_applicable_categories())

        if not cart_categories.intersection(applicable_categories):
            return jsonify({
                'error': f'Coupon only applies to categories: {", ".join(applicable_categories)}'
            }), 400

    # Calculate discount
    discount_amount = 0
    if coupon.discount_type == 'percentage':
        discount_amount = (cart['subtotal'] * coupon.discount_value) / 100
        # Apply maximum discount cap if set
        if coupon.maximum_discount_amount:
            discount_amount = min(discount_amount, float(coupon.maximum_discount_amount))
    elif coupon.discount_type == 'fixed':
        discount_amount = min(coupon.discount_value, cart['subtotal'])

    # Apply discount
    cart['applied_coupon'] = {
        'code': coupon.code,
        'title': coupon.title,
        'discount_type': coupon.discount_type,
        'discount_value': coupon.discount_value,
        'discount_amount': round(discount_amount, 2)
    }
    cart['discount_amount'] = round(discount_amount, 2)
    cart['final_total'] = cart['subtotal'] - cart['discount_amount']

    return jsonify({
        'message': 'Coupon applied successfully',
        'cart': cart
    }), 200

# POST /api/cart/checkout - Complete order with coupon
@bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    user_id = get_jwt_identity()
    data = request.get_json()

    shipping_address = data.get('shipping_address', '')
    payment_method = data.get('payment_method', '')

    cart = get_user_cart(user_id)

    if not cart['items']:
        return jsonify({'error': 'Cart is empty'}), 400

    # Validate stock again
    for item in cart['items']:
        product = Product.query.get(item['product_id'])
        if not product or not product.is_active:
            return jsonify({'error': f'Product {item["product_id"]} not found'}), 404

        if product.stock_quantity < item['quantity']:
            return jsonify({'error': f'Insufficient stock for {product.name}'}), 400

    # Validate coupon if applied
    coupon = None
    if cart['applied_coupon']:
        coupon = Coupon.query.filter_by(code=cart['applied_coupon']['code']).first()
        if not coupon or not coupon.is_active:
            return jsonify({'error': 'Applied coupon is no longer valid'}), 400

        # Check if user already redeemed this coupon
        existing_redemption = Redemption.query.filter_by(
            user_id=int(user_id),
            coupon_id=coupon.id
        ).first()

        if existing_redemption:
            return jsonify({'error': 'You have already redeemed this coupon'}), 400

    try:
        # Create order
        order = Order(
            user_id=int(user_id),
            subtotal=cart['subtotal'],
            discount_amount=cart['discount_amount'],
            final_total=cart['final_total'],
            coupon_code_used=cart['applied_coupon']['code'] if cart['applied_coupon'] else None,
            coupon_id=coupon.id if coupon else None,
            order_status='completed',
            shipping_address=shipping_address,
            payment_method=payment_method,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )

        db.session.add(order)
        db.session.flush()  # Get order ID

        # Create order items
        for item in cart['items']:
            product = Product.query.get(item['product_id'])

            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['product_price'],
                line_total=item['line_total']
            )

            db.session.add(order_item)

            # Update product stock
            product.stock_quantity -= item['quantity']
            product.updated_at = datetime.datetime.utcnow()

        # Create redemption record if coupon was used
        if coupon:
            redemption = Redemption(
                user_id=int(user_id),
                coupon_id=coupon.id,
                order_id=order.id,
                redeemed_at=datetime.datetime.utcnow(),
                discount_applied=cart['discount_amount'],
                original_amount=cart['subtotal'],
                discount_amount=cart['discount_amount'],
                final_amount=cart['final_total'],
                products_applied_to=[item['product_id'] for item in cart['items']]
            )

            db.session.add(redemption)

            # Update coupon usage
            coupon.current_uses += 1
            coupon.updated_at = datetime.datetime.utcnow()

        db.session.commit()

        # Clear cart
        user_carts[user_id] = {
            'items': [],
            'applied_coupon': None,
            'subtotal': 0,
            'discount_amount': 0,
            'final_total': 0
        }

        return jsonify({
            'message': 'Order completed successfully',
            'order': order.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to complete order. Please try again.'}), 500
