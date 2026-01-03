"""
Seed Data Script for Portfolio Demo
Run this inside the backend container to populate the database with mock data.
Usage: python seed_data.py
"""
import random
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta

from app.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import SalesOrder, SalesOrderItem, OrderStatus
from app.services.auth import hash_password

def seed():
    db = SessionLocal()
    print("🌱 Seeding data...")

    # 1. Users
    if not db.query(User).filter(User.email == "admin@demo.local").first():
        admin = User(
            id=uuid4(),
            email="admin@demo.local",
            hashed_password=hash_password("DemoAdmin123!"),
            full_name="Demo Admin",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        print(" + Created Admin User")

    # 2. Products
    products = []
    if db.query(Product).count() == 0:
        categories = ["Electronics", "Furniture", "Office Supplies"]
        for i in range(10):
            p = Product(
                id=uuid4(),
                sku=f"SKU-{1000+i}",
                name=f"Demo Product {i+1}",
                category=random.choice(categories),
                unit="pcs",
                cost_price=Decimal(random.randint(10, 50) * 10000),
                sell_price=Decimal(random.randint(60, 100) * 10000),
                current_stock=random.randint(0, 100),
                min_stock=10
            )
            products.append(p)
            db.add(p)
        print(f" + Created {len(products)} Products")

    # 3. Customers
    customers = []
    if db.query(Customer).count() == 0:
        for i in range(5):
            c = Customer(
                id=uuid4(),
                code=f"CUST-{100+i}",
                name=f"Demo Customer {i+1} Ltd",
                phone=f"090123456{i}",
                email=f"contact@customer{i}.local",
                address=f"123 Demo St, District {i+1}"
            )
            customers.append(c)
            db.add(c)
        print(f" + Created {len(customers)} Customers")
    
    db.commit()
    print("✅ Seeding complete!")
    db.close()

if __name__ == "__main__":
    seed()
