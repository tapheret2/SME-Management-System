from app.database import SessionLocal
from app.models.user import User

def verify_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Name: {user.full_name}")
            print(f"  Role: {user.role}")
            print(f"  Password Hash: {user.hashed_password[:10]}...")
            print("---")
    finally:
        db.close()

if __name__ == "__main__":
    verify_users()
