def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "register@example.com",
            "password": "TestPassword123!",
            "phone": "9876543210"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "register@example.com"
    assert "password_hash" not in response.json()


def test_register_duplicate_email(client):
    data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "TestPassword123!"
    }
    assert client.post("/api/v1/auth/register", json=data).status_code == 201
    response = client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 409


def test_login_success(client, user_data):
    client.post("/api/v1/auth/register", json=user_data)
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_invalid_password(client, user_data):
    client.post("/api/v1/auth/register", json=user_data)
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["email"],
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == 401


def test_protected_endpoint_requires_login(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
