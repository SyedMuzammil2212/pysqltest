from unittest.mock import patch


def add_product_to_cart(client, headers, product_id, quantity):
    return client.post(
        "/api/v1/cart/items",
        json={"product_id": product_id, "quantity": quantity},
        headers=headers
    )


def test_order_requires_nonempty_cart(client, auth_headers, address):
    response = client.post(
        "/api/v1/orders",
        json={"address_id": address["id"]},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_place_order_updates_stock_cart_and_bill(
    client, auth_headers, product, address
):
    add_response = add_product_to_cart(
        client, auth_headers, product["id"], 2
    )
    assert add_response.status_code == 200

    # Prevent an actual SMTP attempt during automated tests.
    with patch("main.routers.orders.send_order_confirmation") as email_mock:
        response = client.post(
            "/api/v1/orders",
            json={"address_id": address["id"]},
            headers=auth_headers
        )

    assert response.status_code == 201, response.text
    order = response.json()
    assert order["user_id"] > 0
    assert order["status"] == "pending"
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 2
    assert order["items"][0]["product_name_snapshot"] == product["name"]
    assert "12 Test Street" in order["shipping_address_snapshot"]

    cart = client.get("/api/v1/cart", headers=auth_headers)
    assert cart.json()["items"] == []

    updated_product = client.get(f"/api/v1/products/{product['id']}")
    assert updated_product.json()["stock"] == product["stock"] - 2

    bill_response = client.get(
        f"/api/v1/orders/{order['id']}/bill",
        headers=auth_headers
    )
    assert bill_response.status_code == 200
    bill = bill_response.json()
    assert bill["user_id"] == order["user_id"]
    assert bill["order_id"] == order["id"]
    assert float(bill["final_total"]) == float(bill["subtotal"]) + float(bill["delivery_fee"])
    email_mock.assert_called_once()


def test_order_rejects_insufficient_stock(
    client, auth_headers, product, address
):
    add_product_to_cart(client, auth_headers, product["id"], 2)

    # Reduce stock after the item enters the cart to exercise order-time validation.
    stock_update = client.patch(
        f"/api/v1/products/{product['id']}/stock",
        json={"stock": 1},
        headers=auth_headers
    )
    assert stock_update.status_code == 200

    response = client.post(
        "/api/v1/orders",
        json={"address_id": address["id"]},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_user_cannot_place_order_using_another_users_address(
    client, auth_headers, second_user_headers, product
):
    other_address = client.post(
        "/api/v1/addresses",
        json={
            "address_line_1": "Other User Road",
            "city": "Hyderabad",
            "state": "Telangana",
            "postal_code": "500002"
        },
        headers=second_user_headers
    ).json()

    add_product_to_cart(client, auth_headers, product["id"], 1)
    response = client.post(
        "/api/v1/orders",
        json={"address_id": other_address["id"]},
        headers=auth_headers
    )
    assert response.status_code == 404


def test_list_get_and_cancel_order_restores_stock(
    client, auth_headers, product, address
):
    add_product_to_cart(client, auth_headers, product["id"], 3)

    with patch("main.routers.orders.send_order_confirmation"):
        placed = client.post(
            "/api/v1/orders",
            json={"address_id": address["id"]},
            headers=auth_headers
        )
    assert placed.status_code == 201
    order_id = placed.json()["id"]

    listed = client.get("/api/v1/orders", headers=auth_headers)
    assert listed.status_code == 200
    assert any(order["id"] == order_id for order in listed.json())

    fetched = client.get(
        f"/api/v1/orders/{order_id}", headers=auth_headers
    )
    assert fetched.status_code == 200

    before_cancel = client.get(f"/api/v1/products/{product['id']}")
    reduced_stock = before_cancel.json()["stock"]

    cancelled = client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=auth_headers
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    after_cancel = client.get(f"/api/v1/products/{product['id']}")
    assert after_cancel.json()["stock"] == reduced_stock + 3

    second_cancel = client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=auth_headers
    )
    assert second_cancel.status_code == 400


def test_user_cannot_view_another_users_order(
    client, auth_headers, second_user_headers, product, address
):
    add_product_to_cart(client, auth_headers, product["id"], 1)
    with patch("main.routers.orders.send_order_confirmation"):
        placed = client.post(
            "/api/v1/orders",
            json={"address_id": address["id"]},
            headers=auth_headers
        )
    order_id = placed.json()["id"]

    response = client.get(
        f"/api/v1/orders/{order_id}",
        headers=second_user_headers
    )
    assert response.status_code == 404
