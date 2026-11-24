
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.dependencies import get_current_user
from app.config import settings

from app.models.user import User
from app.models.adderess import Address
from app.models.cart import Cart
from app.models.car_item import CartItem
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.bill import Bill

from app.utils.mail import send_order_confirmation_email

from app.schemas.order import OrderCreate, OrderResponse


router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"]
)


# 1. PLACE ORDER
@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def place_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:

        # STEP 1: CHECK SAVED ADDRESS OWNERSHIP

        address = db.query(Address).filter(
            Address.id == order_data.address_id,
            Address.user_id == current_user.id
        ).first()

        if address is None:
            raise HTTPException(
                status_code=404,
                detail="Address not found"
            )


        # STEP 2: GET USER CART

        cart = db.query(Cart).filter(
            Cart.user_id == current_user.id
        ).first()

        if cart is None:
            raise HTTPException(
                status_code=400,
                detail="Cart is empty"
            )


        # STEP 3: GET CART ITEMS

        cart_items = db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).all()

        if not cart_items:
            raise HTTPException(
                status_code=400,
                detail="Cannot place an order with an empty cart"
            )


        # STEP 4: LOCK PRODUCT ROWS

        product_ids = sorted({
            item.product_id for item in cart_items
        })

        products = db.query(Product).filter(
            Product.id.in_(product_ids)
        ).order_by(
            Product.id
        ).with_for_update().all()

        product_map = {
            product.id: product for product in products
        }


        # STEP 5: VALIDATE PRODUCT AVAILABILITY AND STOCK

        for item in cart_items:

            product = product_map.get(item.product_id)

            if product is None or not product.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="One or more products are unavailable"
                )

            if item.quantity > product.stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product.name}"
                )


        # STEP 6: CALCULATE SUBTOTAL USING DATABASE PRICES

        subtotal = Decimal("0.00")

        for item in cart_items:

            product = product_map[item.product_id]

            subtotal += product.price * item.quantity


        delivery_fee = settings.DELIVERY_FEE

        final_total = subtotal + delivery_fee


        # STEP 7: CREATE SHIPPING ADDRESS SNAPSHOT

        address_snapshot = {
            "address_line_1": address.address_line_1,
            "address_line_2": address.address_line_2,
            "city": address.city,
            "state": address.state,
            "postal_code": address.postal_code
        }


        # STEP 8: PREPARE EMAIL ITEMS

        email_items = []

        for item in cart_items:

            product = product_map[item.product_id]

            email_items.append({
                "name": product.name,
                "quantity": item.quantity,
                "unit_price": str(product.price),
                "subtotal": str(product.price * item.quantity)
            })


        # STEP 9: CREATE ORDER

        new_order = Order(
            user_id=current_user.id,
            shipping_address_snapshot=address_snapshot,
            status="pending",
            total=final_total
        )

        db.add(new_order)

        # Generate order ID before creating order items
        db.flush()


        # STEP 10: CREATE ORDER ITEMS AND REDUCE STOCK

        for item in cart_items:

            product = product_map[item.product_id]

            item_subtotal = product.price * item.quantity

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name_snapshot=product.name,
                quantity=item.quantity,
                unit_price=product.price,
                subtotal=item_subtotal
            )

            db.add(order_item)

            # Reduce available stock
            product.stock -= item.quantity


        # STEP 11: CREATE BILL RECORD

        new_bill = Bill(
            user_id=new_order.user_id,
            order_id=new_order.id,
            bill_number=f"BILL-{uuid4().hex[:12].upper()}",
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            final_total=final_total
        )

        db.add(new_bill)


        # STEP 12: CLEAR CART

        db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).delete(synchronize_session=False)


        # STEP 13: COMMIT EVERYTHING TOGETHER

        db.commit()

        db.refresh(new_order)


        # STEP 14: SEND ORDER CONFIRMATION EMAIL IN BACKGROUND

        background_tasks.add_task(
            send_order_confirmation_email,
            recipient=current_user.email,
            order_number=str(new_order.id),
            items=email_items,
            total=str(final_total),
            shipping_address=address_snapshot
        )

        return new_order


    except Exception:
        db.rollback()
        raise


# 2. LIST USER ORDERS
@router.get("", response_model=list[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return orders


# 3. VIEW SINGLE ORDER
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


# 4. CANCEL PENDING ORDER
@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:

        # STEP 1: FIND AND LOCK THE USER'S ORDER

        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        ).with_for_update().first()

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )


        # STEP 2: CHECK ORDER STATUS

        if order.status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Only pending orders can be cancelled"
            )


        # STEP 3: GET ORDER ITEMS

        order_items = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()


        # STEP 4: LOCK THE RELATED PRODUCT ROWS

        product_ids = sorted({
            item.product_id for item in order_items
        })

        products = db.query(Product).filter(
            Product.id.in_(product_ids)
        ).order_by(
            Product.id
        ).with_for_update().all()

        product_map = {
            product.id: product for product in products
        }


        # STEP 5: RESTORE PRODUCT STOCK

        for item in order_items:

            product = product_map.get(item.product_id)

            if product is None:
                raise HTTPException(
                    status_code=409,
                    detail="A product associated with this order no longer exists"
                )

            product.stock += item.quantity


        # STEP 6: UPDATE ORDER STATUS

        order.status = "cancelled"


        # STEP 7: COMMIT BOTH CHANGES TOGETHER

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise
