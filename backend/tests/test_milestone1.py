"""Milestone 1 tests - Basic API and DB connection."""
import pytest


class TestMilestone1:
    """Milestone 1: Health check and DB connection tests."""
    
    def test_root_endpoint(self, client):
        """Test root returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "SME Management System API"
        assert "version" in data
    
    def test_health_check(self, client):
        """Test health endpoint returns status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "app_name" in data
    
    def test_cors_preflight(self, client):
        """Test CORS preflight request."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert response.status_code == 200
    
    def test_nonexistent_endpoint(self, client):
        """Test 404 for unknown route."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
