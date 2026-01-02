# SME Management System

> Complete inventory, orders, and payment management for small & medium enterprises.

![Dashboard Screenshot](docs/screenshots/dashboard.png)
*Screenshot: Dashboard with real-time KPIs*

---

## 🎯 Features

| Module | Capabilities |
|--------|-------------|
| **Products** | SKU management, categories, cost/sell pricing, low-stock alerts |
| **Inventory** | Stock in/out/adjust movements, audit trail |
| **Orders** | Draft → Confirmed → Shipped → Completed workflow, auto stock deduction |
| **Payments** | Incoming (AR) and outgoing (AP), order linking |
| **Reports** | Dashboard KPIs, revenue charts, top products |
| **Export** | CSV export for products, orders, payments |
| **Audit** | Full action log with before/after snapshots |
| **Security** | JWT authentication, role-based access (Admin/Manager/Staff) |

---

## 📸 Screenshots

| Dashboard | Orders | Products |
|-----------|--------|----------|
| ![Dashboard](docs/screenshots/dashboard_thumb.png) | ![Orders](docs/screenshots/orders_thumb.png) | ![Products](docs/screenshots/products_thumb.png) |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/sme-management.git
cd sme-management

# Configure environment
cp .env.example .env
# Edit .env with your settings (especially JWT_SECRET_KEY for production)

# Start services
docker compose up -d

# Load demo data (optional)
docker compose exec api python -m app.demo_data

# Access the application
open http://localhost:5173  # Frontend
open http://localhost:8000/docs  # API Documentation
```

### Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@sme.com | Admin123! |
| Manager | manager@sme.com | Manager123! |
| Staff | staff@sme.com | Staff123! |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  PostgreSQL │
│  (React)    │     │  (FastAPI)  │     │  Database   │
│  Port 5173  │     │  Port 8000  │     │  Port 5432  │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Tech Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React, TanStack Query, Tailwind CSS
- **Database**: PostgreSQL 16
- **Auth**: JWT with refresh tokens
- **Container**: Docker Compose

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Authenticate user |
| GET | `/api/products` | List products |
| POST | `/api/orders` | Create order |
| PUT | `/api/orders/{id}/status` | Update order status |
| GET | `/api/reports/dashboard` | Dashboard metrics |
| GET | `/api/export/products.csv` | Export products |
| GET | `/api/audit` | Audit logs (admin) |

Full documentation at: `http://localhost:8000/docs`

---

## 🔐 Role-Based Access

| Feature | Admin | Manager | Staff |
|---------|:-----:|:-------:|:-----:|
| View Dashboard | ✅ | ✅ | ✅ |
| Manage Products | ✅ | ✅ | ✅ |
| Create Orders | ✅ | ✅ | ✅ |
| View Reports | ✅ | ✅ | ❌ |
| Export Data | ✅ | ✅ | ❌ |
| Manage Users | ✅ | ❌ | ❌ |
| View Audit Logs | ✅ | ❌ | ❌ |

### Frontend Role-Based UI Hiding

The frontend should conditionally render UI elements based on user role:

```javascript
// Example: Hide admin-only features
{user.role === 'admin' && <AuditLogLink />}
{['admin', 'manager'].includes(user.role) && <ReportsMenu />}
```

---

## 💾 Database Backup

### Manual Backup
```bash
docker compose exec db pg_dump -U sme_user sme_db > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
cat backup_20260103.sql | docker compose exec -T db psql -U sme_user sme_db
```

### Automated Backups (Recommended)
Set up a cron job for daily backups:
```bash
0 2 * * * cd /path/to/project && docker compose exec -T db pg_dump -U sme_user sme_db | gzip > /backups/sme_$(date +\%Y\%m\%d).sql.gz
```

---

## 🧪 Testing

```bash
# Run all tests
docker compose exec api pytest tests/ -v

# Run specific milestone tests
docker compose exec api pytest tests/test_milestone1.py -v

# Test coverage
docker compose exec api pytest tests/ --cov=app --cov-report=html
```

**Current status**: 38 tests passing

---

## 📦 Deployment

### Production Checklist
- [ ] Set `DEBUG=false` in `.env`
- [ ] Generate secure `JWT_SECRET_KEY` (min 32 chars)
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Set up SSL/HTTPS (nginx reverse proxy)
- [ ] Configure database backups
- [ ] Set up monitoring/alerting

### Docker Production Build
```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## 💼 Sales Pitch

### Pain Points Solved

❌ **Before**: Messy Excel spreadsheets, lost orders, manual stock counts, no visibility into profits

✅ **After**: Real-time inventory, automated order workflow, instant reports, complete audit trail

### Why Choose SME Management System?

| Problem | Solution |
|---------|----------|
| Stock discrepancies | Automatic deduction on order confirmation |
| Lost payment records | Linked payments with AR/AP tracking |
| No order history | Complete order lifecycle with audit log |
| Manual reporting | One-click dashboard & CSV exports |
| Access control | Role-based permissions (Admin/Manager/Staff) |

### Key Features
- ✅ **Order Workflow**: Draft → Confirm → Ship → Complete with auto stock updates
- ✅ **Low Stock Alerts**: Never run out of bestsellers
- ✅ **Payment Tracking**: Know exactly who owes what
- ✅ **Audit Trail**: Full history of every change
- ✅ **CSV Export**: Easy data for accountants
- ✅ **Multi-user**: Team collaboration with role-based access
- ✅ **Vietnamese-ready**: Supports VND currency, Vietnamese text

### Pricing Suggestion

| Package | Price | Includes |
|---------|-------|----------|
| **Setup Fee** | $500 - $1,000 | Installation, configuration, training, 1-month support |
| **Monthly Maintenance** | $50 - $100/month | Bug fixes, minor updates, email support |
| **Custom Development** | $30 - $50/hour | New features, integrations, customizations |

*For 1-3 users, simple deployment. Scale pricing for more users or advanced features.*

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Support

- 📧 Email: support@yourcompany.com
- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/sme-management/issues)
