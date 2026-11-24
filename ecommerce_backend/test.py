import smtplib
import ssl

try:
    print("Connecting to Gmail...")

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587,
        timeout=30
    )

    print("Connected successfully!")

    server.ehlo()

    server.starttls(
        context=ssl.create_default_context()
    )

    print("TLS connection successful!")

    server.ehlo()
    server.quit()

except Exception as e:
    print("Error:", repr(e))