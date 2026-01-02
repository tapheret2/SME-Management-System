"""Audit log tests."""
import pytest
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.customer import Customer
from app.models.audit import AuditLog
from app.services.auth import hash_password


class TestAuditLog:
    """Audit log tests."""
    
    def _setup_admin(self, db, client):
        """Create admin user."""
        user = User(
            email="admin_audit@example.com",
            hashed_password=hash_password("password123"),
            full_name="Admin Audit",
            role=UserRole.ADMIN
        )
        db.add(user)
        
        customer = Customer(code="AUD001", name="Audit Customer")
        db.add(customer)
        
        product = Product(sku="AUD001", name="Audit Product", current_stock=50)
        db.add(product)
        
        db.commit()
        db.refresh(customer)
        db.refresh(product)
        
        resp = client.post("/api/auth/login", json={
            "email": "admin_audit@example.com",
            "password": "password123"
        })
        return resp.json()["access_token"], customer, product
    
    def test_order_status_change_audit(self, client, db):
        """Test audit log created on order status change."""
        token, customer, product = self._setup_admin(db, client)
        
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
        
        # Change status
        client.put(f"/api/orders/{order_id}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Check audit log exists
        logs = db.query(AuditLog).filter(AuditLog.entity_type == "order").all()
        assert len(logs) >= 1
        
        status_change = next((l for l in logs if l.action == "status_change"), None)
        assert status_change is not None
        assert "draft" in status_change.before_data
        assert "confirmed" in status_change.after_data
    
    def test_audit_endpoint_admin_only(self, client, db):
        """Test audit endpoint requires admin."""
        # Create staff user
        user = User(
            email="staff_audit@example.com",
            hashed_password=hash_password("password123"),
            full_name="Staff Audit",
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        
        resp = client.post("/api/auth/login", json={
            "email": "staff_audit@example.com",
            "password": "password123"
        })
        token = resp.json()["access_token"]
        
        # Try to access audit - should fail
        response = client.get("/api/audit",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
    
    def test_audit_endpoint_filter(self, client, db):
        """Test audit endpoint filtering."""
        token, customer, product = self._setup_admin(db, client)
        
        # Create order to generate audit log
        client.post("/api/orders",
            json={
                "customer_id": str(customer.id),
                "line_items": [{
                    "product_id": str(product.id),
                    "quantity": 1,
                    "unit_price": 50000,
                    "discount": 0
                }]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Query audit logs
        response = client.get("/api/audit?entity_type=order",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
