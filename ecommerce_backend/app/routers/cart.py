from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cart import Cart
from app.models.car_item import CartItem
from app.models.product import Product
from app.models.user import User

from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse
)

from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/v1/cart",
    tags=["Cart"]
)


# HELPER: GET OR CREATE USER CART
def get_or_create_cart(db: Session, user_id: int):

    cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


# HELPER: BUILD CART RESPONSE
def build_cart_response(cart: Cart):

    items = []
    total = Decimal("0.00")

    for item in cart.items:

        subtotal = item.product.price * item.quantity
        total += subtotal

        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "product": item.product,
            "subtotal": subtotal
        })

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": items,
        "total": total
    }


# 1. VIEW CART
@router.get("", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart = get_or_create_cart(db, current_user.id)

    return build_cart_response(cart)


# 2. ADD PRODUCT TO CART
@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED
)
def add_cart_item(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Check whether product exists and is active
    product = db.query(Product).filter(
        Product.id == item_data.product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Active product not found"
        )

    cart = get_or_create_cart(db, current_user.id)

    # Check whether product already exists in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product.id
    ).first()

    if existing_item:

        new_quantity = existing_item.quantity + item_data.quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Requested quantity exceeds available stock"
            )

        existing_item.quantity = new_quantity

    else:

        if item_data.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Requested quantity exceeds available stock"
            )

        new_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=item_data.quantity
        )

        db.add(new_item)

    db.commit()

    return {"message": "Product added to cart successfully"}


# 3. UPDATE CART ITEM QUANTITY
@router.patch("/items/{item_id}")
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Find item belonging to current user's cart
    cart_item = db.query(CartItem).join(Cart).filter(
        CartItem.id == item_id,
        Cart.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    if not cart_item.product.is_active:
        raise HTTPException(
            status_code=400,
            detail="This product is no longer available"
        )

    if item_data.quantity > cart_item.product.stock:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity exceeds available stock"
        )

    cart_item.quantity = item_data.quantity

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Cart item quantity updated successfully",
        "quantity": cart_item.quantity
    }


# 4. REMOVE ONE ITEM FROM CART
@router.delete("/items/{item_id}")
def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart_item = db.query(CartItem).join(Cart).filter(
        CartItem.id == item_id,
        Cart.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return {"message": "Cart item removed successfully"}


# 5. CLEAR ENTIRE CART
@router.delete("")
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:
        return {"message": "Cart is already empty"}

    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete(synchronize_session=False)

    db.commit()

    return {"message": "Cart cleared successfully"}