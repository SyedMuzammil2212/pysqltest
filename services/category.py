from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories.category import CategoryRepository
from schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self):
        self.category_repo = CategoryRepository()

    def get_all(self, db : Session):
        return self.category_repo.get_all(db)

    def get_by_id(self, db : Session, category_id : int):
        category = self.category_repo.get_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Couldn't find category")

        return category

    def create(self, db : Session, data : CategoryCreate):
        return self.category_repo.create(db, data)

    def update(self, db : Session, category_id : int, data : CategoryCreate):
        category = self.get_by_id(db, category_id)
        return self.category_repo.update(db, category, data)

    def delete(self, db : Session, category_id : int):
        category = self.get_by_id(db, category_id)
        return self.category_repo.delete(db, category)

category_service = CategoryService()