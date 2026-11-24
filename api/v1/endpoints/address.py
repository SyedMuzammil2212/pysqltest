from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from cores.dependencies import get_current_user
from models.user import User
from schemas.address import AddressCreate, AddressResponse, AddressUpdate
from services.address import address_service

router = APIRouter()

@router.post("/", response_model=AddressResponse)
def create_address(data : AddressCreate, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return address_service.create(db, user.id, data)

@router.get("/", response_model=list[AddressResponse])
def get_addresses(db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return address_service.get_all(db, user.id)

@router.get("/", response_model=AddressResponse)
def get_address(address_id : int, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return address_service.get_all(db, address_id, user.id)

@router.patch("/{address_id}", response_model=AddressResponse)
def update_address(address_id : int, data : AddressUpdate, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    return address_service.update(db, address_id, user.id, data)

@router.delete("/{address_id}")
def delete_address(address_id : int, db : Session = Depends(get_db), user : User = Depends(get_current_user)):
    address_service.delete(db, address_id, user.id)
    return {"message" : "Address Deleted."}