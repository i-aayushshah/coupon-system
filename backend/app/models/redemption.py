from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from app import db

class Redemption(db.Model):
    __tablename__ = 'redemptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    coupon_id = Column(Integer, ForeignKey('coupons.id'), nullable=False)
    redeemed_at = Column(DateTime, default=datetime.utcnow)
    discount_applied = Column(Float, nullable=False)

    user = relationship('User', back_populates='redemptions')
    coupon = relationship('Coupon', back_populates='redemptions')

    def __repr__(self):
        return f'<Redemption user={self.user_id} coupon={self.coupon_id}>'
