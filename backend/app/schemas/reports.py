from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class RevenueData(BaseModel):
    period: str  # date string or week/month identifier
    revenue: Decimal
    order_count: int


class RevenueReport(BaseModel):
    data: list[RevenueData]
    total_revenue: Decimal
    total_orders: int
    period_type: str  # "day", "week", "month"


class TopProduct(BaseModel):
    product_id: int
    product_sku: str
    product_name: str
    total_quantity: int
    total_revenue: Decimal


class TopProductsReport(BaseModel):
    data: list[TopProduct]
    period_start: date
    period_end: date


class InventoryValuation(BaseModel):
    product_id: int
    product_sku: str
    product_name: str
    current_stock: int
    cost_price: Decimal
    total_value: Decimal


class InventoryValuationReport(BaseModel):
    data: list[InventoryValuation]
    total_value: Decimal


class ARAPSummary(BaseModel):
    total_receivables: Decimal  # Money customers owe us
    total_payables: Decimal     # Money we owe suppliers
    net_position: Decimal       # receivables - payables
    customer_count: int
    supplier_count: int


class DashboardMetrics(BaseModel):
    today_revenue: Decimal
    today_orders: int
    month_revenue: Decimal
    month_orders: int
    total_customers: int
    total_products: int
    low_stock_count: int
    total_receivables: Decimal
    total_payables: Decimal
