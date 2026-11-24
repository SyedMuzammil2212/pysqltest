from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime


class OrderCreate(BaseModel):
    address_id: int


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    shipping_address_snapshot: str
    status: str
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int