from flask import Blueprint, request, jsonify, current_app
from app import db, mail
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
import bcrypt
import re
import uuid
import datetime

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Send real email using Flask-Mail
def send_email(to, subject, body):
    try:
        msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[to])
        msg.body = body
        mail.send(msg)
        print(f"Email sent successfully to {to}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to}: {str(e)}")
        return False

# Helper: validate email format
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
def is_valid_email(email):
    return EMAIL_REGEX.match(email)

# Helper: hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Helper: check password
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# POST /api/auth/register
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    first_name = data['first_name'].strip()
    last_name = data['last_name'].strip()

    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    password_hash = hash_password(password)
    verification_token = str(uuid.uuid4())
    verification_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # 24 hour expiration

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        is_admin=False,
        email_verified=False,
        email_verification_token=verification_token,
        email_verification_expires=verification_expires,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.session.add(user)
    db.session.commit()

    # Send verification email (mock)
    verify_url = f"http://localhost:3000/verify-email/{verification_token}?email={email}"
    subject = "Verify your email"
    body = f"Hi {first_name},\n\nPlease verify your email by clicking the link below:\n{verify_url}\n\nIf you did not register, ignore this email."
    send_email(email, subject, body)

    return jsonify({'message': 'Registration successful. Please check your email to verify your account.'}), 201

# POST /api/auth/login
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    resend_verification = data.get('resend_verification', False)

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password_hash):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.email_verified:
        if resend_verification:
            # Generate new verification token
            new_verification_token = str(uuid.uuid4())
            new_verification_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            user.email_verification_token = new_verification_token
            user.email_verification_expires = new_verification_expires
            user.updated_at = datetime.datetime.utcnow()
            db.session.commit()

            # Send new verification email
            verify_url = f"http://localhost:3000/verify-email?token={new_verification_token}&email={email}"
            subject = "Verify your email"
            body = f"Hi {user.first_name},\n\nPlease verify your email by clicking the link below:\n{verify_url}\n\nIf you did not register, ignore this email."
            send_email(email, subject, body)

            return jsonify({
                'error': 'Email not verified',
                'message': 'A new verification email has been sent to your email address.',
                'resend_verification_sent': True
            }), 403
        else:
            return jsonify({
                'error': 'Email not verified',
                'message': 'Please verify your email before logging in. You can request a new verification link by setting resend_verification to true.',
                'resend_verification_available': True
            }), 403

    # Update last login time
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()

    # Create JWT identity with just the user ID as string
    access_token = create_access_token(identity=str(user.id))

    profile = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_admin': user.is_admin
    }

    # Add redirect information for admin users
    response_data = {
        'access_token': access_token,
        'user': profile
    }

    # If user is admin, add redirect flag
    if user.is_admin:
        response_data['redirect_to'] = '/admin'

    return jsonify(response_data), 200

# POST /api/auth/verify-email
@bp.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    token = data.get('token', '').strip()
    if not email or not token:
        return jsonify({'error': 'Missing email or token'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid email or token'}), 400
    if user.email_verified:
        return jsonify({'message': 'Email already verified.'}), 200
    if user.email_verification_token != token:
        return jsonify({'error': 'Invalid verification token'}), 400
    if not user.email_verification_expires or user.email_verification_expires < datetime.datetime.utcnow():
        return jsonify({'error': 'Verification token has expired. Please request a new one.'}), 400
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    user.updated_at = datetime.datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Email verified successfully.'}), 200

# POST /api/auth/resend-verification
@bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    if not email:
        return jsonify({'error': 'Missing email'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return jsonify({'message': 'If the email exists, a verification link has been sent.'}), 200

    if user.email_verified:
        return jsonify({'message': 'Email is already verified.'}), 200

    # Generate new verification token
    new_verification_token = str(uuid.uuid4())
    new_verification_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    user.email_verification_token = new_verification_token
    user.email_verification_expires = new_verification_expires
    user.updated_at = datetime.datetime.utcnow()
    db.session.commit()

    # Send new verification email
    verify_url = f"http://localhost:3000/verify-email/{new_verification_token}?email={email}"
    subject = "Verify your email"
    body = f"Hi {user.first_name},\n\nPlease verify your email by clicking the link below:\n{verify_url}\n\nIf you did not register, ignore this email."
    send_email(email, subject, body)

    return jsonify({'message': 'If the email exists, a verification link has been sent.'}), 200

# POST /api/auth/forgot-password
@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    if not email:
        return jsonify({'error': 'Missing email'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'If the email exists, a reset link has been sent.'}), 200
    reset_token = str(uuid.uuid4())
    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    user.password_reset_token = reset_token
    user.password_reset_expires = expires
    db.session.commit()
    reset_url = f"http://localhost:3000/reset-password/{reset_token}?email={email}"
    subject = "Password Reset Request"
    body = f"Hi {user.first_name},\n\nTo reset your password, click the link below:\n{reset_url}\n\nIf you did not request this, ignore this email."
    send_email(email, subject, body)
    return jsonify({'message': 'If the email exists, a reset link has been sent.'}), 200

# GET /api/auth/validate-reset-token
@bp.route('/validate-reset-token', methods=['GET'])
def validate_reset_token():
    token = request.args.get('token', '').strip()
    email = request.args.get('email', '').strip().lower()

    if not token or not email:
        return jsonify({'error': 'Missing token or email'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or user.password_reset_token != token:
        return jsonify({'error': 'Invalid token or email'}), 400

    if not user.password_reset_expires or user.password_reset_expires < datetime.datetime.utcnow():
        return jsonify({'error': 'Reset token expired'}), 400

    return jsonify({'message': 'Token is valid', 'email': email}), 200

# POST /api/auth/reset-password
@bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    token = data.get('token', '').strip()
    new_password = data.get('new_password', '')

    if not email or not token or not new_password:
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or user.password_reset_token != token:
        return jsonify({'error': 'Invalid token or email'}), 400

    if not user.password_reset_expires or user.password_reset_expires < datetime.datetime.utcnow():
        return jsonify({'error': 'Reset token expired'}), 400

    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.updated_at = datetime.datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Password reset successful.'}), 200

# GET /api/auth/me (protected)
@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone,
        'is_admin': user.is_admin,
        'email_verified': user.email_verified,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }
    return jsonify({'user': profile}), 200
