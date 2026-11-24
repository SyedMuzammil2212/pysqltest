from sqlalchemy.orm import Session
from models.cart import Cart, CartItem

class CartRepository:
    def get_all(self, db : Session, user_id : int):
        return db.query(Cart).filter(Cart.user_id == user_id).first()

    def create_cart(self, db : Session, user_id : int):
        cart = Cart(user_id = user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    def get_item(self, db : Session, cart_id : int, item_id : int):
        return db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart_id).first()

    def get_item_by_product(self, db : Session, cart_id : int, product_id : int):
        return db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id).first()

    def add_item(self, db : Session, cart_id : int, product_id : int, quantity : int):
        item = self.get_item_by_product(db, cart_id, product_id)
        if item:
            item.quantity += quantity
        else:
            item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
            db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_item(self, db : Session, item : CartItem, quantity : int):
        item.quantity = quantity
        db.commit()
        db.refresh(item)
        return item

    def remove_item(self, db : Session, item : CartItem):
        db.delete(item)
        db.commit()
        return True

    def clear_cart(self, db : Session, cart : Cart):
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
        return True

cart_repo = CartRepository()