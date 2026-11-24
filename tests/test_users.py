def test_get_and_update_profile(client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"

    update = client.patch(
        "/api/v1/users/me",
        json={"name": "Updated Test User", "phone": "9999999999"},
        headers=auth_headers
    )
    assert update.status_code == 200
    assert update.json()["name"] == "Updated Test User"
    assert update.json()["phone"] == "9999999999"


def test_change_password(client, auth_headers):
    response = client.patch(
        "/api/v1/users/me/password",
        json={
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!"
        },
        headers=auth_headers
    )
    assert response.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "TestPassword123!"
        }
    )
    new_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "NewPassword123!"
        }
    )
    assert old_login.status_code == 401
    assert new_login.status_code == 200


def test_change_password_rejects_wrong_current_password(client, auth_headers):
    response = client.patch(
        "/api/v1/users/me/password",
        json={
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!"
        },
        headers=auth_headers
    )
    assert response.status_code == 400


def test_address_crud(client, auth_headers):
    payload = {
        "address_line_1": "12 Test Street",
        "address_line_2": "Apartment 4",
        "city": "Hyderabad",
        "state": "Telangana",
        "postal_code": "500001"
    }

    created = client.post(
        "/api/v1/addresses", json=payload, headers=auth_headers
    )
    assert created.status_code == 201
    address_id = created.json()["id"]

    listed = client.get("/api/v1/addresses", headers=auth_headers)
    assert listed.status_code == 200
    assert any(item["id"] == address_id for item in listed.json())

    fetched = client.get(
        f"/api/v1/addresses/{address_id}", headers=auth_headers
    )
    assert fetched.status_code == 200

    updated = client.patch(
        f"/api/v1/addresses/{address_id}",
        json={"city": "Secunderabad"},
        headers=auth_headers
    )
    assert updated.status_code == 200
    assert updated.json()["city"] == "Secunderabad"

    deleted = client.delete(
        f"/api/v1/addresses/{address_id}", headers=auth_headers
    )
    assert deleted.status_code == 204


def test_user_cannot_access_another_users_address(
    client, auth_headers, second_user_headers
):
    created = client.post(
        "/api/v1/addresses",
        json={
            "address_line_1": "Owner Street",
            "city": "Hyderabad",
            "state": "Telangana",
            "postal_code": "500001"
        },
        headers=auth_headers
    )
    address_id = created.json()["id"]

    response = client.get(
        f"/api/v1/addresses/{address_id}",
        headers=second_user_headers
    )
    assert response.status_code == 404
