from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class OrderCreate(BaseModel):
    address_id: int


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name_snapshot: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    id: int
    user_id: int
    shipping_address_snapshot: str
    status: Literal["pending", "cancelled"]
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]