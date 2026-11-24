from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories.bill import bill_repo

class BillService:
    def get_bills(self, db : Session, user_id : int):
        return bill_repo.get_all(db, user_id)

    def get_bill(self, db : Session, user_id : int, order_id : int):
        bill = bill_repo.get_by_order(db, user_id, order_id)
        if not bill:
            raise HTTPException(status_code=404, detail="Bill doesnt exist")

        return bill

bill_service = BillService()