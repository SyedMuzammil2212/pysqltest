from sqlalchemy.orm import Session
from fastapi import HTTPException
from schemas.user import UserUpdate, PasswordChange
from repositories.user import UserRepository
from cores.security import hash_password, verify_password

class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def get_profile(self, db : Session, user_id : int):
        user = self.user_repo.get_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_profile(self, db : Session, user_id : int, data : UserUpdate):
        user = self.user_repo.get_by_id(db, user_id)

        return self.user_repo.update(db, user, data)

    def change_passwrod(self, db : Session, user_id : int, data : PasswordChange):
        user = self.user_repo.get_by_id(db, user_id)
        
        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Incorrect current password")
        
        new_password_hash = hash_password(data.new_password)
        return self.user_repo.update_password(db, user, new_password_hash)

user_service = UserService()