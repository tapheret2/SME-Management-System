from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api import auth, users, customers, suppliers, products, orders, payments, stock, reports
from app.utils.csv_export import router as export_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create tables if they don't exist (for development)
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title=settings.APP_NAME,
    description="Internal web application for Vietnamese SMEs to manage Orders, Inventory, Customers, Suppliers, Payments, and Reports.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(suppliers.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(stock.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(export_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "SME Management System API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
