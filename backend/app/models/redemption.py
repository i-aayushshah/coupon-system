from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Numeric, Text
from app import db
import json

class Redemption(db.Model):
    __tablename__ = 'redemptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    coupon_id = Column(Integer, ForeignKey('coupons.id'), nullable=False)
    redeemed_at = Column(DateTime, default=datetime.utcnow)
    discount_applied = Column(Float, nullable=False)

    # Enhanced fields for order integration
    order_id = Column(Integer, ForeignKey('orders.id'))
    original_amount = Column(Numeric(10, 2))
    discount_amount = Column(Numeric(10, 2))
    final_amount = Column(Numeric(10, 2))
    products_applied_to = Column(Text)  # JSON string of product IDs

    user = relationship('User', back_populates='redemptions')
    coupon = relationship('Coupon', back_populates='redemptions')
    order = relationship('Order', backref='redemptions')

    def __repr__(self):
        return f'<Redemption user={self.user_id} coupon={self.coupon_id}>'

    def get_products_applied_to(self):
        """Get products applied to as a list"""
        if self.products_applied_to:
            try:
                return json.loads(self.products_applied_to)
            except json.JSONDecodeError:
                return []
        return []

    def set_products_applied_to(self, product_ids):
        """Set products applied to from a list"""
        if isinstance(product_ids, list):
            self.products_applied_to = json.dumps(product_ids)
        else:
            self.products_applied_to = None

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'coupon_id': self.coupon_id,
            'redeemed_at': self.redeemed_at.isoformat(),
            'discount_applied': self.discount_applied,
            'order_id': self.order_id,
            'original_amount': float(self.original_amount) if self.original_amount else None,
            'discount_amount': float(self.discount_amount) if self.discount_amount else None,
            'final_amount': float(self.final_amount) if self.final_amount else None,
            'products_applied_to': self.get_products_applied_to()
        }
