"""Milestone 4 tests - Orders with status workflow."""
import pytest
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.customer import Customer
from app.services.auth import hash_password


class TestMilestone4Orders:
    """Milestone 4: Order tests."""
    
    def _setup(self, db, client):
        """Helper to create user, customer, and product."""
        user = User(
            email="order@example.com",
            hashed_password=hash_password("password123"),
            full_name="Order User",
            role=UserRole.STAFF
        )
        db.add(user)
        
        customer = Customer(code="KH001", name="Test Customer")
        db.add(customer)
        
        product = Product(
            sku="ORD001", 
            name="Order Test Product", 
            current_stock=100,
            sell_price=Decimal("100000")
        )
        db.add(product)
        db.commit()
        db.refresh(customer)
        db.refresh(product)
        
        resp = client.post("/api/auth/login", json={
            "email": "order@example.com",
            "password": "password123"
        })
        return resp.json()["access_token"], customer, product
    
    def test_create_order(self, client, db):
        """Test creating an order."""
        token, customer, product = self._setup(db, client)
        
        response = client.post("/api/orders",
            json={
                "customer_id": str(customer.id),
                "line_items": [{
                    "product_id": str(product.id),
                    "quantity": 5,
                    "unit_price": 100000,
                    "discount": 0
                }],
                "discount": 50000,
                "notes": "Test order"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "draft"
        assert Decimal(data["subtotal"]) == Decimal("500000")
        assert Decimal(data["total"]) == Decimal("450000")  # 500000 - 50000
    
    def test_confirm_order_deducts_stock(self, client, db):
        """Test confirming order deducts stock."""
        token, customer, product = self._setup(db, client)
        initial_stock = product.current_stock
        
        # Create order
        create_resp = client.post("/api/orders",
            json={
                "customer_id": str(customer.id),
                "line_items": [{
                    "product_id": str(product.id),
                    "quantity": 10,
                    "unit_price": 100000,
                    "discount": 0
                }]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = create_resp.json()["id"]
        
        # Confirm order
        response = client.put(f"/api/orders/{order_id}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"
        
        # Verify stock deducted
        db.refresh(product)
        assert product.current_stock == initial_stock - 10
    
    def test_cancel_order_restores_stock(self, client, db):
        """Test cancelling confirmed order restores stock."""
        token, customer, product = self._setup(db, client)
        initial_stock = product.current_stock
        
        # Create and confirm order
        create_resp = client.post("/api/orders",
            json={
                "customer_id": str(customer.id),
                "line_items": [{
                    "product_id": str(product.id),
                    "quantity": 10,
                    "unit_price": 100000,
                    "discount": 0
                }]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = create_resp.json()["id"]
        
        client.put(f"/api/orders/{order_id}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Cancel order
        response = client.put(f"/api/orders/{order_id}/status",
            json={"status": "cancelled"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Verify stock restored
        db.refresh(product)
        assert product.current_stock == initial_stock
    
    def test_invalid_status_transition(self, client, db):
        """Test invalid status transition fails."""
        token, customer, product = self._setup(db, client)
        
        # Create order (draft)
        create_resp = client.post("/api/orders",
            json={
                "customer_id": str(customer.id),
                "line_items": [{
                    "product_id": str(product.id),
                    "quantity": 5,
                    "unit_price": 100000,
                    "discount": 0
                }]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = create_resp.json()["id"]
        
        # Try to skip to completed (invalid)
        response = client.put(f"/api/orders/{order_id}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert "Cannot transition" in response.json()["detail"]
    
    def test_status_workflow(self, client, db):
        """Test complete status workflow."""
        token, customer, product = self._setup(db, client)
        
        # Create order
        create_resp = client.post("/api/orders",
            json={
                "customer_id": str(customer.id),
                "line_items": [{
                    "product_id": str(product.id),
                    "quantity": 2,
                    "unit_price": 100000,
                    "discount": 0
                }]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = create_resp.json()["id"]
        
        # Draft -> Confirmed
        resp = client.put(f"/api/orders/{order_id}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.json()["status"] == "confirmed"
        
        # Confirmed -> Shipped
        resp = client.put(f"/api/orders/{order_id}/status",
            json={"status": "shipped"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.json()["status"] == "shipped"
        
        # Shipped -> Completed
        resp = client.put(f"/api/orders/{order_id}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.json()["status"] == "completed"
    
    def test_insufficient_stock_on_confirm(self, client, db):
        """Test confirm fails with insufficient stock."""
        token, customer, product = self._setup(db, client)
        
        # Create order with more than available stock
        create_resp = client.post("/api/orders",
            json={
                "customer_id": str(customer.id),
                "line_items": [{
                    "product_id": str(product.id),
                    "quantity": 200,  # More than available
                    "unit_price": 100000,
                    "discount": 0
                }]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = create_resp.json()["id"]
        
        # Try to confirm - should fail
        response = client.put(f"/api/orders/{order_id}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]
