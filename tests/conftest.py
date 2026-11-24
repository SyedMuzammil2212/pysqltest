import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from main.main import app
from main.database import get_db
from main.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is missing from .env")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

# Compare database names as well as full URLs, so a slightly different URL
# cannot accidentally point tests at the development database.
if make_url(TEST_DATABASE_URL).database == make_url(DATABASE_URL).database:
    raise RuntimeError("TEST_DATABASE_URL must point to a different database")

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture()
def client():
    # TestClient is deliberately NOT used as a context manager here.
    # This avoids running the app lifespan, which currently calls
    # create_tables() against the development DATABASE_URL.
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def user_data():
    return {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "phone": "9876543210"
    }


@pytest.fixture()
def registered_user(client, user_data):
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def auth_headers(client, registered_user, user_data):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def second_user_headers(client):
    data = {
        "name": "Second User",
        "email": "second@example.com",
        "password": "SecondPassword123!",
        "phone": "9876543211"
    }
    register_response = client.post("/api/v1/auth/register", json=data)
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": data["email"],
            "password": data["password"]
        }
    )
    assert login_response.status_code == 200, login_response.text
    return {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }


@pytest.fixture()
def category(client, auth_headers):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics", "description": "Electronic products"},
        headers=auth_headers
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def product(client, auth_headers, category):
    response = client.post(
        "/api/v1/products",
        json={
            "category_id": category["id"],
            "sku": "TEST-PROD-001",
            "name": "Test Wireless Mouse",
            "description": "Test product",
            "price": "599.00",
            "stock": 20
        },
        headers=auth_headers
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def address(client, auth_headers):
    response = client.post(
        "/api/v1/addresses",
        json={
            "address_line_1": "12 Test Street",
            "address_line_2": "Near Test Park",
            "city": "Hyderabad",
            "state": "Telangana",
            "postal_code": "500001"
        },
        headers=auth_headers
    )
    assert response.status_code == 201, response.text
    return response.json()
