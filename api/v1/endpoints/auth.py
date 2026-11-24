from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.auth import UserLogin, UserRegister
from schemas.user import UserResponse, UserCreate
from services.auth import auth_service

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_data : UserRegister, db : Session = Depends(get_db)):
    return auth_service.register(db, user_data)

@router.post("/login")
def login(user_data : UserLogin, db : Session = Depends(get_db)):
    return auth_service.login(db, user_data)