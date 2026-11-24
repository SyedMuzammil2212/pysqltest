from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from cores.dependencies import get_current_user
from models.user import User
from schemas.cart import CartItemCreate, CartItemUpdate
from services.cart import cart_service

router = APIRouter()

@router.get("/")
def get_cart(db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return cart_service.get_cart(db, user.id)

@router.post("/items")
def add_cart(data : CartItemCreate, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return cart_service.add_item(db, user.id, data.product_id, data.quantity)

@router.patch("/items/{item_id}")
def update_cart(item_id : int, data : CartItemUpdate, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return cart_service.update_item(db, user.id, item_id, data.quantity)

@router.delete("/items/{item_id}")
def remove_item(item_id : int, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    cart_service.remove_item(db, user.id, item_id)
    return {"message" : "Cart item removed"}

@router.delete("/")
def delete_cart(db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    cart_service.clear_cart(db, user.id)
    return {"message" : "Cart cleared"}