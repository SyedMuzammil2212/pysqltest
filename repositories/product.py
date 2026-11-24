from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate

class ProductRepository:
    def get_all(self, db : Session):
        return db.query(Product).filter(Product.is_active == True).all()

    def get_by_id(self, db : Session, p_id : int):
        return db.query(Product).filter(Product.id == p_id, Product.is_active == True).first()

    def create(self, db : Session, product_data : ProductCreate):
        product = Product(**product_data.model_dump())
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def update(self, db : Session, product : Product, data : ProductUpdate):
        updated_data = data.model_dump(exclude_unset=True)

        for key, val in updated_data.items():
            setattr(product, key, val)

        db.commit()
        db.refresh(product)
        return product

    def update_stock(self, db : Session, product : Product, stock : int):
        product.stock = stock
        db.commit()
        db.refresh(product)
        return product

    def delete(self, db : Session, product : Product):
        product.is_active = False
        db.commit()
        db.refresh(product)
        return product

product_repo = ProductRepository()