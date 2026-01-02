"""Milestone 2 tests - Authentication and RBAC."""
import pytest
from app.models.user import User, UserRole
from app.services.auth import hash_password


class TestMilestone2Auth:
    """Milestone 2: Auth tests."""
    
    def test_login_success(self, client, db):
        """Test successful login."""
        # Create user
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test User",
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        
        # Login
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_password(self, client, db):
        """Test login with wrong password."""
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test User",
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with unknown email."""
        response = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123"
        })
        assert response.status_code == 401
    
    def test_me_authenticated(self, client, db):
        """Test /me endpoint with valid token."""
        # Create and login user
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test User",
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        
        login_resp = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        token = login_resp.json()["access_token"]
        
        # Get me
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "staff"
    
    def test_me_unauthenticated(self, client):
        """Test /me without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_refresh_token(self, client, db):
        """Test refresh token flow."""
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test User",
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        
        # Login
        login_resp = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        refresh_token = login_resp.json()["refresh_token"]
        
        # Refresh
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_register_admin_only(self, client, db):
        """Test register requires admin."""
        # Create non-admin user
        user = User(
            email="staff@example.com",
            hashed_password=hash_password("password123"),
            full_name="Staff User",
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        
        login_resp = client.post("/api/auth/login", json={
            "email": "staff@example.com",
            "password": "password123"
        })
        token = login_resp.json()["access_token"]
        
        # Try to register - should fail
        response = client.post("/api/auth/register", 
            json={"email": "new@example.com", "password": "pass123", "full_name": "New", "role": "staff"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
    
    def test_logout(self, client, db):
        """Test logout invalidates token."""
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test User",
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        
        login_resp = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        tokens = login_resp.json()
        
        # Logout
        response = client.post("/api/auth/logout", 
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        assert response.status_code == 200
        
        # Try to refresh - should fail
        response = client.post("/api/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        assert response.status_code == 401
