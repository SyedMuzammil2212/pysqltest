from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BillResponse(BaseModel):
    id: int
    user_id: int
    order_id: int
    bill_number: str
    subtotal: Decimal
    delivery_fee: Decimal
    final_total: Decimal
    created_at: datetime