
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.dependencies import get_current_user

from app.models.user import User
from app.models.order import Order
from app.models.bill import Bill

from app.schemas.bill import BillResponse


router = APIRouter(
    tags=["Bills"]
)


# GET BILL FOR A SPECIFIC ORDER
@router.get(
    "/api/v1/orders/{order_id}/bill",
    response_model=BillResponse
)
def get_order_bill(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check whether the order belongs to the logged-in user
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Find the bill belonging to this order and user
    bill = db.query(Bill).filter(
        Bill.order_id == order.id,
        Bill.user_id == current_user.id
    ).first()

    if bill is None:
        raise HTTPException(
            status_code=404,
            detail="Bill not found for this order"
        )

    return bill


# GET ALL BILLS OF THE LOGGED-IN USER
@router.get(
    "/api/v1/bills",
    response_model=list[BillResponse]
)
def get_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bills = db.query(Bill).filter(
        Bill.user_id == current_user.id
    ).order_by(
        Bill.created_at.desc()
    ).all()

    return bills
