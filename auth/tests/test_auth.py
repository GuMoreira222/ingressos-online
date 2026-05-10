from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_public_forces_user_role(client: TestClient):
    # User tries to register with role=admin
    response = client.post(
        "/auth/register",
        json={
            "email": "hacker@test.com",
            "password": "hackpassword",
            "role": "admin"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "hacker@test.com"
    # Security Check: Role must be forced to 'user'
    assert data["role"] == "user"
    assert "password" not in data

def test_login_basic_auth_success(client: TestClient, normal_user):
    # Test basic auth login
    response = client.post(
        "/auth/login",
        data={"username": "user@test.com", "password": "userpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_basic_auth_failure(client: TestClient, normal_user):
    response = client.post(
        "/auth/login",
        data={"username": "user@test.com", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_protected_route_me(client: TestClient, normal_user):
    # Login to get token
    login_response = client.post("/auth/login", data={"username": "user@test.com", "password": "userpass"})
    token = login_response.json()["access_token"]
    
    # Access protected route
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@test.com"
    assert response.json()["role"] == "user"

def test_admin_can_create_admin(client: TestClient, admin_token: str):
    # Authenticated Admin tries to create another admin
    response = client.post(
        "/auth/register",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "newadmin@test.com",
            "password": "newadminpass",
            "role": "admin"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newadmin@test.com"
    # Since caller is admin, role should be respected
    assert data["role"] == "admin"
