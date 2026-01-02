from app.database import SessionLocal
from app.models.user import User, UserRole
from app.services.auth import hash_password

def create_missing_users():
    db = SessionLocal()
    try:
        users_to_create = [
            {"email": "manager@sme.com", "password": "Manager123!", "name": "Store Manager", "role": UserRole.MANAGER},
            {"email": "staff@sme.com", "password": "Staff123!", "name": "Sales Staff", "role": UserRole.STAFF},
        ]
        
        for u in users_to_create:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                print(f"Creating user: {u['email']}")
                new_user = User(
                    email=u["email"],
                    hashed_password=hash_password(u["password"]),
                    full_name=u["name"],
                    role=u["role"]
                )
                db.add(new_user)
            else:
                print(f"User {u['email']} already exists.")
        
        db.commit()
        print("✅ Missing users created successfully")
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_missing_users()
