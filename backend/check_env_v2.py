import os
from dotenv import load_dotenv
import psycopg2
from app.config import settings

# Force reload from .env in current directory
load_dotenv(override=True)

print("--- ENV VARS (os.environ) ---")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")
print(f"POSTGRES_PASSWORD: {os.getenv('POSTGRES_PASSWORD')}")

print("\n--- SETTINGS (pydantic) ---")
print(f"DB User: {settings.POSTGRES_USER}")
print(f"DB Password: '{settings.POSTGRES_PASSWORD}'")
print(f"DB Host: {settings.POSTGRES_HOST}")
print(f"DB Port: {settings.POSTGRES_PORT}")
print(f"Database URL: {settings.DATABASE_URL}")

print("\n--- CONNECTION TEST ---")
try:
    conn = psycopg2.connect(
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT
    )
    print("✅ Connection SUCCESSFUL!")
    conn.close()
except Exception as e:
    print(f"❌ Connection FAILED: {e}")
