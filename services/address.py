
from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories.address import AddressRepository
from schemas.address import AddressCreate, AddressUpdate


class AddressService:

    def __init__(self):
        self.address_repo = AddressRepository()

    def get_all(self, db: Session, user_id: int):
        return self.address_repo.get_all(db, user_id)

    def get_by_id(self, db: Session, address_id: int, user_id: int):
        address = self.address_repo.get_by_id(db, address_id, user_id)
        if not address:
            raise HTTPException(status_code=404, detail="Address not found.")

        return address

    def create(self, db: Session, user_id: int, data: AddressCreate):
        return self.address_repo.create(db, data, user_id)

    def update(self, db: Session, address_id: int, user_id: int, data: AddressUpdate):
        address = self.get_by_id(db, address_id, user_id)
        return self.address_repo.update(db, address, data)

    def delete(self, db: Session, address_id: int, user_id: int):
        address = self.get_by_id(db, address_id, user_id)
        return self.address_repo.delete(db, address)


address_service = AddressService()
