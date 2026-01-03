# SME Management System

[![License](https://img.shields.io/badge/license-Commercial-purple.svg)](LICENSE)
![Architecture](https://img.shields.io/badge/Architecture-Microservices%20Ready-orange)
![Status](https://img.shields.io/badge/Status-Production%20Stable-green)

> **Enterprise-grade operations management platform for modern businesses.**  
> A unified command center to streamline inventory, automate orders, and ensure financial clarity.

![Dashboard](docs/screenshots/dashboard.png)

---

## 🚀 Product Overview

**SME Management System** is a purpose-built solution for small to medium enterprises facing the chaos of spreadsheet management. It replaces manual tracking with a secure, automated, and audit-ready platform.

**Key Value Propositions:**
*   **Precision**: Zero-error inventory tracking with double-entry stock adjustments.
*   **Speed**: Order processing time reduced by ~70% via automated workflows.
*   **Clarity**: Real-time AR/AP dashboards (Accounts Receivable/Payable).

---

## ⚡ Key Modules

| Module | Capabilities |
|--------|-------------|
| **📦 Smart Inventory** | Multi-warehouse logic, SKU/Barcode management, and Low-stock predictive alerts. |
| **🛒 Order Engine** | State-machine driven workflows (Draft → Confirmed → Shipped) with STRICT validation. |
| **💰 Financial Core** | Integrated AR/AP tracking. Automatic debt calculation per customer/supplier. |
| **🛡️ Enterprise Security** | Role-Based Access Control (RBAC), JWT Rotation, and Immutable Audit Logs. |

---

## 🛠️ Technology Stack

*   **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL 16
*   **Frontend**: React 18, TanStack Query, Tailwind CSS
*   **Infrastructure**: Docker, Nginx, Gunicorn

---

## 📦 Quick Start (Developers)

This repository includes a fully functional showcase version.

### Prerequisites
*   Docker & Docker Compose v2+
*   Git

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/tapheret2/SME-Management-System.git
cd sme-management

# Configure Environment
cp .env.example .env
# Note: The example config is ready for local testing
```

### 2. Deployment

You can choose between Development mode (Hot-reload) or Production mode (Demo).

**Option A: Production / Demo Mode (Recommended)**
Runs on port 80 with Nginx + Gunicorn (Fast & optimized).

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

**Option B: Development Mode**
Runs on port 5173 with Vite hot-reload.

```bash
docker compose up -d
```

### 3. Access

*   **Production URL**: `http://localhost`
*   **Dev URL**: `http://localhost:5173` (If using Option B)
*   **API Docs**: `http://localhost:8000/docs`

> **Demo Credentials**:
> *   Email: `admin@sme.com`
> *   Password: `Admin123!`

---

## 📜 Licensing

**Proprietary Commercial Software - Portfolio Version**

*   The source code in this repository is for **Portfolio / Demonstration purposes only**.
*   Unauthorized copying, modification, distribution, or use for commercial purposes is strictly prohibited.

Copyright © 2026. All Rights Reserved.
