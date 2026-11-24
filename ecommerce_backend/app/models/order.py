from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Order(Base):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shipping_address_snapshot = Column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(
    String(20),
    nullable=False,
    default="pending"
    )
    total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    bill = relationship("Bill", back_populates="order", uselist=False)