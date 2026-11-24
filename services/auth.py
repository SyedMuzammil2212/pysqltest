from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories.user import UserRepository
from schemas.auth import UserRegister, UserLogin
from schemas.user import UserCreate
from cores.security import hash_password, verify_password, create_access_token

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register(self, db : Session, user_data : UserRegister):
        existing_user = self.user_repo.get_by_email(db, user_data.email)

        if existing_user:
            raise HTTPException(status_code=409, detail="User Already Exist")

        password_hash = hash_password(user_data.password)

        return self.user_repo.create(db, user_data, password_hash)

    def login(self, db : Session, user_data : UserLogin):
        user = self.user_repo.get_by_email(db, user_data.email)

        if not user or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token(user.id)
        return {
            "access_token" : token,
            "token_type" : "bearer"
        }

auth_service = AuthService()