from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from main.database import get_db
from main.dependencies import get_current_user
from main.models import Address, User
from main.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse
)

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED
)
def create_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_address = Address(
        user_id=current_user.id,
        **address_data.model_dump()
    )

    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return new_address


@router.get("", response_model=list[AddressResponse])
def get_my_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    addresses = db.query(Address).filter(
        Address.user_id == current_user.id
    ).order_by(Address.id).all()

    return addresses


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    return address


@router.patch("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    updates = address_data.model_dump(exclude_unset=True)

    required_fields = [
        "address_line_1",
        "city",
        "state",
        "postal_code"
    ]

    for field in required_fields:
        if field in updates and updates[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null"
            )

    for field, value in updates.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)

    return address


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    db.delete(address)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
