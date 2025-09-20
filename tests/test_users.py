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


## authorization tests

def test_true_authenticate_token(test_client):
    login_resp = test_client.post("/users/login", json={
        "email": "dave@example.com",
        "password": "Correctpass123+"
    })
    print(login_resp.json())
    access_token = login_resp.json()["access_token"]
    id = login_resp.json()["id"]
    response = test_client.post("/users/verify", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": id,
        "required_role": "organizer"
    })
    print(response.json())
    assert response.status_code == 200
    assert response.json()["verify"] == True
    assert response.json()["uuid"] == id

def test_authenticate_token_wrong_role(test_client):
    login_resp = test_client.post("/users/login", json={
        "email": "dave@example.com",
        "password": "Correctpass123+"
    })
    access_token = login_resp.json()["access_token"]
    id = login_resp.json()["id"]
    response = test_client.post("/users/verify", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": id,
        "required_role": "vendor"
    })
    assert response.status_code == 200
    assert response.json()["verify"] == False
    assert response.json()["uuid"] == id

def test_authenticate_token_wrong_uuid(test_client):
    login_resp = test_client.post("/users/login", json={
        "email": "bob@example.com",
        "password": "Password123+"
    })
    access_token = login_resp.json()["access_token"]
    response = test_client.post("/users/verify", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": "some-random-uuid",
        "required_role": "organizer"
    })
    assert response.status_code == 200
    assert response.json()["verify"] == False
    assert response.json()["uuid"] == "some-random-uuid"