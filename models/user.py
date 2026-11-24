
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(String(20), nullable=False, default="user")

    addresses = relationship("Address", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")
    bills = relationship("Bill", back_populates="user")
