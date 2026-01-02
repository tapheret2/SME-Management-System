"""
Seed script - create initial admin user.
Run: python -m app.seed
"""
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.services.auth import hash_password


def seed():
    """Create initial admin user."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@sme.local").first()
        if admin:
            print("Admin user already exists")
            return
        
        # Create admin
        admin = User(
            email="admin@sme.local",
            hashed_password=hash_password("Admin123!"),
            full_name="Quản trị viên",
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
        print("✅ Created admin user: admin@sme.local / Admin123!")
        
    finally:
        db.close()


if __name__ == "__main__":
    seed()
