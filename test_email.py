from main.utils.email import send_order_confirmation

# send_order_confirmation(
#     recipient="your-gmail-address@gmail.com",
#     order_number="ORD-TEST-0001",
#     items=[
#         {
#             "name": "Test Product",
#             "quantity": 2,
#             "subtotal": "100.00"
#         }
#     ],
#     total="150.00",
#     shipping_address="Test Street, Hyderabad"
# )

# print("Email function executed. Check your inbox and terminal.")

success = send_order_confirmation(
    recipient="codingmo85@gmail.com",
    order_number="ORD-TEST-0001",
    items=[
        {
            "name": "Test Product",
            "quantity": 2,
            "subtotal": "100.00"
        }
    ],
    total="150.00",
    shipping_address="Test Street, Hyderabad"
)

print("Email sent successfully!" if success else "Email sending failed. Check the terminal error.")