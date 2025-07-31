from flask import Blueprint, request, jsonify
from app import db
from app.models import Product, User
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime

bp = Blueprint('products', __name__, url_prefix='/api/products')

# GET /api/products - List active products with filters
@bp.route('', methods=['GET'])
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', '').strip()
    brand = request.args.get('brand', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'name')  # name, price, created_at
    sort_order = request.args.get('sort_order', 'asc')  # asc, desc

    # Build query
    query = Product.query.filter_by(is_active=True)

    # Apply filters
    if category:
        query = query.filter(Product.category.ilike(f'%{category}%'))
    if brand:
        query = query.filter(Product.brand.ilike(f'%{brand}%'))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Apply sorting
    if sort_by == 'name':
        if sort_order == 'desc':
            query = query.order_by(Product.name.desc())
        else:
            query = query.order_by(Product.name.asc())
    elif sort_by == 'price':
        if sort_order == 'desc':
            query = query.order_by(Product.price.desc())
        else:
            query = query.order_by(Product.price.asc())
    elif sort_by == 'created_at':
        if sort_order == 'desc':
            query = query.order_by(Product.created_at.desc())
        else:
            query = query.order_by(Product.created_at.asc())
    else:
        query = query.order_by(Product.name.asc())

    # Pagination
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    products = []
    for product in pagination.items:
        products.append(product.to_dict())

    return jsonify({
        'products': products,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

# GET /api/products/<id> - Get product details
@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.is_active:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify({
        'product': product.to_dict()
    }), 200

# GET /api/products/search?q=<query> - Search products
@bp.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    # Build search query
    db_query = Product.query.filter_by(is_active=True)

    # Search by name, description, brand, or SKU
    search_term = f"%{query}%"
    db_query = db_query.filter(
        db.or_(
            Product.name.ilike(search_term),
            Product.description.ilike(search_term),
            Product.brand.ilike(search_term),
            Product.sku.ilike(search_term)
        )
    )

    # Filter by category if provided
    if category:
        db_query = db_query.filter(Product.category.ilike(f'%{category}%'))

    # Order by relevance (name first, then description)
    db_query = db_query.order_by(
        db.case(
            (Product.name.ilike(f'%{query}%'), 1),
            (Product.description.ilike(f'%{query}%'), 2),
            else_=3
        ),
        Product.name.asc()
    )

    # Pagination
    pagination = db_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    products = []
    for product in pagination.items:
        products.append(product.to_dict())

    return jsonify({
        'products': products,
        'search_query': query,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

# GET /api/products/categories - List product categories
@bp.route('/categories', methods=['GET'])
def get_categories():
    # Get unique categories from active products
    categories = db.session.query(Product.category).filter(
        Product.is_active == True
    ).distinct().all()

    category_list = [cat[0] for cat in categories if cat[0]]
    category_list.sort()

    return jsonify({
        'categories': category_list
    }), 200

# POST /api/products/calculate-discount - Calculate discount for cart
@bp.route('/calculate-discount', methods=['POST'])
@jwt_required()
def calculate_discount():
    data = request.get_json()
    cart_items = data.get('cart_items', [])
    coupon_code = data.get('coupon_code', '').strip()

    if not cart_items:
        return jsonify({'error': 'Cart items are required'}), 400

    if not coupon_code:
        return jsonify({'error': 'Coupon code is required'}), 400

    # Calculate cart total
    cart_total = 0
    cart_products = []

    for item in cart_items:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)

        product = Product.query.get(product_id)
        if not product or not product.is_active:
            return jsonify({'error': f'Product {product_id} not found or inactive'}), 404

        if product.stock_quantity < quantity:
            return jsonify({'error': f'Insufficient stock for {product.name}'}), 400

        line_total = float(product.price) * quantity
        cart_total += line_total

        cart_products.append({
            'product_id': product.id,
            'product_name': product.name,
            'category': product.category,
            'quantity': quantity,
            'unit_price': float(product.price),
            'line_total': line_total
        })

    # Find and validate coupon
    from app.models import Coupon
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
    if coupon.minimum_order_value and cart_total < float(coupon.minimum_order_value):
        return jsonify({
            'error': f'Minimum order value of ${coupon.minimum_order_value} required',
            'current_total': cart_total,
            'minimum_required': float(coupon.minimum_order_value)
        }), 400

    # Check applicable categories
    if coupon.get_applicable_categories():
        cart_categories = set(item['category'] for item in cart_products)
        applicable_categories = set(coupon.get_applicable_categories())

        if not cart_categories.intersection(applicable_categories):
            return jsonify({
                'error': f'Coupon only applies to categories: {", ".join(applicable_categories)}'
            }), 400

    # Calculate discount
    discount_amount = 0
    if coupon.discount_type == 'percentage':
        discount_amount = (cart_total * coupon.discount_value) / 100
        # Apply maximum discount cap if set
        if coupon.maximum_discount_amount:
            discount_amount = min(discount_amount, float(coupon.maximum_discount_amount))
    elif coupon.discount_type == 'fixed':
        discount_amount = min(coupon.discount_value, cart_total)

    final_total = cart_total - discount_amount

    return jsonify({
        'cart_total': cart_total,
        'discount_amount': round(discount_amount, 2),
        'final_total': round(final_total, 2),
        'coupon': {
            'code': coupon.code,
            'title': coupon.title,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'minimum_order_value': float(coupon.minimum_order_value) if coupon.minimum_order_value else 0,
            'applicable_categories': coupon.get_applicable_categories(),
            'maximum_discount_amount': float(coupon.maximum_discount_amount) if coupon.maximum_discount_amount else None
        },
        'cart_items': cart_products
    }), 200
