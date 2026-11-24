from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate

class CategoryRepository:
    def get_all(self,  db : Session):
        return db.query(Category).all()

    def get_by_id(self, db : Session, c_id : int):
        return db.query(Category).filter(Category.id == c_id).first()

    def create(self, db : Session, category_data : CategoryCreate):
        existing_category = db.query(Category).filter(Category.name == category_data.name).first()
        if existing_category:
            raise HTTPException(status_code=409, detail="Category Already Exist")
        category = Category(**category_data.model_dump())

        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def update(self, db : Session, category : Category, data : CategoryUpdate):
        updated_data = data.model_dump(exclude_unset=True)
        for key, val in updated_data.items():
            setattr(category, key, val)

        db.commit()
        db.refresh(category)
        return category

    def delete(self, db : Session, category : Category):
        if category.products:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete category containing products"
            )

        db.delete(category)
        db.commit()
        return True


category_repo = CategoryRepository()