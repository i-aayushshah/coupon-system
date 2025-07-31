from flask import Blueprint, jsonify
from app import db
from app.models import User

bp = Blueprint('test_db', __name__, url_prefix='/api/test')

@bp.route('/db', methods=['GET'])
def test_db():
    try:
        db.create_all()
        return jsonify({'message': 'Database initialized successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/make-admin/<int:user_id>', methods=['POST'])
def make_admin(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.is_admin = True
        db.session.commit()

        return jsonify({
            'message': f'User {user.username} is now an admin',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
