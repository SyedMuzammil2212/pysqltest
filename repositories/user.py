from sqlalchemy.orm import Session
from schemas.user import UserUpdate
from schemas.auth import UserRegister
from models.user import User
from fastapi import HTTPException

class UserRepository:

    def get_all(self, db: Session):
        return db.query(User).all()

    def get_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, user_data: UserRegister, password_hash : str):
        user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=password_hash
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user: User, data: UserUpdate):
        updated_data = data.model_dump(exclude_unset=True)

        for key, val in updated_data.items():
            setattr(user, key, val)

        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, user: User):
        db.delete(user)
        db.commit()
        return True

    def update_password(self, db : Session, user : User, password_hash : str):
        user.password_hash = password_hash
        db.commit()
        db.refresh(user)
        return user

user_repo = UserRepository()