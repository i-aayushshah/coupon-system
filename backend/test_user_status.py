from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='aayushshah817@gmail.com').first()
    if user:
        print(f"User found: {user.username}")
        print(f"Email verified: {user.email_verified}")
        print(f"Verification token: {user.email_verification_token}")
        print(f"Token expires: {user.email_verification_expires}")
    else:
        print("User not found")
