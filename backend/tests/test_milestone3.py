"""Milestone 3 tests - Products and Stock."""
import pytest
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.product import Product
from app.services.auth import hash_password


class TestMilestone3Products:
    """Milestone 3: Product CRUD tests."""
    
    def _create_auth_user(self, db, client):
        """Helper to create user and get token."""
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test User",
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        
        resp = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        return resp.json()["access_token"]
    
    def test_create_product(self, client, db):
        """Test creating a product."""
        token = self._create_auth_user(db, client)
        
        response = client.post("/api/products", 
            json={
                "sku": "TEST001",
                "name": "Test Product",
                "category": "Test",
                "unit": "cái",
                "cost_price": 100000,
                "sell_price": 150000,
                "current_stock": 10,
                "min_stock": 5
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == "TEST001"
        assert data["name"] == "Test Product"
        assert data["current_stock"] == 10
    
    def test_list_products(self, client, db):
        """Test listing products."""
        token = self._create_auth_user(db, client)
        
        # Create product
        product = Product(sku="P001", name="Product 1", current_stock=10)
        db.add(product)
        db.commit()
        
        response = client.get("/api/products",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    def test_get_low_stock_products(self, client, db):
        """Test low stock endpoint."""
        token = self._create_auth_user(db, client)
        
        # Create low stock product
        product = Product(sku="LOW001", name="Low Stock", current_stock=2, min_stock=5)
        db.add(product)
        db.commit()
        
        response = client.get("/api/products/low-stock",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["sku"] == "LOW001" for p in data)
    
    def test_update_product(self, client, db):
        """Test updating a product."""
        token = self._create_auth_user(db, client)
        
        product = Product(sku="UPD001", name="To Update", current_stock=10)
        db.add(product)
        db.commit()
        db.refresh(product)
        
        response = client.put(f"/api/products/{product.id}",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
    
    def test_delete_product(self, client, db):
        """Test soft delete product."""
        token = self._create_auth_user(db, client)
        
        product = Product(sku="DEL001", name="To Delete", current_stock=10)
        db.add(product)
        db.commit()
        db.refresh(product)
        
        response = client.delete(f"/api/products/{product.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204
        
        # Verify soft delete
        db.refresh(product)
        assert product.is_active == False


class TestMilestone3Stock:
    """Milestone 3: Stock movement tests."""
    
    def _setup(self, db, client):
        """Helper to create user and product."""
        user = User(
            email="stock@example.com",
            hashed_password=hash_password("password123"),
            full_name="Stock User",
            role=UserRole.STAFF
        )
        db.add(user)
        
        product = Product(sku="STK001", name="Stock Test", current_stock=100)
        db.add(product)
        db.commit()
        db.refresh(product)
        
        resp = client.post("/api/auth/login", json={
            "email": "stock@example.com",
            "password": "password123"
        })
        return resp.json()["access_token"], product
    
    def test_stock_in(self, client, db):
        """Test stock in operation."""
        token, product = self._setup(db, client)
        
        response = client.post("/api/stock/in",
            json={"product_id": str(product.id), "quantity": 50, "reason": "Nhập hàng"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["stock_before"] == 100
        assert data["stock_after"] == 150
        assert data["type"] == "in"
    
    def test_stock_out(self, client, db):
        """Test stock out operation."""
        token, product = self._setup(db, client)
        
        response = client.post("/api/stock/out",
            json={"product_id": str(product.id), "quantity": 30, "reason": "Xuất bán"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["stock_before"] == 100
        assert data["stock_after"] == 70
    
    def test_stock_out_insufficient(self, client, db):
        """Test stock out with insufficient stock."""
        token, product = self._setup(db, client)
        
        response = client.post("/api/stock/out",
            json={"product_id": str(product.id), "quantity": 200},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert "Insufficient" in response.json()["detail"]
    
    def test_stock_adjust(self, client, db):
        """Test stock adjustment."""
        token, product = self._setup(db, client)
        
        response = client.post("/api/stock/adjust",
            json={"product_id": str(product.id), "quantity": -10, "reason": "Kiểm kê thiếu"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["stock_after"] == 90
