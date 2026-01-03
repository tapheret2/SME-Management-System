from app.config import settings
print(f"DB User: {settings.POSTGRES_USER}")
print(f"DB Password: '{settings.POSTGRES_PASSWORD}'")
print(f"DB Host: {settings.POSTGRES_HOST}")
