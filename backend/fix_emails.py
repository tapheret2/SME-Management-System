
from app.database import SessionLocal
from app.models.user import User

def fix_emails():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.email.like("%@sme.local")).all()
        for user in users:
            old_email = user.email
            new_email = old_email.replace(".local", ".com")
            print(f"Updating {old_email} -> {new_email}")
            user.email = new_email
        db.commit()
        print("✅ Emails updated successfully")
    except Exception as e:
        print(f"❌ Error updating emails: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_emails()
