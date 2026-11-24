def test_cart_view_and_add_same_product_increments_quantity(
    client, auth_headers, product
):
    empty = client.get("/api/v1/cart", headers=auth_headers)
    assert empty.status_code == 200
    assert empty.json()["items"] == []

    first = client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 2},
        headers=auth_headers
    )
    assert first.status_code == 200
    assert first.json()["items"][0]["quantity"] == 2

    second = client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 3},
        headers=auth_headers
    )
    assert second.status_code == 200
    assert len(second.json()["items"]) == 1
    assert second.json()["items"][0]["quantity"] == 5
    assert float(second.json()["total"]) == 599.00 * 5


def test_cart_update_remove_and_clear(client, auth_headers, product):
    added = client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 2},
        headers=auth_headers
    )
    item_id = added.json()["items"][0]["id"]

    updated = client.patch(
        f"/api/v1/cart/items/{item_id}",
        json={"quantity": 4},
        headers=auth_headers
    )
    assert updated.status_code == 200
    assert updated.json()["items"][0]["quantity"] == 4

    removed = client.delete(
        f"/api/v1/cart/items/{item_id}", headers=auth_headers
    )
    assert removed.status_code == 204

    client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 1},
        headers=auth_headers
    )
    cleared = client.delete("/api/v1/cart", headers=auth_headers)
    assert cleared.status_code == 204

    final_cart = client.get("/api/v1/cart", headers=auth_headers)
    assert final_cart.json()["items"] == []


def test_cart_rejects_insufficient_stock(client, auth_headers, product):
    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 999},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_cart_requires_auth(client, product):
    response = client.get("/api/v1/cart")
    assert response.status_code == 401
