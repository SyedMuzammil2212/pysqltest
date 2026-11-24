from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from main.database import get_db
from main.dependencies import get_current_user
from main.models import User
from main.schemas.user import UserUpdate, PasswordChange, UserResponse
from main.utils.security import hash_password, verify_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updates = user_data.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Name cannot be null"
        )

    for field, value in updates.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.patch("/me/password")
def change_my_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(
        password_data.current_password,
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    current_user.password_hash = hash_password(
        password_data.new_password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }
