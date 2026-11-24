import os
import smtplib
import logging

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_order_confirmation(
    recipient: str,
    order_number: str,
    items: list[dict],
    total: str,
    shipping_address: str
):
    try:
        smtp_host = os.getenv("SMTP_HOST", "localhost")
        smtp_port = int(os.getenv("SMTP_PORT", "1025"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        sender = os.getenv("SMTP_FROM_EMAIL", "test@example.com")
        use_tls = os.getenv("SMTP_USE_TLS", "false").lower() == "true"

        message = EmailMessage()
        message["Subject"] = f"Order Confirmation - {order_number}"
        message["From"] = sender
        message["To"] = recipient

        item_details = "\n".join(
            f"- {item['name']} | Quantity: {item['quantity']} "
            f"| Subtotal: {item['subtotal']}"
            for item in items
        )

        message.set_content(
            f"""
Thank you for your order!

Order Number: {order_number}

Items:
{item_details}

Total: {total}

Shipping Address:
{shipping_address}

Payment Method: Cash on Delivery
"""
        )

        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            if use_tls:
                server.starttls()

            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)

            server.send_message(message)
            return True

    except Exception:
        logger.exception("Failed to send order confirmation email")
        return False