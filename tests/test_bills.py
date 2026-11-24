from unittest.mock import patch


def test_list_bills_and_bill_ownership(
    client, auth_headers, second_user_headers, product, address
):
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 1},
        headers=auth_headers
    )

    with patch("main.routers.orders.send_order_confirmation"):
        placed = client.post(
            "/api/v1/orders",
            json={"address_id": address["id"]},
            headers=auth_headers
        )
    assert placed.status_code == 201
    order_id = placed.json()["id"]

    bills = client.get("/api/v1/bills", headers=auth_headers)
    assert bills.status_code == 200
    assert len(bills.json()) == 1
    assert bills.json()[0]["order_id"] == order_id

    own_bill = client.get(
        f"/api/v1/orders/{order_id}/bill",
        headers=auth_headers
    )
    assert own_bill.status_code == 200
    assert own_bill.json()["user_id"] == placed.json()["user_id"]

    other_user_bill = client.get(
        f"/api/v1/orders/{order_id}/bill",
        headers=second_user_headers
    )
    assert other_user_bill.status_code == 404


def test_bills_requires_auth(client):
    response = client.get("/api/v1/bills")
    assert response.status_code == 401
