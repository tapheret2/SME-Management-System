"""Schemas package."""
from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserResponse,
    Token, TokenRefresh, LoginRequest
)
from app.schemas.product import (
    ProductBase, ProductCreate, ProductUpdate, ProductResponse,
    ProductListResponse, LowStockProduct
)
from app.schemas.stock import (
    StockInCreate, StockOutCreate, StockAdjustCreate,
    StockMovementResponse, StockMovementListResponse
)
from app.schemas.customer import (
    CustomerBase, CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
)
from app.schemas.order import (
    OrderLineCreate, OrderLineResponse,
    OrderCreate, OrderUpdate, OrderStatusUpdate, OrderResponse, OrderListResponse
)
from app.schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentListResponse, ARAPSummary
)
from app.schemas.reports import (
    DashboardMetrics, RevenueDataPoint, RevenueReport, TopProductItem, TopProductsReport
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "Token", "TokenRefresh", "LoginRequest",
    # Product
    "ProductBase", "ProductCreate", "ProductUpdate", "ProductResponse",
    "ProductListResponse", "LowStockProduct",
    # Stock
    "StockInCreate", "StockOutCreate", "StockAdjustCreate",
    "StockMovementResponse", "StockMovementListResponse",
    # Customer
    "CustomerBase", "CustomerCreate", "CustomerUpdate", "CustomerResponse", "CustomerListResponse",
    # Order
    "OrderLineCreate", "OrderLineResponse",
    "OrderCreate", "OrderUpdate", "OrderStatusUpdate", "OrderResponse", "OrderListResponse",
    # Payment
    "PaymentCreate", "PaymentUpdate", "PaymentResponse", "PaymentListResponse", "ARAPSummary",
    # Reports
    "DashboardMetrics", "RevenueDataPoint", "RevenueReport", "TopProductItem", "TopProductsReport",
]
