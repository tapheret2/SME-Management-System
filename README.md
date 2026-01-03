# SME Management System

[![Release](https://img.shields.io/badge/release-v1.0.0-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-Commercial-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Production%20Ready-green.svg)]()

> **Enterprise-grade operations management for modern businesses.**  
> Streamline inventory, automate orders, and gain financial clarity in one powerful, self-hosted platform.

![Dashboard](docs/screenshots/dashboard.png)

---

## 🚀 Why Peganyx?

Managing a growing business with spreadsheets is a recipe for disaster. Stock discrepancies, lost orders, and untracked payments bleed revenue. 

**SME Management System** solves this by providing a unified command center for your entire operation:

*   **Inventory Control**: Real-time tracking with low-stock alerts and audit trails.
*   **Order Automation**: Seamless workflow from Draft → Confirmed → Shipped → Delivered.
*   **Financial Clarity**: Track who owes you (AR) and who you owe (AP) instantly.
*   **Data Sovereignty**: Self-hosted on your infrastructure. Your data, your rules.

---

## ⚡ Key Features

| Module | Capabilities |
|--------|-------------|
| **📦 Products** | Advanced SKU management, tiered pricing, and instant stock visibility. |
| **🛒 Orders** | Frictionless order processing with automatic inventory deduction and status tracking. |
| **💰 Payments** | Granular AR/AP tracking. Link payments to specific orders. |
| **📊 Reports** | C-level dashboards, revenue charts, and actionable business intelligence. |
| **🔒 Security** | Role-Based Access Control (RBAC), JWT authentication, and comprehensive audit logging. |
| **🌍 Localization** | Built for Vietnam market (VND currency, local formats) + International support. |

---

## 🛠️ Tech Stack & Architecture

Built on a battle-tested, high-performance stack designed for stability and scale:

*   **Backend**: Python 3.11, FastAPI (High-performance Async API), SQLAlchemy
*   **Frontend**: React 18, TanStack Query, Tailwind CSS (Modern, responsive UI)
*   **Database**: PostgreSQL 16 (Reliable, ACID-compliant data storage)
*   **Infrastructure**: Docker & Docker Compose (Containerized deployment)

---

## 📦 Quick Start (Production)

### Prerequisites
*   Docker Engine & Docker Compose v2+
*   Git

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/tapheret2/SME-Management-System.git
cd sme-management

# Configure Environment
cp backend/.env.example .env
# IMPORTANT: Edit .env and set a secure JWT_SECRET_KEY
```

### 2. Deployment

```bash
# Build and start services in production mode
docker compose up -d --build

# Verify status
docker compose ps
```

### 3. Access

*   **Application**: `http://localhost:5173` (or your domain)
*   **API Docs**: `http://localhost:8000/docs`

---

## 🔐 Default Credentials

> **WARNING**: Change these credentials immediately after first login.

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| **Administrator** | `admin@sme.com` | `Admin123!` | Full System Access |
| **Manager** | `manager@sme.com` | `Manager123!` | Operations & Reports |
| **Staff** | `staff@sme.com` | `Staff123!` | Orders & Basic Tasks |

---

## 📜 License

**Proprietary Commercial Software**

Copyright © 2026. All rights reserved.  
Unauthorized copying of this file, via any medium is strictly prohibited.  
See [LICENSE](LICENSE) for terms.

---

Need help or customization?

---
*Built with ❤️.*
