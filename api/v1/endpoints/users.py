from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from cores.dependencies import get_current_user
from models.user import User
from schemas.user import UserResponse, UserUpdate, PasswordChange
from services.user import user_service

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_me(curr_user : User = Depends(get_current_user), db : Session = Depends(get_db)):
    return user_service.get_profile(db, curr_user.id)

@router.patch("/me", response_model=UserResponse)
def update_me(data : UserUpdate, curr_user : User = Depends(get_current_user), db : Session = Depends(get_db)):
    return user_service.update_profile(db, curr_user.id, data)

@router.patch("/me/password")
def update_pass(data : PasswordChange, curr_user : User = Depends(get_current_user), db : Session = Depends(get_db)):
    return user_service.change_passwrod(db, curr_user.id, data)