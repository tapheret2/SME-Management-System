"""Report schemas."""
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    today_revenue: Decimal
    today_orders: int
    month_revenue: Decimal
    month_orders: int
    total_receivables: Decimal
    total_payables: Decimal
    debtor_count: int
    creditor_count: int
    total_customers: int
    total_products: int
    low_stock_count: int


class RevenueDataPoint(BaseModel):
    period: str
    revenue: Decimal
    order_count: int


class RevenueReport(BaseModel):
    data: list[RevenueDataPoint]
    total_revenue: Decimal
    total_orders: int


class TopProductItem(BaseModel):
    product_id: UUID
    product_sku: str
    product_name: str
    quantity_sold: int
    total_revenue: Decimal


class TopProductsReport(BaseModel):
    data: list[TopProductItem]
