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

# Edit user info
def test_edit_user_info(test_client):
    test_client.post("/users/register", json={
        "email": "bob@example.com",
        "first_name": "Bob",
        "last_name": "Johnson",
        "password": "Password123+",
        "phone_number": "0899999999",
        "role": "organizer"
    })
    login_resp = test_client.post("/users/login", json={
        "email": "bob@example.com",
        "password": "Password123+",
    })
    access_token = login_resp.json()["access_token"]
    id = login_resp.json()["id"]
    response = test_client.put("/users/info", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": id,
        "first_name": "Robert",
        "phone_number": "0811111111"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Robert"
    assert data["phone_number"] == "0811111111"
    assert data["last_name"] == "Johnson"  # unchanged
    assert data["email"] == "bob@example.com"  # unchanged
    assert data["role"] == "organizer"  # unchanged

def test_edit_user_info_duplicate_email(test_client):
    login_resp = test_client.post("/users/login", json={
        "email": "bob@example.com",
        "password": "Password123+",
    })
    access_token = login_resp.json()["access_token"]
    id = login_resp.json()["id"]

    test_client.put("/users/info", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": id,
        "email": "bob@example.com",
        "first_name": "Robert",
        "phone_number": "0811111111"
    }) # First update to ensure email is taken
    response = test_client.put("/users/info", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": id,
        "email": "dave@example.com",
        "first_name": "Bobby",
        "phone_number": "0822222222"
    }) # Attempt to change to the same email again
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already in use"

def test_edit_user_info_unauthorized(test_client):
    response = test_client.put("/users/info", json={
        "first_name": "Hacker",
        "phone_number": "0800000000"
    })
    assert response.status_code == 403  # No token provided
    assert response.json()["detail"] == "Not authenticated"

def test_edit_user_info_invalid_token(test_client):
    response = test_client.put("/users/info", headers={"Authorization": "Bearer invalid_token"}, json={
        "first_name": "Hacker",
        "phone_number": "0800000000"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_edit_user_info_blacklisted_token(test_client):
    login_resp = test_client.post("/users/login", json={
        "email": "bob@example.com",
        "password": "Password123+"
    })
    access_token = login_resp.json()["access_token"]
    id = login_resp.json()["id"]
    test_client.post("/users/logout", headers={"Authorization": f"Bearer {access_token}"})
    response = test_client.put("/users/info", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": id,
        "first_name": "Hacker",
        "phone_number": "0800000000"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has been revoked"

def test_edit_user_info_user_not_found(test_client):
    login_resp = test_client.post("/users/login", json={
        "email": "nonexistent@example.com",
        "password": "NoPass123+"
    })
    access_token = login_resp.json().get("access_token", "some_valid_token")
    response = test_client.put("/users/info", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": "nonexistent-uuid",
        "first_name": "Ghost",
        "phone_number": "0800000000"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_change_password(test_client):
    test_client.post("/users/register", json={
        "email": "bo2b@example.com",
        "password": "Password123+",
        "first_name": "Bob",
        "last_name": "Johnson",
        "phone_number": "0812345678",
        "role": "vendor"
    })
    login_resp = test_client.post("/users/login", json={
        "email": "bo2b@example.com",
        "password": "Password123+"
    })
    access_token = login_resp.json()["access_token"]
    id = login_resp.json()["id"]
    response = test_client.put("/users/password", headers={"Authorization": f"Bearer {access_token}"}, json={
        "new_password": "NewPassword123+"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"
    login_resp = test_client.post("/users/login", json={
        "email": "bo2b@example.com",
        "password": "NewPassword123+"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()
    assert login_resp.json()["id"] == id
    assert login_resp.json()["role"] == "vendor"  # default role
    response = test_client.put("/users/password", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": id,
        "new_password": "AnotherNewPassword123+"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"
    login_resp = test_client.post("/users/login", json={
        "email": "bo2b@example.com",
        "password": "AnotherNewPassword123+"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()
    assert login_resp.json()["id"] == id
    assert login_resp.json()["role"] == "vendor"  # default role  

def test_change_password_unauthorized(test_client): 
    response = test_client.put("/users/password", json={
        "new_password": "HackerPass123+"
    })
    assert response.status_code == 403  # No token provided
    assert response.json()["detail"] == "Not authenticated"

def test_change_password_invalid_token(test_client):
    response = test_client.put("/users/password", headers={"Authorization": "Bearer invalid_token"}, json={
        "new_password": "HackerPass123+"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_change_password_blacklisted_token(test_client):
    test_client.post("/users/register", json={
        "email": "bo3b@example.com",
        "password": "Password123+",
        "first_name": "Bob",
        "last_name": "Johnson",
        "phone_number": "0812345678",
        "role": "vendor"
    })
    login_resp = test_client.post("/users/login", json={
        "email": "bo3b@example.com",
        "password": "Password123+"
    })
    access_token = login_resp.json()["access_token"]
    id = login_resp.json()["id"]
    test_client.post("/users/logout", headers={"Authorization": f"Bearer {access_token}"
    })
    response = test_client.put("/users/password", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": id,
        "new_password": "HackerPass123+"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has been revoked"
def test_change_password_user_not_found(test_client):
    login_resp = test_client.post("/users/login", json={
        "email": "nonexistent@example.com",
        "password": "NoPass123+"
    })
    access_token = login_resp.json().get("access_token", "some_valid_token")
    response = test_client.put("/users/password", headers={"Authorization": f"Bearer {access_token}"}, json={
        "uuid": "nonexistent-uuid",
        "new_password": "GhostPass123+"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
    
