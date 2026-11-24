from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock : Mapped[int] = mapped_column(
    Integer,
    nullable=False,
    default=0
           )
    is_active: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=True
)
    # Relationships
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")