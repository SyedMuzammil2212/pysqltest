from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from cores.dependencies import get_admin_user
from models.user import User
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from services.product import product_service

router = APIRouter()

@router.post("/", response_model=ProductResponse)
def create_product(data : ProductCreate, db : Session = Depends(get_db), user : User = Depends(get_admin_user)):
    return product_service.create(db, data)

@router.get("/", response_model=list[ProductResponse])
def get_products(db : Session = Depends(get_db)):
    return product_service.get_all(db)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id : int, db : Session = Depends(get_db)):
    return product_service.get_by_id(db, product_id)

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id : int, data : ProductUpdate, db : Session = Depends(get_db), user : User = Depends(get_admin_user)):
    return product_service.update(db, product_id, data)

@router.patch("/{product_id}/stock", response_model=ProductResponse)
def update_stock(product_id : int, stock : int, db : Session = Depends(get_db), user : User = Depends(get_admin_user)):
    return product_service.update_stock(db, product_id, stock)

@router.delete("/{product_id}")
def delete_product(product_id : int, db : Session = Depends(get_db), user : User = Depends(get_admin_user)):
    product_service.delete(db, product_id)
    return {"message" : "Product Deleted"}