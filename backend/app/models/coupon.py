from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from app import db

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = Column(Integer, primary_key=True)
    code = Column(String(32), unique=True, nullable=False)
    title = Column(String(120), nullable=False)
    description = Column(String(255))
    discount_type = Column(String(16), nullable=False)  # 'percentage' or 'fixed'
    discount_value = Column(Float, nullable=False)
    is_public = Column(Boolean, default=True)
    max_uses = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship('User', back_populates='coupons')
    redemptions = relationship('Redemption', back_populates='coupon', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Coupon {self.code}>'
