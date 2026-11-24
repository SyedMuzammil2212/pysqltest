from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from db.session import get_db
from cores.dependencies import get_current_user
from models.user import User
from services.order import order_service
from services.email import send_order_email

router = APIRouter()

@router.post("/checkout")
def checkout(address_id : int, background_task : BackgroundTasks, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    order = order_service.checkout(db, user.id, address_id)
    background_task.add_task(
        send_order_email,
        user.email,
        order.id,
        order.total
    )
    return order

@router.get("/")
def get_orders(db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return order_service.get_orders(db, user.id)

@router.get("/{order_id}")
def get_order(order_id : int, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return order_service.get_order(db, user.id, order_id)

@router.post("/{order_id}/cancel")
def cancel_order(order_id : int, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return order_service.cancel_order(db, user.id, order_id)