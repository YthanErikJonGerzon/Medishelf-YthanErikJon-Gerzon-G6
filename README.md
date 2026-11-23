# MediShelf — Clinic Medicine & Medical-Supply Inventory Management System

**MediShelf** is a full-stack web-based inventory management system built with **Django** and **PostgreSQL (Supabase)** for school clinics and barangay health centers. It replaces manual logbooks with real-time medicine and batch tracking, automated shelf-life/expiration monitoring, validated stock-in/stock-out transactions, role-based access control, and an immutable audit trail.

---

## Key Features Implemented

### 1. Account & Role-Based Access Control (Project Development 1)
* **User Registration & Authentication:** Secure registration with email uniqueness validation, password hashing via Django's built-in auth system, login, and session logout.
* **Role-Based Dashboards:** Dedicated dashboards and URL access protection (`@role_required`) for **Administrator**, **Clinic Staff**, and **Viewer** roles.
* **Profile Management:** Logged-in users can view and update their personal information (`full_name`, `email`, `contact_number`, and `profile_photo`).

### 2. Core Feature: Medicine, Batch & Stock Transaction Vertical Slice (Project Development 2)
* **Medicine & Batch CRUD:** Create, read, update, and delete medicine master records and batch-level inventory entries linked to the creating user (`ForeignKey` to `User`).
* **Automated Expiration Categorization (`BR-01`):** Automatically classifies medicine batches into **Valid** (`> 30 days`), **Expiring Soon** (`1–30 days`), or **Expired** (`≤ 0 days`) and excludes expired batches from usable stock totals.
* **Stock-In & Stock-Out Transactions (`BR-02`):** Atomic stock-in (receiving) and stock-out (dispensing) operations that validate positive quantities, prevent over-dispensing beyond on-hand batch quantity, and block dispensing from expired batches.
* **Low-Stock Alerting (`BR-03`):** Flags medicines when total usable stock drops to or below the configured `reorder_level` across role dashboards and the inventory list.
* **Role-Restricted Deletion (`BR-04`):** Restricts permanent deletion of inventory records strictly to **Administrator** accounts.
* **System Audit Trail (`BR-05`):** Logs every medicine update, batch creation, deletion, and stock transaction with timestamps and user attribution.

---

## Tech Stack
* **Backend:** Python 3, Django
* **Database:** PostgreSQL hosted on Supabase (Transaction Pooler)
* **Frontend:** Django Templates, HTML5, CSS3
* **Environment Management:** `python-dotenv`, `psycopg`

---

## Local Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/YthanErikJonGerzon/Medishelf-YthanErikJon-Gerzon-G6.git](https://github.com/YthanErikJonGerzon/Medishelf-YthanErikJon-Gerzon-G6.git)
cd Medishelf-YthanErikJon-Gerzon-G6
