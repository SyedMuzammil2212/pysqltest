from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    total: Decimal