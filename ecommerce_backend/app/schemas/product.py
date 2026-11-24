from pydantic import BaseModel, Field

from decimal import Decimal
class ProductCreate(BaseModel):
    category_id: int
    sku: str
    name: str
    description: str | None = None
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    is_active: bool = True

class ProductUpdate(BaseModel):
    category_id: int | None = None
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

class ProductStockUpdate(BaseModel):
    stock: int = Field(ge=0)
    
class ProductResponse(BaseModel):
    id: int
    category_id: int
    sku: str
    name: str
    description: str | None = None
    price: float
    stock: int
    is_active: bool

    model_config = {
        "from_attributes": True
    }