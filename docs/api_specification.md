# SME Backend API - OpenAPI Route Specification

Base URL: `/api`

---

## Authentication

### POST /auth/register
**Admin only** - Create new user account

```json
// Request
{
  "email": "staff@sme.local",
  "password": "SecurePass123!",
  "full_name": "Nhân viên mới",
  "role": "staff"  // "admin" | "manager" | "staff"
}

// Response 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "staff@sme.local",
  "full_name": "Nhân viên mới",
  "role": "staff",
  "is_active": true,
  "created_at": "2026-01-02T16:30:00+07:00",
  "updated_at": "2026-01-02T16:30:00+07:00"
}
```
| Status | Description |
|--------|-------------|
| 201 | User created |
| 400 | Email already exists |
| 401 | Not authenticated |
| 403 | Not admin |

---

### POST /auth/login
**Public** - Authenticate and get tokens

```json
// Request
{
  "email": "admin@sme.local",
  "password": "Admin123!"
}

// Response 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```
| Status | Description |
|--------|-------------|
| 200 | Login successful |
| 401 | Invalid credentials |

---

### POST /auth/refresh
**Public** - Refresh access token

```json
// Request
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

// Response 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```
| Status | Description |
|--------|-------------|
| 200 | Tokens refreshed |
| 401 | Invalid/expired refresh token |

---

### GET /auth/me
**Authenticated** - Get current user info

```json
// Response 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@sme.local",
  "full_name": "Quản trị viên",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-01-01T00:00:00+07:00",
  "updated_at": "2026-01-01T00:00:00+07:00"
}
```

---

### POST /auth/logout
**Authenticated** - Invalidate refresh token

```json
// Response 200 OK
{ "message": "Logged out successfully" }
```

---

## Users (Admin only)

### GET /users
List all users with pagination

```
GET /users?page=1&size=20&search=admin
```

```json
// Response 200 OK
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "admin@sme.local",
      "full_name": "Quản trị viên",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-01-01T00:00:00+07:00",
      "updated_at": "2026-01-01T00:00:00+07:00"
    }
  ],
  "total": 1
}
```

### GET /users/{id}
Get single user by UUID

### PUT /users/{id}
Update user (partial update supported)

### DELETE /users/{id}
Deactivate user (soft delete via `is_active=false`)

---

### GET /roles
List available roles

```json
// Response 200 OK
[
  { "value": "admin", "label": "Quản trị viên" },
  { "value": "manager", "label": "Quản lý" },
  { "value": "staff", "label": "Nhân viên" }
]
```

---

## Products

### GET /products
List products with filtering

```
GET /products?page=1&size=20&search=laptop&category=Máy tính&active_only=true
```

```json
// Response 200 OK
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "sku": "SP001",
      "name": "Laptop Dell Inspiron 15",
      "category": "Máy tính",
      "unit": "cái",
      "cost_price": 15000000,
      "sell_price": 18000000,
      "current_stock": 25,
      "min_stock": 5,
      "is_active": true,
      "is_low_stock": false,
      "created_at": "2026-01-01T00:00:00+07:00",
      "updated_at": "2026-01-01T00:00:00+07:00"
    }
  ],
  "total": 1
}
```

### POST /products
Create product

```json
// Request
{
  "sku": "SP011",
  "name": "Bàn làm việc",
  "category": "Nội thất",
  "unit": "cái",
  "cost_price": 2000000,
  "sell_price": 3000000,
  "current_stock": 10,
  "min_stock": 2
}

// Response 201 Created
{ "id": "...", "sku": "SP011", ... }
```

### GET /products/{id}
### PUT /products/{id}
### DELETE /products/{id}

---

### GET /inventory/low-stock
**Alias**: GET /products/low-stock

```json
// Response 200 OK
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440009",
    "sku": "SP009",
    "name": "Webcam Logitech C920",
    "current_stock": 3,
    "min_stock": 5
  }
]
```

---

## Orders

### GET /orders
List orders with filtering

```
GET /orders?page=1&size=20&status=confirmed&customer_id=UUID&from_date=2026-01-01&to_date=2026-01-31
```

### POST /orders
Create order with line items

```json
// Request
{
  "customer_id": "550e8400-e29b-41d4-a716-446655440010",
  "line_items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440001",
      "quantity": 2,
      "unit_price": 18000000,
      "discount": 0
    }
  ],
  "discount": 500000,
  "notes": "Giao hàng trước 5PM"
}

// Response 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440020",
  "order_number": "SO-20260102-001",
  "status": "draft",
  "subtotal": 36000000,
  "discount": 500000,
  "total": 35500000,
  "paid_amount": 0,
  "remaining_amount": 35500000,
  "line_items": [...]
}
```

### GET /orders/{id}
### PUT /orders/{id}
### DELETE /orders/{id}

---

### GET /orders/{id}/items
Get order line items

### POST /orders/{id}/items
Add line item to order

### PUT /orders/{id}/items/{item_id}
Update line item

### DELETE /orders/{id}/items/{item_id}
Remove line item

---

### PUT /orders/{id}/status
Update order status (with workflow validation)

```json
// Request
{ "status": "confirmed" }

// Response 200 OK
{
  "id": "...",
  "status": "confirmed",
  ...
}
```

| Status | Description |
|--------|-------------|
| 200 | Status updated |
| 400 | Invalid status transition |
| 404 | Order not found |

**Valid transitions:**
- draft → confirmed, cancelled
- confirmed → shipped, cancelled
- shipped → completed
- completed → (none)
- cancelled → (none)

---

## Payments

### GET /payments
List payments

```
GET /payments?page=1&size=20&type=incoming&customer_id=UUID
```

### POST /payments
Create payment

```json
// Request
{
  "type": "incoming",
  "method": "bank",
  "customer_id": "550e8400-e29b-41d4-a716-446655440010",
  "order_id": "550e8400-e29b-41d4-a716-446655440020",
  "amount": 10000000,
  "notes": "Thanh toán đợt 1"
}

// Response 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440030",
  "payment_number": "PAY-20260102-001",
  "type": "incoming",
  "method": "bank",
  "amount": 10000000,
  ...
}
```

### GET /payments/{id}
### PUT /payments/{id}
### DELETE /payments/{id}

---

### GET /payments/receivables
**Alias**: GET /reports/ar-ap → Accounts Receivable

```json
// Response 200 OK
{
  "items": [
    {
      "entity_id": "550e8400-e29b-41d4-a716-446655440010",
      "entity_code": "KH001",
      "entity_name": "Công ty ABC",
      "total_amount": 50000000,
      "paid_amount": 20000000,
      "remaining_amount": 30000000
    }
  ],
  "total_receivables": 30000000
}
```

### GET /payments/payables
Accounts Payable (same structure, for suppliers)

---

## Reports

### GET /reports/dashboard
Dashboard metrics

```json
// Response 200 OK
{
  "today_revenue": 15000000,
  "today_orders": 5,
  "month_revenue": 450000000,
  "month_orders": 120,
  "total_receivables": 80000000,
  "total_payables": 25000000,
  "total_customers": 45,
  "total_products": 150,
  "low_stock_count": 3
}
```

---

### GET /reports/revenue
Revenue report by period

```
GET /reports/revenue?period=day&days=30
```

```json
// Response 200 OK
{
  "data": [
    { "period": "2026-01-01", "revenue": 12000000, "order_count": 4 },
    { "period": "2026-01-02", "revenue": 15000000, "order_count": 5 }
  ],
  "total_revenue": 27000000,
  "total_orders": 9
}
```

**Parameters:**
- `period`: `day` | `week` | `month`
- `days`: Number of days to look back (default: 30)

---

### GET /reports/top-products
Top selling products

```
GET /reports/top-products?days=30&limit=10
```

```json
// Response 200 OK
{
  "data": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440001",
      "product_sku": "SP001",
      "product_name": "Laptop Dell Inspiron 15",
      "quantity_sold": 25,
      "total_revenue": 450000000
    }
  ]
}
```

---

### GET /reports/inventory-valuation
Inventory value by product

```json
// Response 200 OK
{
  "data": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440001",
      "product_sku": "SP001",
      "product_name": "Laptop Dell Inspiron 15",
      "current_stock": 25,
      "cost_price": 15000000,
      "total_value": 375000000
    }
  ],
  "total_value": 1250000000
}
```

---

### GET /reports/ar-ap-summary
Combined AR/AP summary

```json
// Response 200 OK
{
  "total_receivables": 80000000,
  "customer_count": 15,
  "total_payables": 25000000,
  "supplier_count": 5
}
```

---

## Export

### GET /export/orders.csv
Export orders to CSV

```
GET /export/orders.csv?status=completed&from_date=2026-01-01
```
Response: `text/csv` file download

---

### GET /export/inventory.csv
**Alias**: GET /export/products

Export products/inventory to CSV

Response: `text/csv` file download

---

### GET /export/payments.csv
Export payments to CSV

```
GET /export/payments.csv?type=incoming&from_date=2026-01-01
```

---

## Stock Movements

### GET /stock
List stock movements

### POST /stock/in
Stock in (receiving)

```json
// Request
{
  "product_id": "550e8400-e29b-41d4-a716-446655440001",
  "quantity": 10,
  "supplier_id": "550e8400-e29b-41d4-a716-446655440050",
  "reason": "Nhập hàng từ NCC"
}
```

### POST /stock/out
Stock out (manual)

### POST /stock/adjust
Stock adjustment

```json
// Request
{
  "product_id": "550e8400-e29b-41d4-a716-446655440001",
  "quantity": -2,  // Negative for decrease
  "reason": "Kiểm kê phát hiện thiếu"
}
```

---

# Test Checklist

## Auth Tests
- [ ] `test_login_success` - Valid credentials return tokens
- [ ] `test_login_invalid_password` - Wrong password returns 401
- [ ] `test_login_nonexistent_user` - Unknown email returns 401
- [ ] `test_register_admin_only` - Non-admin cannot register users
- [ ] `test_register_duplicate_email` - Duplicate email returns 400
- [ ] `test_refresh_valid_token` - Valid refresh token works
- [ ] `test_refresh_invalid_token` - Invalid token returns 401
- [ ] `test_me_authenticated` - Returns current user info
- [ ] `test_me_unauthenticated` - No token returns 401/403
- [ ] `test_logout_invalidates_token` - Refresh token invalidated

## User Tests (Admin)
- [ ] `test_list_users_admin` - Admin can list users
- [ ] `test_list_users_non_admin` - Non-admin gets 403
- [ ] `test_create_user` - Admin can create user
- [ ] `test_update_user` - Admin can update user
- [ ] `test_delete_user` - Soft delete sets is_active=false
- [ ] `test_get_roles` - Returns role list

## Product Tests
- [ ] `test_list_products` - Pagination and search work
- [ ] `test_list_products_filter_category` - Category filter works
- [ ] `test_create_product` - Creates with correct fields
- [ ] `test_create_product_duplicate_sku` - Duplicate SKU returns 400
- [ ] `test_update_product` - Partial update works
- [ ] `test_delete_product` - Soft delete via is_active
- [ ] `test_low_stock_products` - Returns only low stock items

## Order Tests
- [ ] `test_create_order` - Creates order with line items
- [ ] `test_create_order_invalid_customer` - Invalid customer_id returns 404
- [ ] `test_list_orders` - Filtering by status works
- [ ] `test_get_order` - Returns full order with line items
- [ ] `test_update_order_draft` - Can update draft order
- [ ] `test_update_order_confirmed` - Cannot change confirmed order items
- [ ] `test_status_draft_to_confirmed` - Valid transition works
- [ ] `test_status_draft_to_completed` - Invalid transition returns 400
- [ ] `test_confirm_deducts_stock` - Stock reduced on confirm
- [ ] `test_cancel_restores_stock` - Stock restored on cancel
- [ ] `test_delete_order` - Soft delete sets deleted_at

## Payment Tests
- [ ] `test_create_payment_incoming` - Creates from customer
- [ ] `test_create_payment_outgoing` - Creates to supplier
- [ ] `test_payment_updates_debt` - Customer debt reduced
- [ ] `test_payment_updates_order` - Order paid_amount updated
- [ ] `test_receivables_summary` - AR report correct
- [ ] `test_payables_summary` - AP report correct

## Stock Tests
- [ ] `test_stock_in` - Increases product stock
- [ ] `test_stock_out` - Decreases product stock
- [ ] `test_stock_out_insufficient` - Returns 400 if not enough
- [ ] `test_stock_adjust` - Adjusts up or down
- [ ] `test_stock_movement_audit` - Movement logged correctly

## Report Tests
- [ ] `test_dashboard_metrics` - Returns all metrics
- [ ] `test_revenue_by_day` - Daily aggregation correct
- [ ] `test_revenue_by_month` - Monthly aggregation correct
- [ ] `test_top_products` - Sorted by quantity/revenue
- [ ] `test_inventory_valuation` - Calculates value correctly
- [ ] `test_arap_summary` - AR/AP totals correct

## Export Tests
- [ ] `test_export_orders_csv` - Returns valid CSV
- [ ] `test_export_products_csv` - Returns valid CSV
- [ ] `test_export_payments_csv` - Returns valid CSV
- [ ] `test_export_orders_filtered` - Filters applied
