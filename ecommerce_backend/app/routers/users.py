
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User

from app.schemas.user import (
    UserResponse,
    UserUpdate,
    PasswordChange
)

from app.utils.dependencies import get_current_user

from app.utils.security import hash_password, verify_password


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)


# 1. GET USER PROFILE
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):

    return current_user


# 2. UPDATE USER PROFILE
@router.patch("/me", response_model=UserResponse)
def update_my_profile(

    user_data: UserUpdate,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    if "name" in update_data and not update_data["name"].strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )

    for field, value in update_data.items():

        setattr(current_user, field, value)

    db.commit()

    db.refresh(current_user)

    return current_user


# 3. CHANGE USER PASSWORD
@router.patch("/me/password")
def change_password(

    password_data: PasswordChange,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    # Verify current password
    password_valid = verify_password(
        password_data.current_password,
        current_user.password_hash
    )

    if not password_valid:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Check whether new password is same as current password
    if password_data.current_password == password_data.new_password:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Hash new password
    new_hashed_password = hash_password(
        password_data.new_password
    )

    # Update database
    current_user.password_hash = new_hashed_password

    db.commit()

    return {
        "message": "Password changed successfully"
    }
