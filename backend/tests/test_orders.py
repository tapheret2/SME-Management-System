import pytest
from tests.conftest import auth_header
from app.models.customer import Customer
from app.models.product import Product


class TestOrders:
    """Test order endpoints."""
    
    @pytest.fixture
    def customer(self, db):
        """Create a test customer."""
        customer = Customer(
            code="CUST001",
            name="Test Customer",
            phone="0123456789"
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    
    @pytest.fixture
    def product(self, db):
        """Create a test product."""
        product = Product(
            sku="PROD001",
            name="Test Product",
            unit="cái",
            cost_price=100000,
            sell_price=150000,
            current_stock=100,
            min_stock=10
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    def test_create_order(self, client, admin_token, customer, product):
        """Test creating an order."""
        response = client.post("/api/orders",
            headers=auth_header(admin_token),
            json={
                "customer_id": customer.id,
                "line_items": [
                    {
                        "product_id": product.id,
                        "quantity": 2,
                        "unit_price": 150000,
                        "discount": 0
                    }
                ],
                "discount": 0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "draft"
        assert data["customer_id"] == customer.id
        assert len(data["line_items"]) == 1
        assert data["total"] == 300000
    
    def test_list_orders(self, client, admin_token):
        """Test listing orders."""
        response = client.get("/api/orders", headers=auth_header(admin_token))
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_get_order(self, client, admin_token, customer, product):
        """Test getting a specific order."""
        # Create order first
        create_response = client.post("/api/orders",
            headers=auth_header(admin_token),
            json={
                "customer_id": customer.id,
                "line_items": [
                    {
                        "product_id": product.id,
                        "quantity": 1,
                        "unit_price": 150000,
                        "discount": 0
                    }
                ],
                "discount": 0
            }
        )
        order_id = create_response.json()["id"]
        
        # Get order
        response = client.get(f"/api/orders/{order_id}", headers=auth_header(admin_token))
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
    
    def test_confirm_order_updates_stock(self, client, admin_token, customer, product, db):
        """Test confirming order deducts stock."""
        # Create order
        create_response = client.post("/api/orders",
            headers=auth_header(admin_token),
            json={
                "customer_id": customer.id,
                "line_items": [
                    {
                        "product_id": product.id,
                        "quantity": 5,
                        "unit_price": 150000,
                        "discount": 0
                    }
                ],
                "discount": 0
            }
        )
        order_id = create_response.json()["id"]
        
        # Confirm order
        response = client.put(f"/api/orders/{order_id}/status",
            headers=auth_header(admin_token),
            json={"status": "confirmed"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"
        
        # Check stock was deducted
        db.refresh(product)
        assert product.current_stock == 95  # 100 - 5
    
    def test_invalid_status_transition(self, client, admin_token, customer, product):
        """Test invalid order status transition."""
        # Create and confirm order
        create_response = client.post("/api/orders",
            headers=auth_header(admin_token),
            json={
                "customer_id": customer.id,
                "line_items": [
                    {
                        "product_id": product.id,
                        "quantity": 1,
                        "unit_price": 150000,
                        "discount": 0
                    }
                ],
                "discount": 0
            }
        )
        order_id = create_response.json()["id"]
        
        # Try to go directly from draft to completed (invalid)
        response = client.put(f"/api/orders/{order_id}/status",
            headers=auth_header(admin_token),
            json={"status": "completed"}
        )
        assert response.status_code == 400
    
    def test_cancel_order_restores_stock(self, client, admin_token, customer, product, db):
        """Test cancelling a confirmed order restores stock."""
        # Create and confirm order
        create_response = client.post("/api/orders",
            headers=auth_header(admin_token),
            json={
                "customer_id": customer.id,
                "line_items": [
                    {
                        "product_id": product.id,
                        "quantity": 10,
                        "unit_price": 150000,
                        "discount": 0
                    }
                ],
                "discount": 0
            }
        )
        order_id = create_response.json()["id"]
        
        # Confirm the order
        client.put(f"/api/orders/{order_id}/status",
            headers=auth_header(admin_token),
            json={"status": "confirmed"}
        )
        
        db.refresh(product)
        assert product.current_stock == 90  # 100 - 10
        
        # Cancel the order
        response = client.put(f"/api/orders/{order_id}/status",
            headers=auth_header(admin_token),
            json={"status": "cancelled"}
        )
        assert response.status_code == 200
        
        # Check stock was restored
        db.refresh(product)
        assert product.current_stock == 100  # Restored
