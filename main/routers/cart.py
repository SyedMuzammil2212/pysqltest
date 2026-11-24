from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from main.database import get_db
from main.dependencies import get_current_user
from main.models import Cart, CartItem, Product, User
from main.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    CartResponse
)

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


def get_user_cart(db: Session, user_id: int, lock: bool = False):
    query = db.query(Cart).filter(Cart.user_id == user_id)

    if lock:
        query = query.with_for_update()

    cart = query.first()

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    return cart


def get_cart_item(
    db: Session,
    cart_id: int,
    item_id: int
):
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart_id
    ).first()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    return item


@router.get("", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_user_cart(db, current_user.id)

    cart_items = db.query(CartItem, Product).join(
        Product,
        CartItem.product_id == Product.id
    ).filter(
        CartItem.cart_id == cart.id
    ).all()

    items = []
    total = Decimal("0.00")

    for cart_item, product in cart_items:
        subtotal = product.price * cart_item.quantity
        total += subtotal

        items.append(
            CartItemResponse(
                id=cart_item.id,
                product_id=product.id,
                product_name=product.name,
                sku=product.sku,
                unit_price=product.price,
                quantity=cart_item.quantity,
                subtotal=subtotal
            )
        )

    return CartResponse(
        id=cart.id,
        items=items,
        total=total
    )


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK
)
def add_cart_item(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_user_cart(db, current_user.id, lock=True)

    product = db.query(Product).filter(
        Product.id == item_data.product_id
    ).first()

    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active product not found"
        )

    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product.id
    ).first()

    new_quantity = item_data.quantity

    if existing_item:
        new_quantity += existing_item.quantity

    if new_quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient product stock"
        )

    if existing_item:
        existing_item.quantity = new_quantity
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=new_quantity
        )
        db.add(new_item)

    db.commit()

    return get_cart(db, current_user)


@router.patch(
    "/items/{item_id}",
    response_model=CartResponse
)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_user_cart(db, current_user.id, lock=True)

    item = get_cart_item(db, cart.id, item_id)

    product = db.query(Product).filter(
        Product.id == item.product_id
    ).first()

    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active product not found"
        )

    if item_data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient product stock"
        )

    item.quantity = item_data.quantity

    db.commit()

    return get_cart(db, current_user)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_user_cart(db, current_user.id, lock=True)

    item = get_cart_item(db, cart.id, item_id)

    db.delete(item)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT
)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_user_cart(db, current_user.id, lock=True)

    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
