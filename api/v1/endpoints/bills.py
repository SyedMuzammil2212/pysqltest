from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from cores.dependencies import get_current_user
from models.user import User
from services.bill import bill_service

router = APIRouter()

@router.get("/")
def get_bills(db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return bill_service.get_bills(db, user.id)

@router.get("/{order_id}")
def get_bill(order_id : int, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return bill_service.get_bill(db, user.id, order_id)