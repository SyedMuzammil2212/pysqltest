from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.address import Address
from schemas.address import AddressCreate, AddressUpdate

class AddressRepository:
    def get_all(self, db : Session, user_id : int):
        return db.query(Address).filter(Address.user_id == user_id).all()

    def get_by_id(self, db : Session, user_id : int, address_id : int):
        return db.query(Address).filter(Address.user_id == user_id, Address.id == address_id).first()

    def create(self, db : Session, address_data : AddressCreate, user_id : int):
        address = Address(**address_data.model_dump(), user_id = user_id)

        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    def update(self, db : Session, address : Address, data : AddressUpdate):
        updated_data = data.model_dump(exclude_unset=True)
        for key, val in updated_data.items():
            setattr(address, key, val)

        db.commit()
        db.refresh(address)
        return address

    def delete(self, db : Session, address : Address):
        db.delete(address)
        db.commit()
        return True

address_repo = AddressRepository()