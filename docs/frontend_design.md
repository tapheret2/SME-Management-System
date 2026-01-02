# SME Frontend Design Specification

## Route Map

```
/login                    → Login page (public)
/                         → Dashboard (protected)
/orders                   → Orders list
/orders/:id               → Order detail
/orders/new               → Create order
/products                 → Products list
/products/:id             → Product detail/edit
/inventory                → Stock movements
/customers                → Customers list
/suppliers                → Suppliers list
/payments                 → Payments list
/reports                  → Reports dashboard
/settings                 → Settings (admin only)
/settings/users           → User management
```

---

## Navigation Structure

### Sidebar (Desktop) / Bottom Nav (Mobile)

```
┌─────────────────┐
│ 🏠 Dashboard    │
│ 📋 Đơn hàng     │
│ 📦 Sản phẩm     │
│ 📊 Tồn kho      │
│ 👥 Khách hàng   │
│ 🏭 Nhà cung cấp │
│ 💰 Thanh toán   │
│ 📈 Báo cáo      │
│ ⚙️ Cài đặt      │ (admin only)
└─────────────────┘
```

---

## Component Breakdown

### Shared Components

| Component | Props | Usage |
|-----------|-------|-------|
| `Layout` | `children` | Main app wrapper with sidebar |
| `PageHeader` | `title`, `subtitle`, `actions` | Page title + action buttons |
| `DataTable` | `columns`, `data`, `loading`, `pagination` | Reusable data table |
| `Modal` | `isOpen`, `onClose`, `title`, `children` | Dialog overlay |
| `FormField` | `label`, `error`, `children` | Form input wrapper |
| `Button` | `variant`, `loading`, `onClick` | Primary/Secondary/Danger |
| `Badge` | `variant`, `children` | Status badges |
| `Card` | `title`, `children` | Dashboard cards |
| `SearchInput` | `value`, `onChange`, `placeholder` | Search with debounce |
| `Select` | `options`, `value`, `onChange` | Dropdown select |
| `Toast` | (via react-hot-toast) | Notifications |
| `LoadingSpinner` | `size` | Loading indicator |
| `EmptyState` | `message`, `action` | No data placeholder |
| `ConfirmDialog` | `message`, `onConfirm` | Delete confirmation |

---

## Data Fetching Strategy (TanStack Query)

### Query Keys Convention
```javascript
// List queries
['products']
['products', { page, search, category }]
['orders', { page, status, customer_id }]
['customers', { page, search }]

// Detail queries
['product', productId]
['order', orderId]
['customer', customerId]

// Reports (with params)
['dashboard-metrics']
['revenue-report', { period, days }]
['top-products', { days, limit }]
['low-stock-products']
```

### Query Configuration
```javascript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes
      cacheTime: 30 * 60 * 1000,     // 30 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

### Mutation Pattern
```javascript
const mutation = useMutation({
  mutationFn: createProduct,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['products'] });
    toast.success('Tạo sản phẩm thành công!');
    closeModal();
  },
  onError: (error) => {
    toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
  },
});
```

---

## Page Specifications

### 1. Login Page

**Route:** `/login`

**Layout:** Centered card, no sidebar

**Form Fields:**
| Field | Type | Validation |
|-------|------|------------|
| Email | email input | Required, valid email |
| Password | password input | Required, min 6 chars |

**Actions:** Submit button, loading state

---

### 2. Dashboard

**Route:** `/`

**Components:**
- 4x KPI Cards (revenue, orders, AR, low stock)
- Revenue Chart (Area chart, 30 days)
- Low Stock Alert List
- Recent Orders Table (5 items)

**KPI Cards:**
| Card | Value | SubValue |
|------|-------|----------|
| Doanh thu hôm nay | VND amount | Order count |
| Doanh thu tháng | VND amount | Order count |
| Công nợ phải thu | VND amount | Customer count |
| Cảnh báo tồn kho | Product count | Total products |

**Queries:**
- `['dashboard-metrics']`
- `['revenue-report', { period: 'day', days: 30 }]`
- `['low-stock-products']`

---

### 3. Orders List

**Route:** `/orders`

**Filters:**
| Filter | Type | Options |
|--------|------|---------|
| Status | Select | All, Draft, Confirmed, Shipped, Completed, Cancelled |
| Customer | Search/Select | Customer list |
| Date Range | Date picker | From/To |

**Table Columns:**
| Column | Width | Sortable |
|--------|-------|----------|
| Mã đơn | 120px | Yes |
| Khách hàng | flex | No |
| Ngày đặt | 100px | Yes |
| Tổng tiền | 120px | Yes |
| Còn nợ | 100px | No |
| Trạng thái | 100px | No |
| Actions | 80px | No |

**Actions:** + Tạo đơn hàng

**Row Actions:** View, Quick status change

---

### 4. Order Detail

**Route:** `/orders/:id`

**Sections:**
1. **Header** - Order number, status badge, back button
2. **Customer Info** - Name, phone, address
3. **Line Items Table**
   - SKU, Product name, Quantity, Unit price, Discount, Line total
   - Add/Edit/Remove buttons (if draft)
4. **Order Summary** - Subtotal, Discount, Total, Paid, Remaining
5. **Status Actions** - Confirm, Ship, Complete, Cancel buttons
6. **Payment History** - Related payments list

**Forms:**
- Add Line Item Modal (product select, quantity, price)
- Edit discount modal

---

### 5. Products List

**Route:** `/products`

**Filters:**
| Filter | Type |
|--------|------|
| Search | Text (SKU, name) |
| Category | Select |
| Active only | Checkbox |

**Table Columns:**
| Column | Width |
|--------|-------|
| SKU | 100px |
| Tên sản phẩm | flex |
| Danh mục | 120px |
| Giá vốn | 100px |
| Giá bán | 100px |
| Tồn kho | 80px |
| Actions | 100px |

**Create/Edit Modal Fields:**
| Field | Type | Required |
|-------|------|----------|
| SKU | text | Yes |
| Tên sản phẩm | text | Yes |
| Danh mục | text | No |
| Đơn vị | text | Yes |
| Giá vốn | number | Yes |
| Giá bán | number | Yes |
| Tồn kho tối thiểu | number | No |
| Tồn kho ban đầu | number | No (create only) |

---

### 6. Inventory (Stock Movements)

**Route:** `/inventory`

**Layout:** 2-column grid
- Left: Current stock table
- Right: Recent movements table

**Actions:**
- + Nhập kho (Stock In modal)
- - Xuất kho (Stock Out modal)
- ± Điều chỉnh (Adjust modal)

**Stock Modal Fields:**
| Field | Type |
|-------|------|
| Sản phẩm | Product select |
| Số lượng | number |
| NCC | Supplier select (in only) |
| Lý do | text (adjust required) |

---

### 7. Customers List

**Route:** `/customers`

**Table Columns:**
| Column | Width |
|--------|-------|
| Mã KH | 80px |
| Tên | flex |
| Điện thoại | 120px |
| Email | 150px |
| Công nợ | 120px |
| Actions | 100px |

**Create/Edit Modal Fields:**
| Field | Required |
|-------|----------|
| Mã KH | Yes |
| Tên | Yes |
| Điện thoại | No |
| Email | No |
| Địa chỉ | No |
| Ghi chú | No |

---

### 8. Suppliers List

**Route:** `/suppliers`

Same structure as Customers with:
- "Công nợ phải trả" instead of "Công nợ"

---

### 9. Payments List

**Route:** `/payments`

**Tabs:** Tất cả | Phải thu (AR) | Phải trả (AP)

**Table Columns:**
| Column | Width |
|--------|-------|
| Mã phiếu | 120px |
| Loại | 80px |
| Đối tượng | flex |
| Số tiền | 120px |
| PT thanh toán | 100px |
| Ngày | 100px |

**Create Modal Fields:**
| Field | Type |
|-------|------|
| Loại | Select (Thu/Chi) |
| Khách hàng/NCC | Select (conditional) |
| Đơn hàng | Select (optional) |
| Số tiền | number |
| PT thanh toán | Select (Cash/Bank/Other) |
| Ghi chú | textarea |

---

### 10. Reports

**Route:** `/reports`

**Sections:**
1. **Summary Cards** (4x)
   - Total revenue, Inventory value, AR, AP
2. **Revenue Chart**
   - Period selector: Day/Week/Month
   - Days selector: 7/30/90/365
3. **Top Products** (horizontal bar chart)
4. **Inventory Valuation Table**
5. **Export Buttons** (CSV downloads)

---

### 11. Settings (Admin)

**Route:** `/settings`

**Tabs:**
- Users (list + CRUD)
- (Future: Roles, Company info)

**Users Table:**
| Column | Width |
|--------|-------|
| Email | flex |
| Họ tên | 150px |
| Vai trò | 100px |
| Trạng thái | 80px |
| Actions | 100px |

**Create User Modal:**
| Field | Required |
|-------|----------|
| Email | Yes |
| Mật khẩu | Yes |
| Họ tên | Yes |
| Vai trò | Yes (select) |

---

## Responsive Breakpoints

```css
/* Mobile first */
@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md - show sidebar */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

### Mobile Adaptations:
- Sidebar → Bottom navigation (5 main items)
- Tables → Card list view
- 2-column grids → Single column
- Modal → Full screen on mobile
- Horizontal scroll for wide tables

---

## File Structure

```
src/
├── api/                    # API client modules
│   ├── client.js
│   ├── auth.js
│   ├── products.js
│   ├── orders.js
│   └── ...
├── components/
│   ├── Layout/
│   │   ├── Layout.jsx
│   │   ├── Sidebar.jsx
│   │   └── MobileNav.jsx
│   ├── ui/
│   │   ├── Button.jsx
│   │   ├── Modal.jsx
│   │   ├── DataTable.jsx
│   │   ├── Badge.jsx
│   │   └── ...
│   └── forms/
│       ├── ProductForm.jsx
│       ├── OrderForm.jsx
│       └── ...
├── context/
│   └── AuthContext.jsx
├── hooks/
│   ├── useProducts.js      # Product queries
│   ├── useOrders.js
│   └── ...
├── pages/
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   ├── Products.jsx
│   ├── Orders.jsx
│   ├── OrderDetail.jsx
│   └── ...
├── utils/
│   ├── formatters.js       # VND, date formatting
│   └── validators.js
├── App.jsx
├── main.jsx
└── index.css
```
