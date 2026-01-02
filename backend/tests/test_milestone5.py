"""Milestone 5 tests - Payments and Reports."""
import pytest
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.services.auth import hash_password


class TestMilestone5Payments:
    """Milestone 5: Payment tests."""
    
    def _setup(self, db, client):
        """Helper to create user and customer."""
        user = User(
            email="pay@example.com",
            hashed_password=hash_password("password123"),
            full_name="Pay User",
            role=UserRole.STAFF
        )
        db.add(user)
        
        customer = Customer(code="PAY001", name="Payment Customer", total_debt=Decimal("500000"))
        db.add(customer)
        
        supplier = Supplier(code="SUP001", name="Test Supplier", total_payable=Decimal("200000"))
        db.add(supplier)
        
        db.commit()
        db.refresh(customer)
        db.refresh(supplier)
        
        resp = client.post("/api/auth/login", json={
            "email": "pay@example.com",
            "password": "password123"
        })
        return resp.json()["access_token"], customer, supplier
    
    def test_create_incoming_payment(self, client, db):
        """Test creating incoming payment from customer."""
        token, customer, _ = self._setup(db, client)
        
        response = client.post("/api/payments",
            json={
                "type": "incoming",
                "method": "bank",
                "customer_id": str(customer.id),
                "amount": 100000,
                "notes": "Test payment"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "incoming"
        assert "PAY-" in data["payment_number"]
    
    def test_incoming_payment_reduces_debt(self, client, db):
        """Test incoming payment reduces customer debt."""
        token, customer, _ = self._setup(db, client)
        initial_debt = customer.total_debt
        
        client.post("/api/payments",
            json={
                "type": "incoming",
                "customer_id": str(customer.id),
                "amount": 100000
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        db.refresh(customer)
        assert customer.total_debt == initial_debt - Decimal("100000")
    
    def test_ar_ap_summary(self, client, db):
        """Test AR/AP summary."""
        token, _, _ = self._setup(db, client)
        
        response = client.get("/api/payments/ar-ap",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_receivables" in data
        assert "total_payables" in data


class TestMilestone5Reports:
    """Milestone 5: Report tests."""
    
    def _setup(self, db, client):
        user = User(
            email="report@example.com",
            hashed_password=hash_password("password123"),
            full_name="Report User",
            role=UserRole.STAFF
        )
        db.add(user)
        
        product = Product(sku="REP001", name="Report Product", current_stock=50)
        db.add(product)
        
        customer = Customer(code="RKH001", name="Report Customer")
        db.add(customer)
        
        supplier = Supplier(code="RSUP001", name="Report Supplier")
        db.add(supplier)
        
        db.commit()
        
        resp = client.post("/api/auth/login", json={
            "email": "report@example.com",
            "password": "password123"
        })
        return resp.json()["access_token"]
    
    def test_dashboard_metrics(self, client, db):
        """Test dashboard metrics endpoint."""
        token = self._setup(db, client)
        
        response = client.get("/api/reports/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "today_revenue" in data
        assert "month_revenue" in data
        assert "total_customers" in data
        assert "low_stock_count" in data
    
    def test_revenue_report(self, client, db):
        """Test revenue report."""
        token = self._setup(db, client)
        
        response = client.get("/api/reports/revenue?days=30",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total_revenue" in data
        assert "total_orders" in data
    
    def test_top_products(self, client, db):
        """Test top products report."""
        token = self._setup(db, client)
        
        response = client.get("/api/reports/top-products?days=30&limit=10",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestMilestone5Export:
    """Milestone 5: Export tests."""
    
    def _auth(self, db, client):
        user = User(
            email="export@example.com",
            hashed_password=hash_password("password123"),
            full_name="Export User",
            role=UserRole.STAFF
        )
        db.add(user)
        db.commit()
        
        resp = client.post("/api/auth/login", json={
            "email": "export@example.com",
            "password": "password123"
        })
        return resp.json()["access_token"]
    
    def test_export_products_csv(self, client, db):
        """Test export products CSV."""
        token = self._auth(db, client)
        
        response = client.get("/api/export/products.csv",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
    
    def test_export_orders_csv(self, client, db):
        """Test export orders CSV."""
        token = self._auth(db, client)
        
        response = client.get("/api/export/orders.csv",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
