from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User, Coupon, Redemption, Product, Order, OrderItem
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import datetime
import re
import csv
from io import StringIO

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Admin middleware decorator
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

# Helper: validate coupon code format
def is_valid_coupon_code(code):
    # Allow alphanumeric and hyphens, 3-20 characters
    return re.match(r'^[A-Za-z0-9-]{3,20}$', code) is not None

# Helper: validate date range
def is_valid_date_range(start_date, end_date):
    try:
        start = parse_date_string(start_date)
        end = parse_date_string(end_date)
        return start < end
    except ValueError:
        return False

# Helper: validate discount values
def is_valid_discount(discount_type, discount_value):
    if discount_type == 'percentage':
        return 0 < discount_value <= 100
    elif discount_type == 'fixed':
        return discount_value > 0
    return False

# Helper: parse date string to datetime
def parse_date_string(date_str):
    """Parse date string that could be in date or datetime format"""
    try:
        if 'T' in date_str:
            # Try different datetime formats
            if ':' in date_str.split('T')[1]:
                time_part = date_str.split('T')[1]
                if time_part.count(':') == 2:
                    # Full ISO format: "2024-01-01T10:30:00"
                    return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                else:
                    # datetime-local format: "2024-01-01T10:30"
                    return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            else:
                # Date with T but no time: "2024-01-01T"
                return datetime.datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
        else:
            # date-only format: "2024-01-01"
            return datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f'Invalid date format. Expected YYYY-MM-DD, YYYY-MM-DDTHH:MM, or YYYY-MM-DDTHH:MM:SS, got: {date_str}')

# Helper: validate product data
def is_valid_product_data(data):
    required_fields = ['name', 'price', 'category']
    if not all(field in data for field in required_fields):
        return False, 'Missing required fields'

    if not data['name'].strip():
        return False, 'Product name is required'

    try:
        price = float(data['price'])
        if price <= 0:
            return False, 'Price must be greater than 0'
    except (ValueError, TypeError):
        return False, 'Invalid price format'

    if not data['category'].strip():
        return False, 'Category is required'

    return True, 'Valid'

# POST /api/admin/products - Create new product
@bp.route('/products', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    data = request.get_json()

    # Validate data
    is_valid, error_message = is_valid_product_data(data)
    if not is_valid:
        return jsonify({'error': error_message}), 400

    # Check if SKU already exists
    sku = data.get('sku', '').strip()
    if sku and Product.query.filter_by(sku=sku).first():
        return jsonify({'error': 'SKU already exists'}), 409

    # Get admin user
    user_id = get_jwt_identity()
    admin_user = User.query.get(int(user_id))

    product = Product(
        name=data['name'].strip(),
        description=data.get('description', '').strip(),
        price=float(data['price']),
        category=data['category'].strip(),
        brand=data.get('brand', '').strip(),
        sku=sku,
        stock_quantity=data.get('stock_quantity', 0),
        is_active=data.get('is_active', True),
        image_url=data.get('image_url', '').strip(),
        minimum_order_value=float(data.get('minimum_order_value', 0)),
        created_by=admin_user.id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201

# GET /api/admin/products - List all products with pagination
@bp.route('/products', methods=['GET'])
@jwt_required()
@admin_required
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', '').strip()
    status = request.args.get('status', 'all')  # all, active, inactive

    query = Product.query

    # Apply filters
    if category:
        query = query.filter(Product.category.ilike(f'%{category}%'))

    if status == 'active':
        query = query.filter(Product.is_active == True)
    elif status == 'inactive':
        query = query.filter(Product.is_active == False)

    # Order by creation date
    query = query.order_by(Product.created_at.desc())

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

# GET /api/admin/products/<id> - Get specific product
@bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_product(product_id):
    product = Product.query.get_or_404(product_id)

    return jsonify({
        'product': product.to_dict()
    }), 200

# PUT /api/admin/products/<id> - Update product
@bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    # Fields that can be updated
    updatable_fields = ['name', 'description', 'price', 'category', 'brand',
                       'sku', 'stock_quantity', 'is_active', 'image_url',
                       'minimum_order_value']

    for field in updatable_fields:
        if field in data:
            if field == 'price':
                try:
                    setattr(product, field, float(data[field]))
                except (ValueError, TypeError):
                    return jsonify({'error': 'Invalid price format'}), 400
            elif field == 'stock_quantity':
                try:
                    setattr(product, field, int(data[field]))
                except (ValueError, TypeError):
                    return jsonify({'error': 'Invalid stock quantity format'}), 400
            elif field == 'minimum_order_value':
                try:
                    setattr(product, field, float(data[field]))
                except (ValueError, TypeError):
                    return jsonify({'error': 'Invalid minimum order value format'}), 400
            else:
                setattr(product, field, data[field])

    # Check SKU uniqueness if updated
    if 'sku' in data and data['sku']:
        existing_product = Product.query.filter_by(sku=data['sku']).first()
        if existing_product and existing_product.id != product_id:
            return jsonify({'error': 'SKU already exists'}), 409

    product.updated_at = datetime.datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    }), 200

# DELETE /api/admin/products/<id> - Delete product
@bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    # Check if product has been ordered
    if product.order_items.count() > 0:
        return jsonify({'error': 'Cannot delete product that has been ordered'}), 400

    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'}), 200

# POST /api/admin/products/bulk-upload - CSV bulk upload
@bp.route('/products/bulk-upload', methods=['POST'])
@jwt_required()
@admin_required
def bulk_upload_products():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400

    try:
        # Read CSV file
        csv_data = file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_data))

        # Get admin user
        user_id = get_jwt_identity()
        admin_user = User.query.get(int(user_id))

        success_count = 0
        error_count = 0
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 (header is row 1)
            try:
                # Validate required fields
                if not row.get('name') or not row.get('price') or not row.get('category'):
                    errors.append(f'Row {row_num}: Missing required fields')
                    error_count += 1
                    continue

                # Check SKU uniqueness
                sku = row.get('sku', '').strip()
                if sku and Product.query.filter_by(sku=sku).first():
                    errors.append(f'Row {row_num}: SKU already exists')
                    error_count += 1
                    continue

                # Create product
                product = Product(
                    name=row['name'].strip(),
                    description=row.get('description', '').strip(),
                    price=float(row['price']),
                    category=row['category'].strip(),
                    brand=row.get('brand', '').strip(),
                    sku=sku,
                    stock_quantity=int(row.get('stock_quantity', 0)),
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    image_url=row.get('image_url', '').strip(),
                    minimum_order_value=float(row.get('minimum_order_value', 0)),
                    created_by=admin_user.id,
                    created_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow()
                )

                db.session.add(product)
                success_count += 1

            except (ValueError, TypeError) as e:
                errors.append(f'Row {row_num}: Invalid data format - {str(e)}')
                error_count += 1
                continue

        db.session.commit()

        return jsonify({
            'message': 'Bulk upload completed',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process CSV file: {str(e)}'}), 500

# POST /api/admin/coupons - Create new coupon
@bp.route('/coupons', methods=['POST'])
@jwt_required()
@admin_required
def create_coupon():
    data = request.get_json()
    required_fields = ['code', 'title', 'description', 'discount_type', 'discount_value',
                      'is_public', 'max_uses', 'start_date', 'end_date']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    code = data['code'].strip().upper()
    title = data['title'].strip()
    description = data['description'].strip()
    discount_type = data['discount_type']
    discount_value = data['discount_value']
    is_public = data['is_public']
    max_uses = data['max_uses']
    start_date = data['start_date']
    end_date = data['end_date']

    # Validation
    if not is_valid_coupon_code(code):
        return jsonify({'error': 'Invalid coupon code format'}), 400

    if Coupon.query.filter_by(code=code).first():
        return jsonify({'error': 'Coupon code already exists'}), 409

    # Parse dates
    try:
        start_datetime = parse_date_string(start_date)
        end_datetime = parse_date_string(end_date)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    if not is_valid_date_range(start_date, end_date):
        return jsonify({'error': 'Invalid date range'}), 400

    if not is_valid_discount(discount_type, discount_value):
        return jsonify({'error': 'Invalid discount value'}), 400

    if max_uses <= 0:
        return jsonify({'error': 'Max uses must be greater than 0'}), 400

    # Get admin user
    user_id = get_jwt_identity()
    admin_user = User.query.get(int(user_id))

    # Enhanced coupon fields
    minimum_order_value = data.get('minimum_order_value', 0)
    applicable_categories = data.get('applicable_categories', [])
    maximum_discount_amount = data.get('maximum_discount_amount')
    first_time_user_only = data.get('first_time_user_only', False)

    coupon = Coupon(
        code=code,
        title=title,
        description=description,
        discount_type=discount_type,
        discount_value=discount_value,
        is_public=is_public,
        max_uses=max_uses,
        current_uses=0,
        start_date=start_datetime,
        end_date=end_datetime,
        created_by=admin_user.id,
        is_active=True,
        minimum_order_value=minimum_order_value,
        maximum_discount_amount=maximum_discount_amount,
        first_time_user_only=first_time_user_only,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )

    # Set applicable categories
    coupon.set_applicable_categories(applicable_categories)

    db.session.add(coupon)
    db.session.commit()

    return jsonify({
        'message': 'Coupon created successfully',
        'coupon': coupon.to_dict()
    }), 201

# GET /api/admin/coupons - List all coupons with pagination
@bp.route('/coupons', methods=['GET'])
@jwt_required()
@admin_required
def list_coupons():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', 'all')  # all, active, inactive
    search = request.args.get('search', '').strip()

    query = Coupon.query

    # Filter by status
    now = datetime.datetime.utcnow()
    if status == 'active':
        # Active: is_active=True AND current date is between start and end dates
        query = query.filter(
            Coupon.is_active == True,
            Coupon.start_date <= now,
            Coupon.end_date >= now
        )
    elif status == 'inactive':
        # Inactive: is_active=False
        query = query.filter(Coupon.is_active == False)
    elif status == 'expired':
        # Expired: end_date has passed
        query = query.filter(Coupon.end_date < now)
    elif status == 'pending':
        # Pending: start_date is in the future
        query = query.filter(Coupon.start_date > now)

    # Search functionality
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Coupon.code.ilike(search_term),
                Coupon.title.ilike(search_term),
                Coupon.description.ilike(search_term)
            )
        )

    # Order by creation date
    query = query.order_by(Coupon.created_at.desc())

    # Pagination
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    coupons = []
    for coupon in pagination.items:
        coupons.append({
            'id': coupon.id,
            'code': coupon.code,
            'title': coupon.title,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'is_public': coupon.is_public,
            'max_uses': coupon.max_uses,
            'current_uses': coupon.current_uses,
            'start_date': coupon.start_date.strftime('%Y-%m-%d'),
            'end_date': coupon.end_date.strftime('%Y-%m-%d'),
            'is_active': coupon.is_active,
            'created_at': coupon.created_at.isoformat(),
            # Enhanced fields for product integration
            'minimum_order_value': float(coupon.minimum_order_value) if coupon.minimum_order_value else 0,
            'applicable_categories': coupon.get_applicable_categories(),
            'maximum_discount_amount': float(coupon.maximum_discount_amount) if coupon.maximum_discount_amount else None,
            'first_time_user_only': coupon.first_time_user_only
        })

    return jsonify({
        'coupons': coupons,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

# GET /api/admin/coupons/<id> - Get specific coupon details
@bp.route('/coupons/<int:coupon_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)

    return jsonify({
        'coupon': {
            'id': coupon.id,
            'code': coupon.code,
            'title': coupon.title,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'is_public': coupon.is_public,
            'max_uses': coupon.max_uses,
            'current_uses': coupon.current_uses,
            'start_date': coupon.start_date.isoformat() if coupon.start_date else None,
            'end_date': coupon.end_date.isoformat() if coupon.end_date else None,
            'is_active': coupon.is_active,
            'created_at': coupon.created_at.isoformat(),
            'updated_at': coupon.updated_at.isoformat(),
            # Enhanced fields for product integration
            'minimum_order_value': float(coupon.minimum_order_value) if coupon.minimum_order_value else 0,
            'applicable_categories': coupon.get_applicable_categories(),
            'maximum_discount_amount': float(coupon.maximum_discount_amount) if coupon.maximum_discount_amount else None,
            'first_time_user_only': coupon.first_time_user_only,
            'creator': {
                'id': coupon.creator.id,
                'username': coupon.creator.username,
                'email': coupon.creator.email
            } if coupon.creator else None
        }
    }), 200

# PUT /api/admin/coupons/<id> - Update coupon
@bp.route('/coupons/<int:coupon_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    data = request.get_json()

    # Fields that can be updated
    updatable_fields = ['title', 'description', 'discount_value', 'is_public',
                       'max_uses', 'start_date', 'end_date', 'is_active',
                       'minimum_order_value', 'applicable_categories',
                       'maximum_discount_amount', 'first_time_user_only']

    for field in updatable_fields:
        if field in data:
            if field in ['start_date', 'end_date']:
                try:
                    date_value = parse_date_string(data[field])
                    setattr(coupon, field, date_value)
                except ValueError as e:
                    return jsonify({'error': str(e)}), 400
            elif field == 'applicable_categories':
                # Handle JSON field for categories
                if isinstance(data[field], list):
                    coupon.set_applicable_categories(data[field])
                else:
                    return jsonify({'error': 'applicable_categories must be a list'}), 400
            elif field in ['minimum_order_value', 'maximum_discount_amount']:
                # Handle decimal fields
                try:
                    decimal_value = float(data[field]) if data[field] is not None else None
                    if decimal_value is not None and decimal_value < 0:
                        return jsonify({'error': f'{field} cannot be negative'}), 400
                    setattr(coupon, field, decimal_value)
                except (ValueError, TypeError):
                    return jsonify({'error': f'Invalid {field} format'}), 400
            elif field == 'first_time_user_only':
                # Handle boolean field
                if not isinstance(data[field], bool):
                    return jsonify({'error': 'first_time_user_only must be a boolean'}), 400
                setattr(coupon, field, data[field])
            else:
                setattr(coupon, field, data[field])

    # Validation
    if hasattr(coupon, 'start_date') and hasattr(coupon, 'end_date'):
        if not is_valid_date_range(coupon.start_date.strftime('%Y-%m-%d'),
                                 coupon.end_date.strftime('%Y-%m-%d')):
            return jsonify({'error': 'Invalid date range'}), 400

    if 'discount_value' in data:
        if not is_valid_discount(coupon.discount_type, data['discount_value']):
            return jsonify({'error': 'Invalid discount value'}), 400

    if 'max_uses' in data and data['max_uses'] <= 0:
        return jsonify({'error': 'Max uses must be greater than 0'}), 400

    coupon.updated_at = datetime.datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Coupon updated successfully',
        'coupon': {
            'id': coupon.id,
            'code': coupon.code,
            'title': coupon.title,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'is_public': coupon.is_public,
            'max_uses': coupon.max_uses,
            'current_uses': coupon.current_uses,
            'start_date': coupon.start_date.strftime('%Y-%m-%d'),
            'end_date': coupon.end_date.strftime('%Y-%m-%d'),
            'is_active': coupon.is_active,
            'updated_at': coupon.updated_at.isoformat(),
            # Enhanced fields for product integration
            'minimum_order_value': float(coupon.minimum_order_value) if coupon.minimum_order_value else 0,
            'applicable_categories': coupon.get_applicable_categories(),
            'maximum_discount_amount': float(coupon.maximum_discount_amount) if coupon.maximum_discount_amount else None,
            'first_time_user_only': coupon.first_time_user_only
        }
    }), 200

# DELETE /api/admin/coupons/<id> - Delete coupon
@bp.route('/coupons/<int:coupon_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)

    # Check if coupon has been used
    if coupon.current_uses > 0:
        return jsonify({'error': 'Cannot delete coupon that has been used'}), 400

    db.session.delete(coupon)
    db.session.commit()

    return jsonify({'message': 'Coupon deleted successfully'}), 200

# GET /api/admin/coupons/<id>/redemptions - View redemption history
@bp.route('/coupons/<int:coupon_id>/redemptions', methods=['GET'])
@jwt_required()
@admin_required
def get_coupon_redemptions(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = db.session.query(Redemption, User, Order).join(
        User, Redemption.user_id == User.id
    ).outerjoin(
        Order, Redemption.order_id == Order.id
    ).filter(
        Redemption.coupon_id == coupon_id
    ).order_by(Redemption.redeemed_at.desc())

    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    redemptions = []
    for redemption, user, order in pagination.items:
        redemption_data = {
            'id': redemption.id,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'discount_applied': redemption.discount_applied,
            'redeemed_at': redemption.redeemed_at.isoformat()
        }

        if order:
            redemption_data['order'] = {
                'id': order.id,
                'order_status': order.order_status,
                'subtotal': float(order.subtotal),
                'final_total': float(order.final_total),
                'created_at': order.created_at.isoformat()
            }

            # Add product information if available
            if redemption.original_amount and redemption.final_amount:
                redemption_data['order']['original_amount'] = float(redemption.original_amount)
                redemption_data['order']['final_amount'] = float(redemption.final_amount)
                redemption_data['order']['products_applied_to'] = redemption.get_products_applied_to()

        redemptions.append(redemption_data)

    return jsonify({
        'coupon': {
            'id': coupon.id,
            'code': coupon.code,
            'title': coupon.title,
            'current_uses': coupon.current_uses,
            'max_uses': coupon.max_uses
        },
        'redemptions': redemptions,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

# GET /api/admin/dashboard - Dashboard stats
@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def admin_dashboard():
    # Total coupons
    total_coupons = Coupon.query.count()

    # Active vs inactive coupons
    active_coupons = Coupon.query.filter_by(is_active=True).count()
    inactive_coupons = Coupon.query.filter_by(is_active=False).count()

    # Public vs private coupons
    public_coupons = Coupon.query.filter_by(is_public=True).count()
    private_coupons = Coupon.query.filter_by(is_public=False).count()

    # Product statistics
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    low_stock_products = Product.query.filter(Product.stock_quantity < 10).count()

    # Order statistics
    total_orders = Order.query.count()
    completed_orders = Order.query.filter_by(order_status='completed').count()
    total_revenue = db.session.query(db.func.sum(Order.final_total)).scalar() or 0

    # Most redeemed coupons (top 5)
    most_redeemed = db.session.query(
        Coupon, db.func.count(Redemption.id).label('redemption_count')
    ).outerjoin(Redemption, Coupon.id == Redemption.coupon_id).group_by(Coupon.id).order_by(
        db.func.count(Redemption.id).desc()
    ).limit(5).all()

    most_redeemed_list = []
    for coupon, count in most_redeemed:
        most_redeemed_list.append({
            'id': coupon.id,
            'code': coupon.code,
            'title': coupon.title,
            'redemption_count': count
        })

    # Recent redemptions (last 10) - Fixed with explicit joins
    recent_redemptions = db.session.query(
        Redemption, User, Coupon, Order
    ).select_from(Redemption).join(
        User, Redemption.user_id == User.id
    ).join(
        Coupon, Redemption.coupon_id == Coupon.id
    ).outerjoin(
        Order, Redemption.order_id == Order.id
    ).order_by(
        Redemption.redeemed_at.desc()
    ).limit(10).all()

    recent_redemptions_list = []
    for redemption, user, coupon, order in recent_redemptions:
        redemption_data = {
            'id': redemption.id,
            'user': {
                'username': user.username,
                'email': user.email
            },
            'coupon': {
                'code': coupon.code,
                'title': coupon.title
            },
            'discount_applied': redemption.discount_applied,
            'redeemed_at': redemption.redeemed_at.isoformat()
        }

        if order:
            redemption_data['order'] = {
                'id': order.id,
                'order_status': order.order_status,
                'final_total': float(order.final_total)
            }

        recent_redemptions_list.append(redemption_data)

    # Total redemptions
    total_redemptions = Redemption.query.count()

    # Expired coupons
    expired_coupons = Coupon.query.filter(
        Coupon.end_date < datetime.datetime.utcnow()
    ).count()

    # Top selling products
    top_products = db.session.query(
        Product, db.func.sum(OrderItem.quantity).label('total_sold')
    ).join(
        OrderItem, Product.id == OrderItem.product_id
    ).group_by(
        Product.id
    ).order_by(
        db.func.sum(OrderItem.quantity).desc()
    ).limit(5).all()

    top_products_list = []
    for product, total_sold in top_products:
        top_products_list.append({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'total_sold': total_sold,
            'current_stock': product.stock_quantity
        })

    return jsonify({
        'stats': {
            'total_coupons': total_coupons,
            'active_coupons': active_coupons,
            'inactive_coupons': inactive_coupons,
            'public_coupons': public_coupons,
            'private_coupons': private_coupons,
            'total_redemptions': total_redemptions,
            'expired_coupons': expired_coupons,
            'total_products': total_products,
            'active_products': active_products,
            'low_stock_products': low_stock_products,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_revenue': round(float(total_revenue), 2)
        },
        'most_redeemed_coupons': most_redeemed_list,
        'recent_redemptions': recent_redemptions_list,
        'top_selling_products': top_products_list
    }), 200

# GET /api/admin/users - List all users with pagination
@bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '').strip()

    query = User.query

    # Apply search filter
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )

    # Order by creation date
    query = query.order_by(User.created_at.desc())

    # Pagination
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = []
    for user in pagination.items:
        users.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user.is_admin,
            'email_verified': user.email_verified,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        })

    return jsonify({
        'users': users,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

# GET /api/admin/users/<id> - Get specific user details
@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)

    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'email_verified': user.email_verified,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    }), 200

# GET /api/admin/users/<id>/stats - Get user statistics
@bp.route('/users/<int:user_id>/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_user_stats(user_id):
    user = User.query.get_or_404(user_id)

    # Get user's redemption count
    redemption_count = Redemption.query.filter_by(user_id=user_id).count()

    # Get user's total savings
    total_savings = db.session.query(db.func.sum(Redemption.discount_applied)).filter(
        Redemption.user_id == user_id
    ).scalar() or 0

    # Get user's order count
    order_count = Order.query.filter_by(user_id=user_id).count()

    # Get user's total spent
    total_spent = db.session.query(db.func.sum(Order.final_total)).filter(
        Order.user_id == user_id
    ).scalar() or 0

    # Get recent redemptions (last 5)
    recent_redemptions = db.session.query(
        Redemption, Coupon
    ).join(
        Coupon, Redemption.coupon_id == Coupon.id
    ).filter(
        Redemption.user_id == user_id
    ).order_by(Redemption.redeemed_at.desc()).limit(5).all()

    recent_redemptions_list = []
    for redemption, coupon in recent_redemptions:
        recent_redemptions_list.append({
            'id': redemption.id,
            'coupon_code': coupon.code,
            'coupon_title': coupon.title,
            'discount_applied': redemption.discount_applied,
            'redeemed_at': redemption.redeemed_at.isoformat()
        })

    return jsonify({
        'stats': {
            'redemption_count': redemption_count,
            'total_savings': round(float(total_savings), 2),
            'order_count': order_count,
            'total_spent': round(float(total_spent), 2)
        },
        'recent_redemptions': recent_redemptions_list
    }), 200

# PUT /api/admin/users/<id>/role - Update user admin role
@bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'is_admin' not in data:
        return jsonify({'error': 'is_admin field is required'}), 400

    if not isinstance(data['is_admin'], bool):
        return jsonify({'error': 'is_admin must be a boolean'}), 400

    # Get current admin user
    current_admin_id = get_jwt_identity()

    # Prevent admin from removing their own admin status
    if int(current_admin_id) == user_id and not data['is_admin']:
        return jsonify({'error': 'You cannot remove your own admin status'}), 400

    user.is_admin = data['is_admin']
    user.updated_at = datetime.datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': f'User role updated successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }), 200

# PUT /api/admin/users/<id>/status - Update user status (email verification)
@bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def update_user_status(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'email_verified' not in data:
        return jsonify({'error': 'email_verified field is required'}), 400

    if not isinstance(data['email_verified'], bool):
        return jsonify({'error': 'email_verified must be a boolean'}), 400

    user.email_verified = data['email_verified']
    user.updated_at = datetime.datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': f'User status updated successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'email_verified': user.email_verified
        }
    }), 200

# GET /api/admin/categories - Get all product categories
@bp.route('/categories', methods=['GET'])
@jwt_required()
@admin_required
def get_categories():
    # Get unique categories from products
    categories = db.session.query(Product.category).distinct().filter(
        Product.category.isnot(None),
        Product.category != ''
    ).order_by(Product.category).all()

    # Extract category names from the query result
    category_list = [category[0] for category in categories]

    return jsonify({
        'categories': category_list
    }), 200

# GET /api/admin/activities - Recent activities for admin dashboard
@bp.route('/activities', methods=['GET'])
@jwt_required()
@admin_required
def get_recent_activities():
    # Get recent activities from different sources
    activities = []

    # Recent user registrations (last 7 days)
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    recent_users = User.query.filter(
        User.created_at >= week_ago
    ).order_by(User.created_at.desc()).limit(5).all()

    for user in recent_users:
        activities.append({
            'id': f'user_{user.id}',
            'type': 'user_registered',
            'title': 'New User Registration',
            'description': f'{user.first_name} {user.last_name} joined the platform',
            'timestamp': user.created_at.isoformat(),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })

    # Recent coupon creations (last 7 days)
    recent_coupons = Coupon.query.filter(
        Coupon.created_at >= week_ago
    ).order_by(Coupon.created_at.desc()).limit(5).all()

    for coupon in recent_coupons:
        activities.append({
            'id': f'coupon_{coupon.id}',
            'type': 'coupon_created',
            'title': 'New Coupon Created',
            'description': f'Coupon "{coupon.title}" ({coupon.code}) was created',
            'timestamp': coupon.created_at.isoformat(),
            'coupon': {
                'id': coupon.id,
                'code': coupon.code,
                'title': coupon.title
            }
        })

    # Recent redemptions (last 7 days)
    recent_redemptions = db.session.query(
        Redemption, User, Coupon
    ).join(
        User, Redemption.user_id == User.id
    ).join(
        Coupon, Redemption.coupon_id == Coupon.id
    ).filter(
        Redemption.redeemed_at >= week_ago
    ).order_by(Redemption.redeemed_at.desc()).limit(5).all()

    for redemption, user, coupon in recent_redemptions:
        activities.append({
            'id': f'redemption_{redemption.id}',
            'type': 'coupon_redeemed',
            'title': 'Coupon Redeemed',
            'description': f'{user.first_name} {user.last_name} redeemed {coupon.code}',
            'timestamp': redemption.redeemed_at.isoformat(),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'coupon': {
                'id': coupon.id,
                'code': coupon.code,
                'title': coupon.title
            },
            'discount_applied': redemption.discount_applied
        })

    # Recent orders (last 7 days)
    recent_orders = Order.query.filter(
        Order.created_at >= week_ago
    ).order_by(Order.created_at.desc()).limit(5).all()

    for order in recent_orders:
        activities.append({
            'id': f'order_{order.id}',
            'type': 'order_placed',
            'title': 'New Order Placed',
            'description': f'Order #{order.id} placed for ${order.final_total}',
            'timestamp': order.created_at.isoformat(),
            'order': {
                'id': order.id,
                'order_status': order.order_status,
                'final_total': float(order.final_total)
            }
        })

    # Sort all activities by timestamp (most recent first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)

    # Return only the most recent 10 activities
    return jsonify({
        'activities': activities[:10]
    }), 200
