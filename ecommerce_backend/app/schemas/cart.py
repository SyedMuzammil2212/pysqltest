from pydantic import BaseModel, Field
from decimal import Decimal
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    price: Decimal
    stock: int
    is_active: bool

    model_config = {"from_attributes": True}


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: CartProductResponse
    subtotal: Decimal


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse]
    total: Decimal