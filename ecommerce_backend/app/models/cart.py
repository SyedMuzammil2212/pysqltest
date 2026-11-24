from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Cart(Base):

    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    index=True
)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart")