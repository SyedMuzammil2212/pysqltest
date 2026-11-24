def test_category_crud(client, auth_headers):
    created = client.post(
        "/api/v1/categories",
        json={"name": "Books", "description": "Printed books"},
        headers=auth_headers
    )
    assert created.status_code == 201
    category_id = created.json()["id"]

    listed = client.get("/api/v1/categories")
    assert listed.status_code == 200
    assert any(item["id"] == category_id for item in listed.json())

    fetched = client.get(f"/api/v1/categories/{category_id}")
    assert fetched.status_code == 200

    updated = client.patch(
        f"/api/v1/categories/{category_id}",
        json={"name": "Programming Books"},
        headers=auth_headers
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Programming Books"

    deleted = client.delete(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers
    )
    assert deleted.status_code == 204


def test_category_cannot_be_deleted_when_product_exists(
    client, auth_headers, category, product
):
    response = client.delete(
        f"/api/v1/categories/{category['id']}",
        headers=auth_headers
    )
    assert response.status_code == 409


def test_product_create_and_category_validation(client, auth_headers, category):
    bad = client.post(
        "/api/v1/products",
        json={
            "category_id": 99999,
            "sku": "BAD-CAT",
            "name": "Invalid Category Product",
            "price": "10.00",
            "stock": 5
        },
        headers=auth_headers
    )
    assert bad.status_code == 404

    good = client.post(
        "/api/v1/products",
        json={
            "category_id": category["id"],
            "sku": "PROD-NEW",
            "name": "New Product",
            "price": "100.00",
            "stock": 10
        },
        headers=auth_headers
    )
    assert good.status_code == 201


def test_product_browse_search_filter_and_sort(client, product, category):
    all_products = client.get("/api/v1/products")
    assert all_products.status_code == 200
    assert any(p["id"] == product["id"] for p in all_products.json())

    searched = client.get("/api/v1/products", params={"search": "Wireless"})
    assert searched.status_code == 200
    assert any(p["id"] == product["id"] for p in searched.json())

    filtered = client.get(
        "/api/v1/products", params={"category_id": category["id"]}
    )
    assert filtered.status_code == 200
    assert all(p["category_id"] == category["id"] for p in filtered.json())

    sorted_desc = client.get(
        "/api/v1/products", params={"sort_order": "desc"}
    )
    assert sorted_desc.status_code == 200
    prices = [float(p["price"]) for p in sorted_desc.json()]
    assert prices == sorted(prices, reverse=True)

    paged = client.get(
        "/api/v1/products", params={"page": 1, "page_size": 1}
    )
    assert paged.status_code == 200
    assert len(paged.json()) <= 1


def test_get_update_stock_and_deactivate_product(
    client, auth_headers, product, category
):
    fetched = client.get(f"/api/v1/products/{product['id']}")
    assert fetched.status_code == 200

    updated = client.patch(
        f"/api/v1/products/{product['id']}",
        json={"name": "Updated Mouse", "category_id": category["id"]},
        headers=auth_headers
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated Mouse"

    stock = client.patch(
        f"/api/v1/products/{product['id']}/stock",
        json={"stock": 35},
        headers=auth_headers
    )
    assert stock.status_code == 200
    assert stock.json()["stock"] == 35

    deactivated = client.delete(
        f"/api/v1/products/{product['id']}",
        headers=auth_headers
    )
    assert deactivated.status_code == 204

    assert client.get(f"/api/v1/products/{product['id']}").status_code == 404
    listing = client.get("/api/v1/products")
    assert all(p["id"] != product["id"] for p in listing.json())


def test_list_products_in_category(client, category, product):
    response = client.get(
        f"/api/v1/categories/{category['id']}/products"
    )
    assert response.status_code == 200
    assert any(p["id"] == product["id"] for p in response.json())


def test_product_management_requires_auth(client, category):
    response = client.post(
        "/api/v1/products",
        json={
            "category_id": category["id"],
            "sku": "NO-AUTH",
            "name": "No Auth Product",
            "price": "20.00",
            "stock": 1
        }
    )
    assert response.status_code == 401
