"""
FastAPI main application - Milestone 3
With auth, products, and stock endpoints
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, engine, Base
from app.api import auth, products, stock

# Create tables on startup (dev only)
if settings.DEBUG:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="SME Management System API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(stock.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "SME Management System API", "version": "1.0.0"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with DB connection test."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "app_name": settings.APP_NAME
    }
