"""Demo dataset loader for testing and demos."""
from decimal import Decimal
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.product import Product
from app.services.auth import hash_password


DEMO_PRODUCTS = [
    {"sku": "EL-001", "name": "LED Light Bulb 9W", "category": "Electrical", "unit": "pcs", "cost_price": 25000, "sell_price": 45000, "current_stock": 150, "min_stock": 20},
    {"sku": "EL-002", "name": "Power Strip 6-outlet", "category": "Electrical", "unit": "pcs", "cost_price": 85000, "sell_price": 150000, "current_stock": 45, "min_stock": 10},
    {"sku": "PL-001", "name": "PVC Pipe 21mm x 4m", "category": "Plumbing", "unit": "pcs", "cost_price": 35000, "sell_price": 55000, "current_stock": 80, "min_stock": 15},
    {"sku": "PL-002", "name": "Ball Valve 1/2\"", "category": "Plumbing", "unit": "pcs", "cost_price": 45000, "sell_price": 75000, "current_stock": 60, "min_stock": 10},
    {"sku": "TL-001", "name": "Screwdriver Set 6pcs", "category": "Tools", "unit": "set", "cost_price": 120000, "sell_price": 200000, "current_stock": 25, "min_stock": 5},
    {"sku": "TL-002", "name": "Measuring Tape 5m", "category": "Tools", "unit": "pcs", "cost_price": 35000, "sell_price": 60000, "current_stock": 40, "min_stock": 8},
    {"sku": "PT-001", "name": "Wall Paint White 5L", "category": "Paint", "unit": "bucket", "cost_price": 180000, "sell_price": 280000, "current_stock": 30, "min_stock": 5},
    {"sku": "HW-001", "name": "Door Lock Set", "category": "Hardware", "unit": "set", "cost_price": 250000, "sell_price": 400000, "current_stock": 15, "min_stock": 3},
]

DEMO_CUSTOMERS = [
    {"code": "KH-001", "name": "Nguyen Van A", "phone": "0901234567", "email": "nguyenvana@email.com", "address": "123 Le Loi, District 1, HCMC"},
    {"code": "KH-002", "name": "Tran Thi B", "phone": "0912345678", "address": "456 Nguyen Hue, District 1, HCMC"},
    {"code": "KH-003", "name": "Le Van C", "phone": "0923456789", "email": "levanc@email.com"},
    {"code": "KH-004", "name": "ABC Construction Co.", "phone": "0281234567", "email": "info@abcconstruction.vn", "address": "789 Vo Van Kiet, District 5, HCMC"},
]

DEMO_SUPPLIERS = [
    {"code": "NCC-001", "name": "Dien Quang Electric", "phone": "0281111111", "email": "sales@dienquang.vn"},
    {"code": "NCC-002", "name": "Binh Minh Plastics", "phone": "0282222222", "email": "order@binhminhpipe.vn"},
    {"code": "NCC-003", "name": "Nippon Paint Vietnam", "phone": "0283333333", "email": "dealer@nipponpaint.vn"},
]


def load_demo_data():
    """Load demo dataset into database."""
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Product).count() > 0:
            print("⚠️  Demo data already exists, skipping...")
            return
        
        # Create demo users
        users = [
            User(email="admin@sme.local", hashed_password=hash_password("Admin123!"), full_name="System Admin", role=UserRole.ADMIN),
            User(email="manager@sme.local", hashed_password=hash_password("Manager123!"), full_name="Store Manager", role=UserRole.MANAGER),
            User(email="staff@sme.local", hashed_password=hash_password("Staff123!"), full_name="Sales Staff", role=UserRole.STAFF),
        ]
        db.add_all(users)
        
        # Create products
        for p in DEMO_PRODUCTS:
            db.add(Product(**{k: Decimal(str(v)) if k in ["cost_price", "sell_price"] else v for k, v in p.items()}))
        
        # Create customers
        for c in DEMO_CUSTOMERS:
            db.add(Customer(**c))
        
        # Create suppliers
        for s in DEMO_SUPPLIERS:
            db.add(Supplier(**s))
        
        db.commit()
        print("✅ Demo data loaded successfully!")
        print("   Users: admin@sme.local, manager@sme.local, staff@sme.local")
        print("   Password: [Role]123! (e.g., Admin123!)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading demo data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    load_demo_data()
