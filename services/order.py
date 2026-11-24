from sqlalchemy.orm import Session
from fastapi import HTTPException
from decimal import Decimal

from models.order import Order, OrderItem
from models.cart import Cart
from models.address import Address
from models.product import Product
from models.bill import Bill
from cores.config import settings


class OrderService:

    def get_orders(self, db: Session, user_id: int):
        return db.query(Order).filter(Order.user_id == user_id).all()

    def get_order(self, db: Session, user_id: int, order_id: int):
        order = db.query(Order).filter( Order.id == order_id, Order.user_id == user_id).first()
        if not order:
            raise HTTPException(404, "Order not found.")

        return order

    def checkout(self, db: Session, user_id: int, address_id: int):
        try:
            # Get cart
            cart = db.query(Cart).filter(Cart.user_id == user_id).first()

            if not cart or not cart.items:
                raise HTTPException(400, "Cart is empty.")

            # Verify address ownership
            address = db.query(Address).filter(Address.id == address_id, Address.user_id == user_id).first()

            if not address:
                raise HTTPException(404, "Address not found.")

            subtotal = Decimal("0.00")
            order_items = []

            # Validate stock and calculate total
            for item in cart.items:
                product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()

                if not product or not product.is_active:
                    raise HTTPException(400, "Product unavailable.")

                if product.stock < item.quantity:
                    raise HTTPException(400, "Insufficient stock.")

                item_total = product.price * item.quantity
                subtotal += item_total
                product.stock -= item.quantity

                order_items.append({
                    "product_id": product.id,
                    "product_name_snapshot": product.name,
                   "quantity": item.quantity,
                    "unit_price": product.price,
                    "subtotal": item_total
                })

            # Calculate final amount
            delivery_fee = Decimal(str(settings.DELIVERY_FEE))
            final_total = subtotal + delivery_fee

            # Create order
            order = Order(
                user_id=user_id,
                shipping_address_snapshot={
                    "address_line": address.address_line,
                    "city": address.city,
                    "state": address.state,
                    "postal_code": address.postal_code
                },
                status="pending",
                total=final_total
            )

            db.add(order)
            db.flush()

            # Create order items
            for item in order_items:
                db.add(OrderItem(order_id=order.id, **item))

            # Create bill
            bill = Bill(
                user_id=user_id,
                order_id=order.id,
                bill_number=f"BILL-{order.id}",
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                final_total=final_total
            )

            db.add(bill)

            # Clear cart
            for item in cart.items:
                db.delete(item)

            db.commit()
            db.refresh(order)

            return order

        except Exception:
            db.rollback()
            raise

    def cancel_order(self, db: Session, user_id: int, order_id: int):
        try:
            order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).with_for_update().first()

            if not order:
                raise HTTPException(404, "Order not found.")

            if order.status != "pending":
                raise HTTPException(400, "Order cannot be cancelled.")

            for item in order.items:
                product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()

                if product:
                    product.stock += item.quantity

            order.status = "cancelled"

            db.commit()
            db.refresh(order)

            return order

        except Exception:
            db.rollback()
            raise


order_service = OrderService()