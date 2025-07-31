from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User, Coupon, Redemption
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import datetime
import re

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
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
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

    if not is_valid_date_range(start_date, end_date):
        return jsonify({'error': 'Invalid date range'}), 400

    if not is_valid_discount(discount_type, discount_value):
        return jsonify({'error': 'Invalid discount value'}), 400

    if max_uses <= 0:
        return jsonify({'error': 'Max uses must be greater than 0'}), 400

    # Get admin user
    user_id = get_jwt_identity()
    admin_user = User.query.get(int(user_id))

    coupon = Coupon(
        code=code,
        title=title,
        description=description,
        discount_type=discount_type,
        discount_value=discount_value,
        is_public=is_public,
        max_uses=max_uses,
        current_uses=0,
        start_date=datetime.datetime.strptime(start_date, '%Y-%m-%d'),
        end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d'),
        created_by=admin_user.id,
        is_active=True,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )

    db.session.add(coupon)
    db.session.commit()

    return jsonify({
        'message': 'Coupon created successfully',
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
            'created_at': coupon.created_at.isoformat()
        }
    }), 201

# GET /api/admin/coupons - List all coupons with pagination
@bp.route('/coupons', methods=['GET'])
@jwt_required()
@admin_required
def list_coupons():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', 'all')  # all, active, inactive

    query = Coupon.query

    # Filter by status
    if status == 'active':
        query = query.filter(Coupon.is_active == True)
    elif status == 'inactive':
        query = query.filter(Coupon.is_active == False)

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
            'created_at': coupon.created_at.isoformat()
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
            'start_date': coupon.start_date.strftime('%Y-%m-%d'),
            'end_date': coupon.end_date.strftime('%Y-%m-%d'),
            'is_active': coupon.is_active,
            'created_at': coupon.created_at.isoformat(),
            'updated_at': coupon.updated_at.isoformat(),
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
                       'max_uses', 'start_date', 'end_date', 'is_active']

    for field in updatable_fields:
        if field in data:
            if field in ['start_date', 'end_date']:
                try:
                    date_value = datetime.datetime.strptime(data[field], '%Y-%m-%d')
                    setattr(coupon, field, date_value)
                except ValueError:
                    return jsonify({'error': f'Invalid {field} format'}), 400
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
            'updated_at': coupon.updated_at.isoformat()
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

    query = Redemption.query.filter_by(coupon_id=coupon_id)
    query = query.order_by(Redemption.redeemed_at.desc())

    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    redemptions = []
    for redemption in pagination.items:
        redemptions.append({
            'id': redemption.id,
            'user': {
                'id': redemption.user.id,
                'username': redemption.user.username,
                'email': redemption.user.email,
                'first_name': redemption.user.first_name,
                'last_name': redemption.user.last_name
            },
            'discount_applied': redemption.discount_applied,
            'redeemed_at': redemption.redeemed_at.isoformat()
        })

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
        Redemption, User, Coupon
    ).select_from(Redemption).join(
        User, Redemption.user_id == User.id
    ).join(
        Coupon, Redemption.coupon_id == Coupon.id
    ).order_by(
        Redemption.redeemed_at.desc()
    ).limit(10).all()

    recent_redemptions_list = []
    for redemption, user, coupon in recent_redemptions:
        recent_redemptions_list.append({
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
        })

    # Total redemptions
    total_redemptions = Redemption.query.count()

    # Expired coupons
    expired_coupons = Coupon.query.filter(
        Coupon.end_date < datetime.datetime.utcnow()
    ).count()

    return jsonify({
        'stats': {
            'total_coupons': total_coupons,
            'active_coupons': active_coupons,
            'inactive_coupons': inactive_coupons,
            'public_coupons': public_coupons,
            'private_coupons': private_coupons,
            'total_redemptions': total_redemptions,
            'expired_coupons': expired_coupons
        },
        'most_redeemed_coupons': most_redeemed_list,
        'recent_redemptions': recent_redemptions_list
    }), 200
