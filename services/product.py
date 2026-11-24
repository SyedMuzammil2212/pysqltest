from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories.product import ProductRepository
from repositories.category import CategoryRepository
from schemas.product import ProductUpdate, ProductCreate

class ProductService:

    def __init__(self):
        self.product_repo = ProductRepository()
        self.category_repo = CategoryRepository()

    def get_all(self, db: Session):
        return self.product_repo.get_all(db)

    def get_by_id(self, db: Session, p_id: int):
        product = self.product_repo.get_by_id(db, p_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")

        return product

    def create(self, db: Session, data: ProductCreate):
        category = self.category_repo.get_by_id(db, data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")

        return self.product_repo.create(db, data)

    def update(self, db: Session, p_id: int, data: ProductUpdate):
        product = self.get_by_id(db, p_id)
        if data.category_id is not None:
            category = self.category_repo.get_by_id(db, data.category_id)
            if not category:
                raise HTTPException(status_code=404, detail="Category not found.")

        return self.product_repo.update(db, product, data)

    def update_stock(self, db: Session, p_id: int, stock: int):
        product = self.get_by_id(db, p_id)
        if stock < 0:
            raise HTTPException(status_code=400, detail="Stock cannot be negative.")

        return self.product_repo.update_stock(db, product, stock)

    def delete(self, db: Session, p_id: int):
        product = self.get_by_id(db, p_id)
        return self.product_repo.delete(db, product)

    def get_by_category(self, db: Session, category_id: int):
        category = self.category_repo.get_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")

        return [
            product for product in self.product_repo.get_all(db)
            if product.category_id == category_id
        ]


product_service = ProductService()