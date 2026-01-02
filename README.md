# SME Management System

Hệ thống quản lý nội bộ cho doanh nghiệp SME Việt Nam - Quản lý Đơn hàng, Tồn kho, Khách hàng, Nhà cung cấp, Thanh toán/Công nợ và Báo cáo.

## 🚀 Quick Start

### Yêu cầu

- Docker & Docker Compose
- Node.js 18+ (nếu chạy frontend riêng)
- Python 3.11+ (nếu chạy backend riêng)

### Chạy với Docker Compose

```bash
# Clone repo và vào thư mục
cd SME

# Copy file môi trường
cp .env.example .env

# Khởi động tất cả services
docker compose up --build

# Chờ khoảng 1-2 phút để build xong
```

Sau khi chạy xong:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Seed dữ liệu demo

```bash
# Chạy seed script trong container
docker compose exec api python -m app.seed
```

### Tài khoản demo

| Vai trò | Email | Mật khẩu |
|---------|-------|----------|
| Admin | admin@sme.local | Admin123! |
| Manager | manager@sme.local | Manager123! |
| Staff | staff@sme.local | Staff123! |

## 📁 Project Structure

```
SME/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── utils/     # Utilities
│   ├── alembic/       # DB migrations
│   └── tests/         # pytest tests
├── frontend/          # React + Vite frontend
│   └── src/
│       ├── api/       # API client
│       ├── components/
│       ├── pages/
│       └── context/
└── docker-compose.yml
```

## 🔧 Development

### Chạy backend riêng

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Cần PostgreSQL đang chạy
export DATABASE_URL="postgresql://user:pass@localhost:5432/sme_db"
uvicorn app.main:app --reload
```

### Chạy frontend riêng

```bash
cd frontend
npm install
npm run dev
```

### Chạy tests

```bash
cd backend
pytest tests/ -v
```

### Tạo migration mới

```bash
docker compose exec api alembic revision --autogenerate -m "description"
docker compose exec api alembic upgrade head
```

## 🔑 Features

### Quản lý người dùng (RBAC)
- 3 vai trò: Admin, Manager, Staff
- JWT authentication (access + refresh tokens)

### Quản lý sản phẩm
- CRUD sản phẩm với SKU, giá vốn, giá bán
- Cảnh báo tồn kho thấp

### Quản lý khách hàng/Nhà cung cấp
- Thông tin liên hệ
- Theo dõi công nợ

### Quản lý đơn hàng
- Quy trình: Nháp → Xác nhận → Giao hàng → Hoàn thành
- Tự động trừ/cộng tồn kho
- Quản lý chi tiết sản phẩm trong đơn

### Xuất/Nhập kho
- Nhập kho từ NCC
- Xuất kho (bán hoặc thủ công)
- Điều chỉnh tồn kho

### Thanh toán & Công nợ
- Phiếu thu (từ khách hàng)
- Phiếu chi (cho nhà cung cấp)
- Báo cáo AR/AP

### Báo cáo
- Dashboard tổng quan
- Biểu đồ doanh thu theo ngày/tuần/tháng
- Top sản phẩm bán chạy
- Giá trị tồn kho
- Xuất CSV

## 📋 API Documentation

Truy cập http://localhost:8000/docs để xem Swagger UI với đầy đủ API endpoints.

### Main endpoints:

- `POST /api/auth/login` - Đăng nhập
- `GET /api/products` - Danh sách sản phẩm
- `GET /api/customers` - Danh sách khách hàng
- `GET /api/suppliers` - Danh sách NCC
- `GET /api/orders` - Danh sách đơn hàng
- `GET /api/payments` - Danh sách thanh toán
- `GET /api/stock` - Lịch sử xuất nhập kho
- `GET /api/reports/dashboard` - Metrics dashboard

## 🔒 Environment Variables

Xem file `.env.example` để biết các biến môi trường cần thiết.

## 📝 License

MIT License
