import smtplib
from email.message import EmailMessage
from cores.config import settings

def send_order_email(email : str, order_id : int, total : float):
    message = EmailMessage()

    message["Subject"] = f"Order confirmation   #{order_id}"
    message["From"] = settings.MAIL_FROM
    message["To"] = email

    message.set_content(f"""
    Thank you for your order!

    Your order #{order_id} has been successfully placed.

    Order Total : {total}

    Thank you shopping with us!
    Please visit Again.
    """)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)

    except Exception as e:
        print(f"Email sending Failed {e}")