from fastapi import APIRouter, Query
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, extract
from typing import Optional

from app.api.deps import DBSession, CurrentUser
from app.models.order import SalesOrder, OrderStatus
from app.models.product import Product
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.schemas.reports import (
    RevenueReport, RevenueData,
    TopProductsReport, TopProduct,
    InventoryValuationReport, InventoryValuation,
    ARAPSummary, DashboardMetrics
)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(db: DBSession, current_user: CurrentUser):
    """
    Get dashboard summary metrics.
    """
    today = date.today()
    month_start = today.replace(day=1)
    
    # Today's revenue and orders
    today_orders = db.query(SalesOrder).filter(
        func.date(SalesOrder.order_date) == today,
        SalesOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.COMPLETED])
    ).all()
    today_revenue = sum(o.total for o in today_orders)
    
    # Month's revenue and orders
    month_orders = db.query(SalesOrder).filter(
        SalesOrder.order_date >= month_start,
        SalesOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.COMPLETED])
    ).all()
    month_revenue = sum(o.total for o in month_orders)
    
    # Counts
    total_customers = db.query(Customer).count()
    total_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Low stock count
    low_stock_count = db.query(Product).filter(
        Product.is_active == True,
        Product.current_stock <= Product.min_stock
    ).count()
    
    # Receivables and payables
    total_receivables = db.query(func.coalesce(func.sum(Customer.total_debt), 0)).scalar()
    total_payables = db.query(func.coalesce(func.sum(Supplier.total_payable), 0)).scalar()
    
    return DashboardMetrics(
        today_revenue=Decimal(today_revenue or 0),
        today_orders=len(today_orders),
        month_revenue=Decimal(month_revenue or 0),
        month_orders=len(month_orders),
        total_customers=total_customers,
        total_products=total_products,
        low_stock_count=low_stock_count,
        total_receivables=Decimal(total_receivables or 0),
        total_payables=Decimal(total_payables or 0)
    )


@router.get("/revenue", response_model=RevenueReport)
async def get_revenue_report(
    db: DBSession,
    current_user: CurrentUser,
    period: str = Query("day", regex="^(day|week|month)$"),
    days: int = Query(30, ge=1, le=365)
):
    """
    Get revenue report by period (day/week/month).
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    orders = db.query(SalesOrder).filter(
        SalesOrder.order_date >= start_date,
        SalesOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.COMPLETED])
    ).all()
    
    # Group by period
    data_dict = {}
    for order in orders:
        order_date = order.order_date.date() if isinstance(order.order_date, datetime) else order.order_date
        
        if period == "day":
            key = order_date.isoformat()
        elif period == "week":
            # ISO week
            key = f"{order_date.isocalendar()[0]}-W{order_date.isocalendar()[1]:02d}"
        else:  # month
            key = f"{order_date.year}-{order_date.month:02d}"
        
        if key not in data_dict:
            data_dict[key] = {"revenue": Decimal(0), "count": 0}
        
        data_dict[key]["revenue"] += order.total
        data_dict[key]["count"] += 1
    
    # Convert to list
    data = [
        RevenueData(period=k, revenue=v["revenue"], order_count=v["count"])
        for k, v in sorted(data_dict.items())
    ]
    
    total_revenue = sum(d.revenue for d in data)
    total_orders = sum(d.order_count for d in data)
    
    return RevenueReport(
        data=data,
        total_revenue=total_revenue,
        total_orders=total_orders,
        period_type=period
    )


@router.get("/top-products", response_model=TopProductsReport)
async def get_top_products(
    db: DBSession,
    current_user: CurrentUser,
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get top selling products by revenue.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get completed orders in date range
    orders = db.query(SalesOrder).filter(
        SalesOrder.order_date >= start_date,
        SalesOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.COMPLETED])
    ).all()
    
    # Aggregate by product
    product_data = {}
    for order in orders:
        for line in order.line_items:
            if line.product_id not in product_data:
                product = db.query(Product).filter(Product.id == line.product_id).first()
                product_data[line.product_id] = {
                    "product_sku": product.sku if product else "N/A",
                    "product_name": product.name if product else "Unknown",
                    "total_quantity": 0,
                    "total_revenue": Decimal(0)
                }
            
            product_data[line.product_id]["total_quantity"] += line.quantity
            product_data[line.product_id]["total_revenue"] += line.line_total
    
    # Sort by revenue and take top N
    sorted_products = sorted(
        product_data.items(),
        key=lambda x: x[1]["total_revenue"],
        reverse=True
    )[:limit]
    
    data = [
        TopProduct(
            product_id=pid,
            product_sku=pdata["product_sku"],
            product_name=pdata["product_name"],
            total_quantity=pdata["total_quantity"],
            total_revenue=pdata["total_revenue"]
        )
        for pid, pdata in sorted_products
    ]
    
    return TopProductsReport(
        data=data,
        period_start=start_date,
        period_end=end_date
    )


@router.get("/inventory-valuation", response_model=InventoryValuationReport)
async def get_inventory_valuation(db: DBSession, current_user: CurrentUser):
    """
    Get inventory valuation report (cost-based).
    """
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.current_stock > 0
    ).all()
    
    data = []
    total_value = Decimal(0)
    
    for product in products:
        value = Decimal(product.current_stock) * product.cost_price
        data.append(InventoryValuation(
            product_id=product.id,
            product_sku=product.sku,
            product_name=product.name,
            current_stock=product.current_stock,
            cost_price=product.cost_price,
            total_value=value
        ))
        total_value += value
    
    return InventoryValuationReport(data=data, total_value=total_value)


@router.get("/ar-ap-summary", response_model=ARAPSummary)
async def get_ar_ap_summary(db: DBSession, current_user: CurrentUser):
    """
    Get accounts receivable and payable summary.
    """
    # Receivables (customers owe us)
    total_receivables = db.query(func.coalesce(func.sum(Customer.total_debt), 0)).scalar()
    customer_count = db.query(Customer).filter(Customer.total_debt > 0).count()
    
    # Payables (we owe suppliers)
    total_payables = db.query(func.coalesce(func.sum(Supplier.total_payable), 0)).scalar()
    supplier_count = db.query(Supplier).filter(Supplier.total_payable > 0).count()
    
    return ARAPSummary(
        total_receivables=Decimal(total_receivables or 0),
        total_payables=Decimal(total_payables or 0),
        net_position=Decimal(total_receivables or 0) - Decimal(total_payables or 0),
        customer_count=customer_count,
        supplier_count=supplier_count
    )
