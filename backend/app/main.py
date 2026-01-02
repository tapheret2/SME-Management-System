"""
FastAPI main application - Production Ready
Full SME Management System API
"""
import logging
from uuid import uuid4

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.database import get_db, engine, Base
from app.api import auth, products, stock, customers, orders, payments, reports, export, audit

logger = logging.getLogger("sme")

# Create tables on startup (dev only)
if settings.DEBUG:
    Base.metadata.create_all(bind=engine)


# P2 Fix: Request ID middleware for tracing
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


app = FastAPI(
    title=settings.APP_NAME,
    description="SME Management System API - Orders, Inventory, Customers, Suppliers, Payments, Reports",
    version="1.0.0"
)

# P2 Fix: Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# P0 Fix: CORS from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id}] Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": request_id}
    )


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(stock.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(audit.router, prefix="/api")


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
    except OperationalError:
        db_status = "disconnected"
    except Exception:
        db_status = "error"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "app_name": settings.APP_NAME
    }
