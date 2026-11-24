
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.adderess import Address

from app.models.user import User

from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse
)

from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/v1/address",
    tags=["Address"]
)


# 1. CREATE ADDRESS
@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(

    address_data: AddressCreate,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    new_address = Address(
        user_id=current_user.id,
        address_line_1=address_data.address_line_1,
        address_line_2=address_data.address_line_2,
        city=address_data.city,
        state=address_data.state,
        postal_code=address_data.postal_code
    )

    db.add(new_address)

    db.commit()

    db.refresh(new_address)

    return new_address


# 2. VIEW ALL USER ADDRESSES
@router.get("/", response_model=list[AddressResponse])
def get_addresses(

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    addresses = db.query(Address).filter(
        Address.user_id == current_user.id
    ).all()

    return addresses


# 3. VIEW SINGLE ADDRESS
@router.get("/{address_id}", response_model=AddressResponse)
def get_address(

    address_id: int,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not address:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    return address


# 4. UPDATE ADDRESS
@router.patch("/{address_id}", response_model=AddressResponse)
def update_address(

    address_id: int,

    address_data: AddressUpdate,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not address:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    update_data = address_data.model_dump(exclude_unset=True)

    if not update_data:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    for field, value in update_data.items():

        setattr(address, field, value)

    db.commit()

    db.refresh(address)

    return address


# 5. DELETE ADDRESS
@router.delete("/{address_id}")
def delete_address(

    address_id: int,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not address:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    db.delete(address)

    db.commit()

    return {
        "message": "Address deleted successfully"
    }
