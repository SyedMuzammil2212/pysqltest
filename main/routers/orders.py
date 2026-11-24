import os
import uuid
from decimal import Decimal

from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks
)
from sqlalchemy.orm import Session

from main.database import get_db
from main.dependencies import get_current_user
from main.models import (
    User,
    Address,
    Cart,
    CartItem,
    Product,
    Order,
    OrderItem,
    Bill
)
from main.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderItemResponse
)
from main.utils.email import send_order_confirmation

load_dotenv()

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

DELIVERY_FEE = Decimal(os.getenv("DELIVERY_FEE", "50.00"))


def format_address(address: Address) -> str:
    parts = [
        address.address_line_1,
        address.address_line_2,
        address.city,
        address.state,
        address.postal_code
    ]

    return ", ".join(part for part in parts if part)


def build_order_response(order: Order, items: list[OrderItem]):
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        shipping_address_snapshot=order.shipping_address_snapshot,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name_snapshot=item.product_name_snapshot,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal
            )
            for item in items
        ]
    )


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
        # Verify that the address belongs to the logged-in user.
        address = db.query(Address).filter(
            Address.id == order_data.address_id,
            Address.user_id == current_user.id
        ).first()

        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )

        cart = db.query(Cart).filter(
            Cart.user_id == current_user.id
        ).with_for_update().first()

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )

        cart_items = db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).all()

        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot place an order with an empty cart"
            )

        product_ids = sorted(item.product_id for item in cart_items)


        products = db.query(Product).filter(
            Product.id.in_(product_ids)
        ).order_by(Product.id).with_for_update().all()

        product_map = {product.id: product for product in products}

        for cart_item in cart_items:
            product = product_map.get(cart_item.product_id)

            if product is None or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {cart_item.product_id} is unavailable"
                )

            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}"
                )

        order_subtotal = Decimal("0.00")

        for cart_item in cart_items:
            product = product_map[cart_item.product_id]
            order_subtotal += product.price * cart_item.quantity

        final_total = order_subtotal + DELIVERY_FEE
        shipping_snapshot = format_address(address)

        new_order = Order(
            user_id=current_user.id,
            shipping_address_snapshot=shipping_snapshot,
            status="pending",
            total=final_total
        )

        db.add(new_order)
        db.flush()

        email_items = []

        for cart_item in cart_items:
            product = product_map[cart_item.product_id]
            item_subtotal = product.price * cart_item.quantity

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name_snapshot=product.name,
                quantity=cart_item.quantity,
                unit_price=product.price,
                subtotal=item_subtotal
            )

            db.add(order_item)

            product.stock -= cart_item.quantity

            email_items.append({
                "name": product.name,
                "quantity": cart_item.quantity,
                "subtotal": str(item_subtotal)
            })

        bill = Bill(
            user_id=new_order.user_id,
            order_id=new_order.id,
            bill_number=f"BILL-{uuid.uuid4().hex[:12].upper()}",
            subtotal=order_subtotal,
            delivery_fee=DELIVERY_FEE,
            final_total=final_total
        )

        db.add(bill)

        # Clear the cart in the same transaction.
        db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).delete(synchronize_session=False)

        db.flush()

        # Keep the response data before committing.
        response_items = db.query(OrderItem).filter(
            OrderItem.order_id == new_order.id
        ).all()

        response = build_order_response(new_order, response_items)

        # Order, items, bill, stock and cart changes commit together.
        db.commit()

        # Schedule email only after a successful commit.
        background_tasks.add_task(
            send_order_confirmation,
            current_user.email,
            f"ORD-{new_order.id:06d}",
            email_items,
            str(final_total),
            shipping_snapshot
        )

        return response

    except Exception:
        db.rollback()
        raise


@router.get("", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()

    if not orders:
        return []

    order_ids = [order.id for order in orders]

    all_items = db.query(OrderItem).filter(
        OrderItem.order_id.in_(order_ids)
    ).order_by(OrderItem.id).all()

    items_by_order = {}

    for item in all_items:
        items_by_order.setdefault(item.order_id, []).append(item)

    return [
        build_order_response(
            order,
            items_by_order.get(order.id, [])
        )
        for order in orders
    ]


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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    items = db.query(OrderItem).filter(
        OrderItem.order_id == order.id
    ).all()

    return build_order_response(order, items)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        ).with_for_update().first()

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending orders can be cancelled"
            )

        order_items = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()

        product_ids = sorted(item.product_id for item in order_items)

        products = db.query(Product).filter(
            Product.id.in_(product_ids)
        ).order_by(Product.id).with_for_update().all()

        product_map = {product.id: product for product in products}

        for item in order_items:
            product = product_map.get(item.product_id)

            if product is not None:
                product.stock += item.quantity

        order.status = "cancelled"

        db.flush()

        response = build_order_response(order, order_items)

        db.commit()

        return response

    except Exception:
        db.rollback()
        raise
