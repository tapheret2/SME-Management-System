"""
Seed script to create demo data for testing.
Run with: python -m app.seed
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.product import Product
from app.services.auth import hash_password

# Create tables
Base.metadata.create_all(bind=engine)


def seed_users(db: Session):
    """Create demo users."""
    users = [
        {"email": "admin@sme.local", "password": "Admin123!", "full_name": "Quản trị viên", "role": UserRole.ADMIN},
        {"email": "manager@sme.local", "password": "Manager123!", "full_name": "Quản lý", "role": UserRole.MANAGER},
        {"email": "staff@sme.local", "password": "Staff123!", "full_name": "Nhân viên", "role": UserRole.STAFF},
    ]
    
    for user_data in users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"]
            )
            db.add(user)
            print(f"Created user: {user_data['email']}")
    
    db.commit()


def seed_customers(db: Session):
    """Create demo customers."""
    customers = [
        {"code": "KH001", "name": "Công ty ABC", "phone": "0901234567", "email": "abc@email.com", "address": "123 Nguyễn Huệ, Q1, TP.HCM"},
        {"code": "KH002", "name": "Cửa hàng XYZ", "phone": "0912345678", "email": "xyz@email.com", "address": "456 Lê Lợi, Q1, TP.HCM"},
        {"code": "KH003", "name": "Anh Minh", "phone": "0923456789", "address": "789 Trần Hưng Đạo, Q5, TP.HCM"},
        {"code": "KH004", "name": "Chị Lan", "phone": "0934567890", "address": "101 Cách Mạng Tháng 8, Q3, TP.HCM"},
        {"code": "KH005", "name": "Công ty DEF", "phone": "0945678901", "email": "def@email.com", "address": "202 Hai Bà Trưng, Q1, TP.HCM"},
    ]
    
    for data in customers:
        existing = db.query(Customer).filter(Customer.code == data["code"]).first()
        if not existing:
            customer = Customer(**data)
            db.add(customer)
            print(f"Created customer: {data['code']}")
    
    db.commit()


def seed_suppliers(db: Session):
    """Create demo suppliers."""
    suppliers = [
        {"code": "NCC001", "name": "Nhà cung cấp A", "phone": "02838123456", "email": "ncc-a@email.com", "address": "Khu CN Tân Bình, TP.HCM"},
        {"code": "NCC002", "name": "Nhà cung cấp B", "phone": "02838234567", "email": "ncc-b@email.com", "address": "Khu CN Biên Hòa, Đồng Nai"},
        {"code": "NCC003", "name": "Công ty vật tư C", "phone": "02838345678", "address": "Q.Thủ Đức, TP.HCM"},
    ]
    
    for data in suppliers:
        existing = db.query(Supplier).filter(Supplier.code == data["code"]).first()
        if not existing:
            supplier = Supplier(**data)
            db.add(supplier)
            print(f"Created supplier: {data['code']}")
    
    db.commit()


def seed_products(db: Session):
    """Create demo products."""
    products = [
        {"sku": "SP001", "name": "Laptop Dell Inspiron 15", "category": "Máy tính", "unit": "cái", "cost_price": 15000000, "sell_price": 18000000, "current_stock": 25, "min_stock": 5},
        {"sku": "SP002", "name": "Chuột Logitech MX Master", "category": "Phụ kiện", "unit": "cái", "cost_price": 1500000, "sell_price": 2000000, "current_stock": 50, "min_stock": 10},
        {"sku": "SP003", "name": "Bàn phím cơ Keychron K2", "category": "Phụ kiện", "unit": "cái", "cost_price": 1800000, "sell_price": 2500000, "current_stock": 30, "min_stock": 5},
        {"sku": "SP004", "name": "Màn hình Dell 27 inch", "category": "Màn hình", "unit": "cái", "cost_price": 5000000, "sell_price": 6500000, "current_stock": 15, "min_stock": 3},
        {"sku": "SP005", "name": "USB Type-C Hub", "category": "Phụ kiện", "unit": "cái", "cost_price": 300000, "sell_price": 450000, "current_stock": 100, "min_stock": 20},
        {"sku": "SP006", "name": "Tai nghe Sony WH-1000XM4", "category": "Âm thanh", "unit": "cái", "cost_price": 5500000, "sell_price": 7000000, "current_stock": 8, "min_stock": 5},
        {"sku": "SP007", "name": "Ổ cứng SSD 1TB Samsung", "category": "Linh kiện", "unit": "cái", "cost_price": 2000000, "sell_price": 2800000, "current_stock": 40, "min_stock": 10},
        {"sku": "SP008", "name": "RAM DDR4 16GB", "category": "Linh kiện", "unit": "thanh", "cost_price": 800000, "sell_price": 1200000, "current_stock": 60, "min_stock": 15},
        {"sku": "SP009", "name": "Webcam Logitech C920", "category": "Phụ kiện", "unit": "cái", "cost_price": 1200000, "sell_price": 1800000, "current_stock": 3, "min_stock": 5},
        {"sku": "SP010", "name": "Dây cáp HDMI 2m", "category": "Phụ kiện", "unit": "sợi", "cost_price": 50000, "sell_price": 100000, "current_stock": 200, "min_stock": 50},
    ]
    
    for data in products:
        existing = db.query(Product).filter(Product.sku == data["sku"]).first()
        if not existing:
            product = Product(**data)
            db.add(product)
            print(f"Created product: {data['sku']}")
    
    db.commit()


def main():
    """Run all seed functions."""
    print("Starting database seed...")
    db = SessionLocal()
    
    try:
        seed_users(db)
        seed_customers(db)
        seed_suppliers(db)
        seed_products(db)
        print("\n✅ Database seeded successfully!")
        print("\nDemo accounts:")
        print("  Admin:   admin@sme.local / Admin123!")
        print("  Manager: manager@sme.local / Manager123!")
        print("  Staff:   staff@sme.local / Staff123!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
