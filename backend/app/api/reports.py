"""Reports API endpoints."""
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Product
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.order import SalesOrder, SalesOrderItem, OrderStatus
from app.models.stock import StockMovement, MovementType
from app.schemas.reports import DashboardMetrics, RevenueDataPoint, RevenueReport, TopProductItem, TopProductsReport
from app.api.deps import get_current_user


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get dashboard metrics."""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    # Today's metrics
    today_orders = db.query(SalesOrder).filter(
        func.date(SalesOrder.order_date) == today,
        SalesOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.COMPLETED]),
        SalesOrder.deleted_at == None
    ).all()
    
    # Doanh thu = Tổng tiền chốt (Gross sales)
    today_revenue = sum(o.total for o in today_orders) or Decimal("0")
    # Tiền nợ mới = Tổng nợ từ đơn hàng
    today_debt = sum(o.remaining_amount for o in today_orders) or Decimal("0")
    # Thực thu = Số tiền khách đã trả
    today_collected = sum(o.paid_amount for o in today_orders) or Decimal("0")
    today_count = len(today_orders)
    
    today_profit = Decimal("0")
    for order in today_orders:
        for item in order.line_items:
            today_profit += (item.line_total - (item.cost_price * item.quantity))

    # Month metrics
    month_orders = db.query(SalesOrder).filter(
        func.date(SalesOrder.order_date) >= month_start,
        SalesOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.COMPLETED]),
        SalesOrder.deleted_at == None
    ).all()
    
    month_revenue = sum(o.total for o in month_orders) or Decimal("0")
    month_debt = sum(o.remaining_amount for o in month_orders) or Decimal("0")
    month_collected = sum(o.paid_amount for o in month_orders) or Decimal("0")
    month_count = len(month_orders)
    
    month_profit = Decimal("0")
    for order in month_orders:
        for item in order.line_items:
            month_profit += (item.line_total - (item.cost_price * item.quantity))

    # Receivables/Payables (Cross-entity) - Return as Absolute for UI
    c_receivables = db.query(func.coalesce(func.sum(Customer.total_debt), 0)).filter(Customer.total_debt < 0).scalar()
    s_receivables = db.query(func.coalesce(func.sum(Supplier.total_payable), 0)).filter(Supplier.total_payable < 0).scalar()
    total_receivables = abs(Decimal(str(c_receivables or 0)) + Decimal(str(s_receivables or 0)))
    debtor_count = db.query(Customer).filter(Customer.total_debt < 0).count() + db.query(Supplier).filter(Supplier.total_payable < 0).count()
    
    s_payables = db.query(func.coalesce(func.sum(Supplier.total_payable), 0)).filter(Supplier.total_payable > 0).scalar()
    c_payables = db.query(func.coalesce(func.sum(Customer.total_debt), 0)).filter(Customer.total_debt > 0).scalar()
    total_payables = abs(Decimal(str(s_payables or 0)) + Decimal(str(c_payables or 0)))
    creditor_count = db.query(Supplier).filter(Supplier.total_payable > 0).count() + db.query(Customer).filter(Customer.total_debt > 0).count()
    
    # Month Import Cost (Stock IN movements × cost_price)
    from sqlalchemy.orm import joinedload
    month_imports = db.query(StockMovement).filter(
        func.date(StockMovement.created_at) >= month_start,
        StockMovement.type == MovementType.IN
    ).all()
    
    month_import_cost = Decimal("0")
    for movement in month_imports:
        product = db.query(Product).filter(Product.id == movement.product_id).first()
        if product:
            month_import_cost += product.cost_price * movement.quantity

    # Counts
    total_customers = db.query(Customer).count()
    total_products = db.query(Product).filter(Product.is_active == True).count()
    low_stock = db.query(Product).filter(
        Product.is_active == True,
        Product.current_stock <= Product.min_stock
    ).count()
    
    return DashboardMetrics(
        today_revenue=today_revenue,
        today_collected=today_collected,
        today_debt=today_debt,
        today_profit=today_profit,
        today_count=today_count,
        month_revenue=month_revenue,
        month_collected=month_collected,
        month_debt=month_debt,
        month_profit=month_profit,
        month_count=month_count,
        month_import_cost=month_import_cost,
        total_receivables=total_receivables,
        total_payables=total_payables,
        debtor_count=debtor_count,
        creditor_count=creditor_count,
        total_customers=total_customers,
        total_products=total_products,
        low_stock_count=low_stock
    )


@router.get("/revenue", response_model=RevenueReport)
def get_revenue_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get revenue report by day."""
    start_date = datetime.now().date() - timedelta(days=days)
    
    orders = db.query(SalesOrder).filter(
        func.date(SalesOrder.order_date) >= start_date,
        SalesOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.COMPLETED]),
        SalesOrder.deleted_at == None
    ).all()
    
    # Group by date
    daily_data = {}
    for order in orders:
        date_str = order.order_date.strftime("%Y-%m-%d")
        if date_str not in daily_data:
            daily_data[date_str] = {"revenue": Decimal("0"), "count": 0}
        daily_data[date_str]["revenue"] += order.total
        daily_data[date_str]["count"] += 1
    
    data = [
        RevenueDataPoint(period=date, revenue=vals["revenue"], order_count=vals["count"])
        for date, vals in sorted(daily_data.items())
    ]
    
    total_revenue = sum(d.revenue for d in data)
    total_orders = sum(d.order_count for d in data)
    
    return RevenueReport(data=data, total_revenue=total_revenue, total_orders=total_orders)


@router.get("/top-products", response_model=TopProductsReport)
def get_top_products(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get top selling products."""
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Get completed orders in date range
    subquery = db.query(SalesOrder.id).filter(
        func.date(SalesOrder.order_date) >= start_date,
        SalesOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.COMPLETED]),
        SalesOrder.deleted_at == None
    ).subquery()
    
    # Aggregate by product
    results = db.query(
        Product.id,
        Product.sku,
        Product.name,
        func.sum(SalesOrderItem.quantity).label("qty_sold"),
        func.sum(SalesOrderItem.line_total).label("revenue")
    ).join(SalesOrderItem, SalesOrderItem.product_id == Product.id
    ).filter(SalesOrderItem.order_id.in_(subquery)
    ).group_by(Product.id, Product.sku, Product.name
    ).order_by(func.sum(SalesOrderItem.quantity).desc()
    ).limit(limit).all()
    
    data = [
        TopProductItem(
            product_id=r[0],
            product_sku=r[1],
            product_name=r[2],
            quantity_sold=r[3] or 0,
            total_revenue=Decimal(str(r[4] or 0))
        )
        for r in results
    ]
    
    return TopProductsReport(data=data)


@router.get("/inventory-valuation")
def get_inventory_valuation(
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get inventory valuation (stock × cost_price for each product)."""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.current_stock > 0
    ).order_by(Product.current_stock.desc()).all()
    
    data = []
    total_value = Decimal("0")
    
    for p in products:
        item_value = p.cost_price * p.current_stock
        total_value += item_value
        data.append({
            "product_id": str(p.id),
            "product_sku": p.sku,
            "product_name": p.name,
            "current_stock": p.current_stock,
            "cost_price": p.cost_price,
            "total_value": item_value
        })
    
    return {
        "data": data,
        "total_value": total_value
    }
