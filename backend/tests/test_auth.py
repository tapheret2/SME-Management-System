import pytest
from tests.conftest import auth_header


class TestAuth:
    """Test authentication endpoints."""
    
    def test_login_success(self, client, admin_user):
        """Test successful login."""
        response = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, admin_user):
        """Test login with wrong password."""
        response = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "password123"
        })
        assert response.status_code == 401
    
    def test_get_current_user(self, client, admin_token):
        """Test getting current user info."""
        response = client.get("/api/auth/me", headers=auth_header(admin_token))
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # No auth header
    
    def test_refresh_token(self, client, admin_user):
        """Test token refresh."""
        # First login
        login_response = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "password123"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_logout(self, client, admin_token):
        """Test logout."""
        response = client.post("/api/auth/logout", headers=auth_header(admin_token))
        assert response.status_code == 200


class TestUserRBAC:
    """Test role-based access control."""
    
    def test_admin_can_list_users(self, client, admin_token):
        """Test admin can list users."""
        response = client.get("/api/users", headers=auth_header(admin_token))
        assert response.status_code == 200
    
    def test_staff_cannot_list_users(self, client, staff_token):
        """Test staff cannot list users."""
        response = client.get("/api/users", headers=auth_header(staff_token))
        assert response.status_code == 403
    
    def test_admin_can_create_user(self, client, admin_token):
        """Test admin can create users."""
        response = client.post("/api/users", 
            headers=auth_header(admin_token),
            json={
                "email": "newuser@test.com",
                "password": "password123",
                "full_name": "New User",
                "role": "staff"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
