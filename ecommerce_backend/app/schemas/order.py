
from decimal import Decimal
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# REQUEST: PLACE ORDER
class OrderCreate(BaseModel):
    address_id: int = Field(gt=0)


# RESPONSE: ORDER ITEM
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name_snapshot: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


# RESPONSE: ORDER
class OrderResponse(BaseModel):
    id: int
    user_id: int
    shipping_address_snapshot: dict
    status: Literal["pending", "cancelled"]
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}
