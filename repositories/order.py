from sqlalchemy.orm import Session
from models.order import Order, OrderItem
from models.bill import Bill

class OrderRepository:
    def get_all(self, db : Session, user_id : int):
        return db.query(Order).filter(Order.user_id == user_id).all()

    def get_by_it(self, db : Session, order_id : int, user_id : int):
        return db.query(Order).filter(Order.user_id == user_id, Order.id == order_id).first()

    def get_items(self, db : Session, order_id : int):
        return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    def create_item(self, db : Session, item_data : dict):
        item = OrderItem(**item_data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_item(self, db : Session, order : Order, status : str):
        order.status = status
        db.commit()
        db.refresh(order)
        return order

    def get_bill(self, db : Session, order_id : int, user_id :  int):
        return db.query(Bill).filter(Bill.order_id == order_id, Bill.user_id == user_id).first()

    def get_all_bills(self, db : Session, user_id : int):
        return db.query(Bill).filter(Bill.user_id == user_id).all()

order_repo = OrderRepository()
    