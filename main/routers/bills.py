from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from main.database import get_db
from main.dependencies import get_current_user
from main.models import Bill, User
from main.schemas.bill import BillResponse


router = APIRouter(
    prefix="/bills",
    tags=["Bills"]
)

order_bills_router = APIRouter(
    prefix="/orders",
    tags=["Bills"]
)


@order_bills_router.get(
    "/{order_id}/bill",
    response_model=BillResponse
)
def get_order_bill(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bill = db.query(Bill).filter(
        Bill.order_id == order_id,
        Bill.user_id == current_user.id
    ).first()

    if bill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )

    return bill


@router.get(
    "",
    response_model=list[BillResponse]
)
def get_my_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bills = db.query(Bill).filter(
        Bill.user_id == current_user.id
    ).order_by(
        Bill.created_at.desc()
    ).all()

    return bills