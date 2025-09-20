import pytest

def test_register_user(test_client):
    response = test_client.post("/users/register", json={
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Smith",
        "password": "Password123+",
        "phone_number": "0812345678",
        "role": "vendor"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Alice"
    assert data["last_name"] == "Smith"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "vendor"

def test_register_duplicate_email(test_client):
    test_client.post("/users/register", json={
        "email": "bob@example.com",
        "first_name": "Bob",
        "last_name": "Johnson",
        "password": "Password123+",
        "phone_number": "0899999999",
        "role": "organizer"
    })
    response = test_client.post("/users/register", json={
        "email": "bob@example.com",
        "first_name": "Bob",
        "last_name": "Johnson",
        "password": "Password456+",
        "phone_number": "0888888888",
        "role": "vendor"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(test_client):
    test_client.post("/users/register", json={
        "email": "charlie@example.com",
        "first_name": "Charlie",
        "last_name": "Brown",
        "password": "Secret123+",
        "phone_number": "0877777777",
        "role": "vendor"
    })
    response = test_client.post("/users/login", json={
        "email": "charlie@example.com",
        "password": "Secret123+"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["id"] is not None
    #assert data["id"] == 1
    assert data["role"] == "vendor"

def test_login_wrong_password(test_client):
    test_client.post("/users/register", json={
        "email": "dave@example.com",
        "first_name": "Dave",
        "last_name": "Davis",
        "password": "Correctpass123+",
        "phone_number": "0866666666",
        "role": "organizer"
    })
    response = test_client.post("/users/login", json={
        "email": "dave@example.com",
        "first_name": "Dave",
        "last_name": "Davis",
        "password": "Wrongpass123+"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_logout(test_client):
    test_client.post("/users/register", json={
        "email": "dave@example.com",
        "first_name": "Dave",
        "last_name": "Davis",
        "password": "Correctpass123+",
        "phone_number": "0866666666",
        "role": "organizer"
    })
    login_resp = test_client.post("/users/login", json={
        "email": "dave@example.com",
        "first_name": "Dave",
        "last_name": "Davis",
        "password": "Correctpass123+"
    })
    access_token = login_resp.json()["access_token"]
    response = test_client.post("/users/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
