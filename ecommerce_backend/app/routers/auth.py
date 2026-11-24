from fastapi import APIRouter, Depends, HTTPException, status

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User

from app.schemas.user import UserCreate, UserResponse

from app.utils.security import hash_password, verify_password 

from app.utils.token import create_access_token


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


# REGISTER USER
@router.post("/register", response_model=UserResponse)
def register_user(

    user: UserCreate,

    db: Session = Depends(get_db)

):

    # Check whether email already exists
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


# LOGIN USER
@router.post("/login")
def login_user(

    form_data: OAuth2PasswordRequestForm = Depends(),

    db: Session = Depends(get_db)

):

    # Find user using email
    existing_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not existing_user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify password
    password_valid = verify_password(
        form_data.password,
        existing_user.password_hash
    )

    if not password_valid:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create access token
    access_token = create_access_token({

        "sub": str(existing_user.id)

    })

    return {

        "access_token": access_token,

        "token_type": "bearer"

    }