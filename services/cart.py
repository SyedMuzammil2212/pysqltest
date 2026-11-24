
from sqlalchemy.orm import Session
from fastapi import HTTPException

from repositories.cart import CartRepository
from repositories.product import ProductRepository


class CartService:

    def __init__(self):
        self.cart_repo = CartRepository()
        self.product_repo = ProductRepository()

    def get_cart(self, db: Session, user_id: int):
        cart = self.cart_repo.get_all(db, user_id)
        if not cart:
            cart = self.cart_repo.create_cart(db, user_id)

        total = sum(item.product.price * item.quantity for item in cart.items)

        return {
            "id": cart.id,
            "items": cart.items,
            "total": total
        }

    def add_item(self, db: Session, user_id: int, product_id: int, quantity: int):
        product = self.product_repo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")

        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive.")

        cart = self.cart_repo.get_all(db, user_id)
        if not cart:
            cart = self.cart_repo.create_cart(db, user_id)

        item = self.cart_repo.get_item_by_product(db, cart.id, product_id)
        current_quantity = item.quantity if item else 0
        if current_quantity + quantity > product.stock:
            raise HTTPException(status_code=400, detail="Insufficient stock.")

        return self.cart_repo.add_item(db, cart.id, product_id, quantity)

    def update_item(self, db: Session, user_id: int, item_id: int, quantity: int):
        cart = self.cart_repo.get_all(db, user_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found.")

        item = self.cart_repo.get_item(db, cart.id, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Cart item not found.")

        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive.")

        if quantity > item.product.stock:
            raise HTTPException(status_code=400, detail="Insufficient stock.")

        return self.cart_repo.update_item(db, item, quantity)

    def remove_item(self, db: Session, user_id: int, item_id: int):
        cart = self.cart_repo.get_all(db, user_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found.")
        
        item = self.cart_repo.get_item(db, cart.id, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Cart item not found.")

        return self.cart_repo.remove_item(db, item)

    def clear_cart(self, db: Session, user_id: int):
        cart = self.cart_repo.get_all(db, user_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found.")

        return self.cart_repo.clear_cart(db, cart)


cart_service = CartService()
