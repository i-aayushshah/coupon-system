from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Numeric, Text
from app import db
import json

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

    # Enhanced fields for product integration
    minimum_order_value = Column(Numeric(10, 2), default=0)
    applicable_categories = Column(Text)  # JSON string of categories
    maximum_discount_amount = Column(Numeric(10, 2))  # Cap for percentage discounts
    first_time_user_only = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship('User', back_populates='coupons')
    redemptions = relationship('Redemption', back_populates='coupon', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Coupon {self.code}>'

    def get_applicable_categories(self):
        """Get applicable categories as a list"""
        if self.applicable_categories:
            try:
                return json.loads(self.applicable_categories)
            except json.JSONDecodeError:
                return []
        return []

    def set_applicable_categories(self, categories):
        """Set applicable categories from a list"""
        if isinstance(categories, list):
            self.applicable_categories = json.dumps(categories)
        else:
            self.applicable_categories = None

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'description': self.description,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'is_public': self.is_public,
            'max_uses': self.max_uses,
            'current_uses': self.current_uses,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'minimum_order_value': float(self.minimum_order_value) if self.minimum_order_value else 0,
            'applicable_categories': self.get_applicable_categories(),
            'maximum_discount_amount': float(self.maximum_discount_amount) if self.maximum_discount_amount else None,
            'first_time_user_only': self.first_time_user_only,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
