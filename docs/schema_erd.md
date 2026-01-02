# PostgreSQL Schema - ERD & Migration Plan

## ERD Description

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : creates
    USERS ||--o{ SALES_ORDERS : creates
    USERS ||--o{ PAYMENTS : creates
    USERS ||--o{ STOCK_MOVEMENTS : creates
    
    USERS {
        uuid id PK
        varchar email UK
        varchar hashed_password
        varchar full_name
        enum role "admin|manager|staff"
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    CUSTOMERS ||--o{ SALES_ORDERS : places
    CUSTOMERS ||--o{ PAYMENTS : receives
    
    CUSTOMERS {
        uuid id PK
        varchar code UK
        varchar name
        varchar phone
        varchar email
        text address
        text notes
        numeric total_debt
        timestamp created_at
        timestamp updated_at
    }
    
    SUPPLIERS ||--o{ STOCK_MOVEMENTS : supplies
    SUPPLIERS ||--o{ PAYMENTS : pays
    
    SUPPLIERS {
        uuid id PK
        varchar code UK
        varchar name
        varchar phone
        varchar email
        text address
        text notes
        numeric total_payable
        timestamp created_at
        timestamp updated_at
    }
    
    PRODUCTS ||--o{ SALES_ORDER_ITEMS : contains
    PRODUCTS ||--o{ STOCK_MOVEMENTS : tracks
    
    PRODUCTS {
        uuid id PK
        varchar sku UK
        varchar name
        varchar category
        varchar unit
        numeric cost_price
        numeric sell_price
        int current_stock
        int min_stock
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    SALES_ORDERS ||--|{ SALES_ORDER_ITEMS : has
    SALES_ORDERS ||--o{ PAYMENTS : settles
    SALES_ORDERS ||--o{ STOCK_MOVEMENTS : triggers
    
    SALES_ORDERS {
        uuid id PK
        varchar order_number UK
        uuid customer_id FK
        uuid created_by FK
        enum status "draft|confirmed|shipped|completed|cancelled"
        numeric subtotal
        numeric discount
        numeric total
        numeric paid_amount
        text notes
        timestamp order_date
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at "soft delete"
    }
    
    SALES_ORDER_ITEMS {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        numeric unit_price
        numeric discount
        numeric line_total
        timestamp created_at
        timestamp updated_at
    }
    
    STOCK_MOVEMENTS {
        uuid id PK
        uuid product_id FK
        uuid supplier_id FK
        uuid order_id FK
        uuid created_by FK
        enum type "in|out|adjust"
        int quantity
        int stock_before
        int stock_after
        text reason
        timestamp created_at
    }
    
    PAYMENTS {
        uuid id PK
        varchar payment_number UK
        enum type "incoming|outgoing"
        enum method "cash|bank|other"
        uuid customer_id FK
        uuid supplier_id FK
        uuid order_id FK
        uuid created_by FK
        numeric amount
        text notes
        timestamp payment_date
        timestamp created_at
        timestamp updated_at
    }
    
    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        varchar entity_type
        uuid entity_id
        varchar action
        jsonb old_values
        jsonb new_values
        timestamp created_at
    }
```

---

## Key Changes from Current Schema

| Aspect | Before | After |
|--------|--------|-------|
| Primary Keys | Integer (auto-increment) | UUID v4 |
| Timestamps | created_at only on some | created_at/updated_at everywhere |
| Soft Delete | None | deleted_at on sales_orders |
| Indexes | Basic | Optimized for common queries |

---

## Index Strategy

### Performance Indexes

```sql
-- Orders: filter by date range, status, customer
CREATE INDEX idx_sales_orders_order_date ON sales_orders(order_date);
CREATE INDEX idx_sales_orders_status ON sales_orders(status);
CREATE INDEX idx_sales_orders_customer_id ON sales_orders(customer_id);
CREATE INDEX idx_sales_orders_deleted_at ON sales_orders(deleted_at) WHERE deleted_at IS NULL;

-- Order Items: lookup by order and product
CREATE INDEX idx_order_items_order_id ON sales_order_items(order_id);
CREATE INDEX idx_order_items_product_id ON sales_order_items(product_id);

-- Products: search and filter
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_is_active ON products(is_active);

-- Stock Movements: filter by product, type, date
CREATE INDEX idx_stock_movements_product_id ON stock_movements(product_id);
CREATE INDEX idx_stock_movements_created_at ON stock_movements(created_at);

-- Payments: filter by date, type, entities
CREATE INDEX idx_payments_payment_date ON payments(payment_date);
CREATE INDEX idx_payments_type ON payments(type);
CREATE INDEX idx_payments_customer_id ON payments(customer_id);
CREATE INDEX idx_payments_supplier_id ON payments(supplier_id);

-- Audit Logs: filter by entity and date
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

---

## Alembic Migration Plan

### Migration: `001_uuid_schema`

1. **Create UUID extension**
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```

2. **Drop all existing tables** (fresh start for MVP)

3. **Create new tables with UUID PKs**
   - All PKs use `UUID DEFAULT uuid_generate_v4()`
   - All FKs reference UUID columns
   - Add `created_at`, `updated_at` to all tables
   - Add `deleted_at` to `sales_orders` only

4. **Create indexes** as listed above

5. **Seed initial data** (users, demo data)

---

## SQLAlchemy Model Changes

### Base Mixin for UUID + Timestamps

```python
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class UUIDMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class SoftDeleteMixin:
    deleted_at = Column(DateTime(timezone=True), nullable=True)
```

### Models to Update
- `User` - UUID + Timestamps
- `Customer` - UUID + Timestamps
- `Supplier` - UUID + Timestamps
- `Product` - UUID + Timestamps
- `SalesOrder` - UUID + Timestamps + SoftDelete
- `SalesOrderItem` (renamed from OrderLine) - UUID + Timestamps
- `StockMovement` - UUID + created_at only
- `Payment` - UUID + Timestamps
- `AuditLog` - UUID + created_at only
