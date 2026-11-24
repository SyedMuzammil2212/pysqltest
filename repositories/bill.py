from sqlalchemy.orm import Session
from models.bill import Bill

class BillRepository:
    def get_all(self, db : Session, user_id : int):
        return db.query(Bill).filter(Bill.user_id == user_id).all()

    def get_by_order(self, db : Session, user_id : int, order_id : int):
        return db.query(Bill).filter(Bill.user_id == user_id, Bill.order_id == order_id).first()

bill_repo = BillRepository()