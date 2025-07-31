import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///coupon.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret')

    # Gmail SMTP settings for testing
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'aayushshah983@gmail.com'
    MAIL_PASSWORD = 'odvmbcxytuzujrwl'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
