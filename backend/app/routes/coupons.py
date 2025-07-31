from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User, Coupon, Redemption
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
import re

bp = Blueprint('coupons', __name__, url_prefix='/api/coupons')

# Helper: validate coupon for redemption
def validate_coupon_for_redemption(coupon, user_id):
    """Validate if a coupon can be redeemed by a user"""
    errors = []

    # Check if coupon exists and is active
    if not coupon:
        return False, ["Coupon not found"]

    if not coupon.is_active:
        errors.append("Coupon is inactive")

    # Check date validity
    now = datetime.datetime.utcnow()
    if coupon.start_date > now:
        errors.append("Coupon has not started yet")
    if coupon.end_date < now:
        errors.append("Coupon has expired")

    # Check usage limits
    if coupon.current_uses >= coupon.max_uses:
        errors.append("Coupon usage limit reached")

    # Check if user already redeemed this coupon
    existing_redemption = Redemption.query.filter_by(
        user_id=user_id,
        coupon_id=coupon.id
    ).first()

    if existing_redemption:
        errors.append("You have already redeemed this coupon")

    return len(errors) == 0, errors

# Helper: calculate discount amount
def calculate_discount(coupon, order_amount):
    """Calculate the discount amount based on coupon type and order amount"""
    if coupon.discount_type == 'percentage':
        discount_amount = (order_amount * coupon.discount_value) / 100
        return round(discount_amount, 2)
    elif coupon.discount_type == 'fixed':
        # For fixed discount, don't exceed order amount
        return min(coupon.discount_value, order_amount)
    return 0

# GET /api/coupons/public - List all public active coupons
@bp.route('/public', methods=['GET'])
def list_public_coupons():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Query public, active coupons that are within date range
    now = datetime.datetime.utcnow()
    query = Coupon.query.filter(
        Coupon.is_public == True,
        Coupon.is_active == True,
        Coupon.start_date <= now,
        Coupon.end_date >= now,
        Coupon.current_uses < Coupon.max_uses
    ).order_by(Coupon.end_date.asc())  # Show expiring soon first

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
            'max_uses': coupon.max_uses,
            'current_uses': coupon.current_uses,
            'remaining_uses': coupon.max_uses - coupon.current_uses,
            'start_date': coupon.start_date.strftime('%Y-%m-%d'),
            'end_date': coupon.end_date.strftime('%Y-%m-%d'),
            'days_remaining': (coupon.end_date - now).days
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

# GET /api/coupons/validate/<code> - Validate coupon without redeeming
@bp.route('/validate/<code>', methods=['GET'])
def validate_coupon(code):
    coupon = Coupon.query.filter_by(code=code.upper()).first()

    if not coupon:
        return jsonify({
            'valid': False,
            'error': 'Coupon not found'
        }), 404

    # Basic validation
    now = datetime.datetime.utcnow()
    is_valid = True
    errors = []

    if not coupon.is_active:
        is_valid = False
        errors.append("Coupon is inactive")

    if not coupon.is_public:
        is_valid = False
        errors.append("Coupon is not public")

    if coupon.start_date > now:
        is_valid = False
        errors.append("Coupon has not started yet")

    if coupon.end_date < now:
        is_valid = False
        errors.append("Coupon has expired")

    if coupon.current_uses >= coupon.max_uses:
        is_valid = False
        errors.append("Coupon usage limit reached")

    return jsonify({
        'valid': is_valid,
        'coupon': {
            'id': coupon.id,
            'code': coupon.code,
            'title': coupon.title,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'is_public': coupon.is_public,
            'is_active': coupon.is_active,
            'max_uses': coupon.max_uses,
            'current_uses': coupon.current_uses,
            'remaining_uses': coupon.max_uses - coupon.current_uses,
            'start_date': coupon.start_date.strftime('%Y-%m-%d'),
            'end_date': coupon.end_date.strftime('%Y-%m-%d'),
            'days_remaining': (coupon.end_date - now).days
        },
        'errors': errors
    }), 200

# POST /api/coupons/redeem - Redeem a coupon code
@bp.route('/redeem', methods=['POST'])
@jwt_required()
def redeem_coupon():
    data = request.get_json()
    code = data.get('code', '').strip().upper()
    order_amount = data.get('order_amount', 0)

    if not code:
        return jsonify({'error': 'Coupon code is required'}), 400

    if order_amount <= 0:
        return jsonify({'error': 'Order amount must be greater than 0'}), 400

    # Get user
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Find coupon
    coupon = Coupon.query.filter_by(code=code).first()
    if not coupon:
        return jsonify({'error': 'Coupon not found'}), 404

    # Validate coupon for redemption
    is_valid, errors = validate_coupon_for_redemption(coupon, int(user_id))
    if not is_valid:
        return jsonify({
            'error': 'Coupon cannot be redeemed',
            'details': errors
        }), 400

    # Calculate discount
    discount_amount = calculate_discount(coupon, order_amount)

    # Use database transaction to prevent race conditions
    try:
        # Create redemption record
        redemption = Redemption(
            user_id=int(user_id),
            coupon_id=coupon.id,
            redeemed_at=datetime.datetime.utcnow(),
            discount_applied=discount_amount
        )

        # Update coupon usage count
        coupon.current_uses += 1
        coupon.updated_at = datetime.datetime.utcnow()

        # Commit transaction
        db.session.add(redemption)
        db.session.commit()

        return jsonify({
            'message': 'Coupon redeemed successfully',
            'redemption': {
                'id': redemption.id,
                'coupon_code': coupon.code,
                'coupon_title': coupon.title,
                'discount_type': coupon.discount_type,
                'discount_value': coupon.discount_value,
                'order_amount': order_amount,
                'discount_applied': discount_amount,
                'final_amount': order_amount - discount_amount,
                'redeemed_at': redemption.redeemed_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to redeem coupon. Please try again.'}), 500

# GET /api/coupons/search?q=<query> - Search coupons
@bp.route('/search', methods=['GET'])
@jwt_required()
def search_coupons():
    query = request.args.get('q', '').strip()
    discount_type = request.args.get('discount_type', '').strip()
    sort_by = request.args.get('sort_by', 'expiry')  # expiry, discount, name
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    # Build query
    db_query = Coupon.query.filter(
        Coupon.is_public == True,
        Coupon.is_active == True
    )

    # Search by code or title
    search_term = f"%{query}%"
    db_query = db_query.filter(
        db.or_(
            Coupon.code.ilike(search_term),
            Coupon.title.ilike(search_term),
            Coupon.description.ilike(search_term)
        )
    )

    # Filter by discount type
    if discount_type:
        db_query = db_query.filter(Coupon.discount_type == discount_type)

    # Sort results
    if sort_by == 'expiry':
        db_query = db_query.order_by(Coupon.end_date.asc())
    elif sort_by == 'discount':
        db_query = db_query.order_by(Coupon.discount_value.desc())
    elif sort_by == 'name':
        db_query = db_query.order_by(Coupon.title.asc())
    else:
        db_query = db_query.order_by(Coupon.end_date.asc())

    # Pagination
    pagination = db_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    coupons = []
    now = datetime.datetime.utcnow()
    for coupon in pagination.items:
        coupons.append({
            'id': coupon.id,
            'code': coupon.code,
            'title': coupon.title,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'max_uses': coupon.max_uses,
            'current_uses': coupon.current_uses,
            'remaining_uses': coupon.max_uses - coupon.current_uses,
            'start_date': coupon.start_date.strftime('%Y-%m-%d'),
            'end_date': coupon.end_date.strftime('%Y-%m-%d'),
            'days_remaining': (coupon.end_date - now).days,
            'is_expired': coupon.end_date < now
        })

    return jsonify({
        'coupons': coupons,
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

# GET /api/user/redemptions - User's redemption history
@bp.route('/user/redemptions', methods=['GET'])
@jwt_required()
def get_user_redemptions():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Get user's redemptions with coupon details
    query = db.session.query(
        Redemption, Coupon
    ).join(
        Coupon, Redemption.coupon_id == Coupon.id
    ).filter(
        Redemption.user_id == int(user_id)
    ).order_by(
        Redemption.redeemed_at.desc()
    )

    # Pagination
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    redemptions = []
    total_saved = 0

    for redemption, coupon in pagination.items:
        total_saved += redemption.discount_applied
        redemptions.append({
            'id': redemption.id,
            'coupon': {
                'id': coupon.id,
                'code': coupon.code,
                'title': coupon.title,
                'description': coupon.description,
                'discount_type': coupon.discount_type,
                'discount_value': coupon.discount_value
            },
            'discount_applied': redemption.discount_applied,
            'redeemed_at': redemption.redeemed_at.isoformat()
        })

    return jsonify({
        'redemptions': redemptions,
        'total_redemptions': pagination.total,
        'total_saved': round(total_saved, 2),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200
