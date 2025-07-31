from flask import Blueprint, jsonify
from app import db
from app.models import User, Coupon, Redemption

bp = Blueprint('test_db', __name__)

@bp.route('/api/test/db', methods=['GET'])
def test_db():
    try:
        db.create_all()
        return jsonify({'success': True, 'message': 'Database and tables created successfully!'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
