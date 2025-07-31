from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User, Coupon, Redemption
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
import re

bp = Blueprint('user', __name__, url_prefix='/api/user')

# Helper: validate phone number format
def is_valid_phone(phone):
    # Basic phone validation - allows +, digits, spaces, hyphens, parentheses
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    return re.match(r'^\+?[\d]{7,15}$', phone_clean) is not None

# Helper: validate password strength
def is_valid_password(password):
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"

# Helper: check password
def check_password(password, hashed):
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Helper: hash password
def hash_password(password):
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# GET /api/user/profile - Get user profile
@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'profile': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'email_verified': user.email_verified,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        }
    }), 200

# PUT /api/user/profile - Update profile information
@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    updatable_fields = ['first_name', 'last_name', 'phone']

    # Validate input data
    for field in updatable_fields:
        if field in data:
            value = data[field].strip() if isinstance(data[field], str) else data[field]

            if field in ['first_name', 'last_name']:
                if not value or len(value) < 2:
                    return jsonify({'error': f'{field.replace("_", " ").title()} must be at least 2 characters'}), 400
                if len(value) > 50:
                    return jsonify({'error': f'{field.replace("_", " ").title()} must be less than 50 characters'}), 400

            elif field == 'phone':
                if value and not is_valid_phone(value):
                    return jsonify({'error': 'Invalid phone number format'}), 400

            setattr(user, field, value)

    user.updated_at = datetime.datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'profile': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'email_verified': user.email_verified,
            'updated_at': user.updated_at.isoformat()
        }
    }), 200

# POST /api/user/change-password - Change password
@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400

    # Verify current password
    if not check_password(current_password, user.password_hash):
        return jsonify({'error': 'Current password is incorrect'}), 401

    # Validate new password
    is_valid, error_message = is_valid_password(new_password)
    if not is_valid:
        return jsonify({'error': error_message}), 400

    # Hash new password
    new_password_hash = hash_password(new_password)
    user.password_hash = new_password_hash
    user.updated_at = datetime.datetime.utcnow()

    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200

# POST /api/user/delete-account - Delete user account
@bp.route('/delete-account', methods=['POST'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    password = data.get('password', '')

    if not password:
        return jsonify({'error': 'Password is required to delete account'}), 400

    # Verify password
    if not check_password(password, user.password_hash):
        return jsonify({'error': 'Password is incorrect'}), 401

    # Check if user has any redemptions
    redemptions_count = Redemption.query.filter_by(user_id=user.id).count()
    if redemptions_count > 0:
        return jsonify({
            'error': 'Cannot delete account with existing redemptions',
            'redemptions_count': redemptions_count
        }), 400

    # Delete user account
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Account deleted successfully'}), 200

# GET /api/user/stats - User statistics
@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get user's redemptions
    redemptions = Redemption.query.filter_by(user_id=user.id).order_by(
        Redemption.redeemed_at.desc()
    ).all()

    # Calculate total statistics
    total_redemptions = len(redemptions)
    total_savings = sum(r.discount_applied for r in redemptions)

    # Get recent redemptions (last 5)
    recent_redemptions = []
    for redemption in redemptions[:5]:
        coupon = Coupon.query.get(redemption.coupon_id)
        recent_redemptions.append({
            'id': redemption.id,
            'coupon_code': coupon.code if coupon else 'Unknown',
            'coupon_title': coupon.title if coupon else 'Unknown',
            'discount_applied': redemption.discount_applied,
            'redeemed_at': redemption.redeemed_at.isoformat()
        })

    # Get available public coupons count
    now = datetime.datetime.utcnow()
    available_coupons = Coupon.query.filter(
        Coupon.is_public == True,
        Coupon.is_active == True,
        Coupon.start_date <= now,
        Coupon.end_date >= now,
        Coupon.current_uses < Coupon.max_uses
    ).count()

    # Get monthly redemption trends (last 6 months)
    monthly_trends = []
    for i in range(6):
        month_start = (datetime.datetime.utcnow() - datetime.timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = month_start.replace(day=28) + datetime.timedelta(days=4)
        month_end = month_end.replace(day=1) - datetime.timedelta(days=1)

        month_redemptions = Redemption.query.filter(
            Redemption.user_id == user.id,
            Redemption.redeemed_at >= month_start,
            Redemption.redeemed_at <= month_end
        ).count()

        monthly_trends.append({
            'month': month_start.strftime('%Y-%m'),
            'redemptions': month_redemptions
        })

    # Get favorite coupon types
    coupon_types = {}
    for redemption in redemptions:
        coupon = Coupon.query.get(redemption.coupon_id)
        if coupon:
            discount_type = coupon.discount_type
            coupon_types[discount_type] = coupon_types.get(discount_type, 0) + 1

    favorite_type = max(coupon_types.items(), key=lambda x: x[1]) if coupon_types else None

    return jsonify({
        'stats': {
            'total_redemptions': total_redemptions,
            'total_savings': round(total_savings, 2),
            'available_coupons': available_coupons,
            'account_age_days': (datetime.datetime.utcnow() - user.created_at).days
        },
        'recent_redemptions': recent_redemptions,
        'monthly_trends': monthly_trends,
        'favorite_coupon_type': {
            'type': favorite_type[0] if favorite_type else None,
            'count': favorite_type[1] if favorite_type else 0
        },
        'coupon_type_breakdown': coupon_types
    }), 200

# GET /api/user/dashboard - User dashboard data
@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_user_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get user's redemptions with coupon details
    redemptions_query = db.session.query(
        Redemption, Coupon
    ).join(
        Coupon, Redemption.coupon_id == Coupon.id
    ).filter(
        Redemption.user_id == user.id
    ).order_by(
        Redemption.redeemed_at.desc()
    )

    redemptions = redemptions_query.limit(10).all()

    # Calculate statistics
    total_redemptions = redemptions_query.count()
    total_savings = sum(r[0].discount_applied for r in redemptions)

    # Get available public coupons
    now = datetime.datetime.utcnow()
    available_coupons = Coupon.query.filter(
        Coupon.is_public == True,
        Coupon.is_active == True,
        Coupon.start_date <= now,
        Coupon.end_date >= now,
        Coupon.current_uses < Coupon.max_uses
    ).limit(5).all()

    # Format available coupons
    available_coupons_list = []
    for coupon in available_coupons:
        available_coupons_list.append({
            'id': coupon.id,
            'code': coupon.code,
            'title': coupon.title,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'days_remaining': (coupon.end_date - now).days
        })

    # Format recent redemptions
    recent_redemptions_list = []
    for redemption, coupon in redemptions:
        recent_redemptions_list.append({
            'id': redemption.id,
            'coupon_code': coupon.code,
            'coupon_title': coupon.title,
            'discount_applied': redemption.discount_applied,
            'redeemed_at': redemption.redeemed_at.isoformat()
        })

    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        },
        'overview': {
            'total_redemptions': total_redemptions,
            'total_savings': round(total_savings, 2),
            'available_coupons_count': len(available_coupons_list)
        },
        'recent_redemptions': recent_redemptions_list,
        'available_coupons': available_coupons_list
    }), 200
