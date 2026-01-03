# SME Management System (Portfolio Demo)

![React](https://img.shields.io/badge/Frontend-React%20%2B%20TanStack-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Docker](https://img.shields.io/badge/Deploy-Docker%20Compose-blue)

**A production-grade Operations Management platform designed for Small & Medium Enterprises.**

> ⚠️ **Note**: This is a portfolio demonstration version. Some commercial modules (Billing, Advanced Analytics) have been removed or mocked.

## 🏗️ Architecture

This project demonstrates a modern, scalable full-stack architecture:

*   **Frontend**: React 18 (Vite), TailwindCSS, TanStack Query for state management.
*   **Backend**: Python 3.11 (FastAPI), SQLAlchemy (Async), Pydantic.
*   **Database**: PostgreSQL 15.
*   **Infrastructure**: Nginx Reverse Proxy, Gunicorn, Docker Compose (Multi-stage builds).

## ⭐ Key Features (Demo)

*   **Inventory Control**: Real-time SKU tracking with low-stock alerts.
*   **Order Workflow**: Full lifecycle management (Draft → Confirmed → Shipped).
*   **Financials**: Accounts Receivable (AR) & Payable (AP) tracking.
*   **Security**: JWT Authentication (Access/Refresh tokens) & RBAC.

## 🚀 How to Run

### Prerequisites
*   Docker & Docker Compose

### Quick Start
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/sme-management-portfolio.git
    cd sme-management-portfolio
    ```

2.  **Configure Environment**:
    ```bash
    cp .env.example .env
    # No need to edit for local demo (uses default dev config)
    ```

3.  **Start Services**:
    ```bash
    # Starts DB, API, and Web server
    docker compose up -d
    ```

4.  **Access**:
    *   **App**: `http://localhost`
    *   **Docs**: `http://localhost/api/docs`

> **Demo Credentials**:
> *   Email: `admin@demo.local`
> *   Password: `DemoAdmin123!`

## 🔒 Security & Best Practices Implemented

*   **Fail-Secure Config**: Application refuses to start if secrets are missing.
*   **Production Builds**:
    *   Frontend served via Nginx (Static) instead of Node dev server.
    *   Backend runs via Gunicorn Process Manager.
*   **API Gateway**: Nginx configured as a reverse proxy to handle CORS and routing.

---
*Built by [Your Name].*
