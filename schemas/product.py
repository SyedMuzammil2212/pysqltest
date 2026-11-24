from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class ProductCreate(BaseModel):
    category_id: int
    sku: str
    name: str
    description: str | None = None
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)


class ProductUpdate(BaseModel):
    category_id: int | None = None
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)


class ProductStockUpdate(BaseModel):
    stock: int = Field(ge=0)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    sku: str
    name: str
    description: str | None
    price: Decimal
    stock: int
    is_active: bool


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int