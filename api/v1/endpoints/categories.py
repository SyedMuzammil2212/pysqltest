from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.user import User
from schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from db.session import get_db
from cores.dependencies import get_current_user
from services.category import category_service

router = APIRouter()

@router.post("/", response_model=CategoryResponse)
def create_category(data : CategoryCreate, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return category_service.create(db, data)

@router.get("/", response_model=list[CategoryResponse])
def get_categories(db : Session = Depends(get_db)):
    return category_service.get_all(db)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id : int, db : Session = Depends(get_db)):
    return category_service.get_by_id(db, category_id)

@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(category_id : int, data : CategoryUpdate, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return category_service.update(db, category_id, data)

@router.delete("/{category_id}")
def delete_category(category_id : int, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    category_service.delete(db, category_id)
    return {"message" : "Category Deleted"}