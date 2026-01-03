# Changelog

All notable changes to the **Peganyx SME Management System** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-03

### 🚀 Initial Commercial Release

We are proud to announce the first commercial release of the Peganyx SME Management System. This release brings enterprise-grade inventory, order, and payment management to small and medium businesses.

### Added
*   **Authentication**: Secure JWT-based auth with Role-Based Access Control (Admin, Manager, Staff).
*   **Dashboard**: Real-time business intelligence dashboard with key metrics and charts.
*   **Products Module**: Complete lifecycle management (SKU, pricing, stock levels).
*   **Orders Module**: Draft to Completion workflow with automatic inventory deduction.
*   **Inventory Control**: Stock adjustments, audit trails, and low-stock alerts.
*   **Payments Module**: Separate tracking for Accounts Receivable (AR) and Accounts Payable (AP).
*   **Reports**: Comprehensive financial and operational reports.
*   **Export**: One-click CSV export for all major data entities.
*   **Localization**: Full support for Vietnamese language and currency formatting.
*   **Deployment**: Docker Compose support for rapid on-premise deployment.

### Security
*   Password hashing with bcrypt.
*   Protected API endpoints.
*   Secure HTTP-only cookies handling (where applicable).

### Infrastructure
*   PostgreSQL 15+ database backend.
*   FastAPI high-performance Python framework.
*   React + TanStack Query frontend.
