from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime


class BillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    order_id: int
    bill_number: str
    subtotal: Decimal
    delivery_fee: Decimal
    final_total: Decimal
    created_at: datetime