
import logging
import smtplib
import ssl

from email.message import EmailMessage

from app.config import settings


def send_order_confirmation_email(
    recipient: str,
    order_number: str,
    items: list[dict],
    total: str,
    shipping_address: dict
):

    try:

        # STEP 1: CREATE EMAIL MESSAGE

        message = EmailMessage()

        message["Subject"] = f"Order Confirmation #{order_number}"
        message["From"] = settings.MAIL_FROM
        message["To"] = recipient

        # STEP 2: PREPARE ORDER DETAILS

        item_details = ""

        for item in items:

            item_details += (
                f"\nProduct: {item['name']}"
                f"\nQuantity: {item['quantity']}"
                f"\nUnit Price: Rs. {item['unit_price']}"
                f"\nSubtotal: Rs. {item['subtotal']}\n"
            )

        # STEP 3: PREPARE SHIPPING ADDRESS

        address_details = "\n".join(
            f"{key}: {value}"
            for key, value in shipping_address.items()
        )

        # STEP 4: EMAIL BODY

        message.set_content(f"""
Hello,

Your order has been successfully placed!

Order Number: {order_number}

ORDER DETAILS:
{item_details}

Final Total: Rs. {total}

SHIPPING ADDRESS:
{address_details}

Payment Method: Cash on Delivery

Thank you for shopping with us!
""")

        # STEP 5: CREATE SSL CONTEXT

        context = ssl.create_default_context()

        # STEP 6: CONNECT TO GMAIL SMTP SERVER

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=30
        ) as server:

            server.ehlo()

            # Enable secure TLS connection

            server.starttls(context=context)

            server.ehlo()

            # Authenticate with Gmail

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD
            )

            # Send email

            server.send_message(message)

        # STEP 7: LOG SUCCESS

        logging.info(
            "Order confirmation email sent successfully for order %s",
            order_number
        )

    except Exception:

        logging.exception(
            "Order confirmation email failed for order %s",
            order_number
        )
