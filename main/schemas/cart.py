from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    sku: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    total: Decimal