
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime,
    ForeignKey, ForeignKeyConstraint, UniqueConstraint, func
)
from sqlalchemy.orm import relationship

from db.session import Base


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    order_id = Column(Integer, nullable=False, unique=True)
    bill_number = Column(String(50), unique=True, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    delivery_fee = Column(Numeric(10, 2), nullable=False)
    final_total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(
            ["order_id", "user_id"],
            ["orders.id", "orders.user_id"],
            ondelete="RESTRICT"
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="RESTRICT"
        ),
    )

    user = relationship("User", back_populates="bills")
    order = relationship("Order", back_populates="bill")
