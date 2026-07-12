# TransitOps — Smart Transport Operations Platform

A centralized platform for managing the full lifecycle of transport operations: vehicle registry, driver safety tracking, trip dispatching, maintenance service logging, and operational cost rollups. Built to replace spreadsheet-driven fleet management.

---

## Tech Stack

* **Frontend:** Vue 3 (Vite SPA) styled with Tailwind CSS v3
* **Backend:** Python (Flask REST API returning JSON payloads only)
* **Database:** SQLite (`transitops.db` local relational database)
* **Authentication:** JWT-based stateless sessions with Role-Based Access Control (RBAC)

---

## Security & Operational Guardrails

### 1. Robust Password Cryptography
Passwords are securely hashed using Werkzeug's native `generate_password_hash` and verified with `check_password_hash` using salted PBKDF2/scrypt hashes, mitigating crack attempts on plain algorithms.

### 2. Form Submission locks
State-changing actions (e.g. Dispatch Trip, Close Shop Log, Post Fuel) use client-side `isSubmitting` reactive locks to shutter race conditions and duplicate database hits on poor mobile network latency.

### 3. Client-Side Sanitization & Brute Force Lockouts
* Raw input strings are XSS-sanitized to mitigate injection vectors.
* Accounts are temporarily locked out for 30 seconds after 5 consecutive failed login attempts.

### 4. Route Guards & Authoritative RBAC
All view actions are checked on the server (endpoint middleware decorators) and matched in the frontend router via `beforeEach` claim filters. Restricted views like `/analytics` block unauthorized access and redirect users to a custom `/403` Forbidden screen.

---

## Dynamic Responsive Layout & Data Condensation

* **Touch-Optimized Bottom Nav:** Viewports under 768px hide the desktop sidebar and render a thumb-friendly bottom nav bar featuring 48px minimum height tap zones for operational field workflows.
* **Collapsible Accordion Tables:** On mobile viewports, tables automatically drop secondary columns and render only 3 core identifiers. Click headers transition into smooth accordion drawers containing the hidden metadata fields.

---

## Roles Permissions Matrix

| Role | Fleet Registry | Drivers | Trips | Fuel/Expenses | Analytics |
|---|---|---|---|---|---|
| **Fleet Manager** | ✓ (CRUD) | ✓ (CRUD) | – | – | ✓ (Read) |
| **Dispatcher** | ✓ (Read) | – | ✓ (CRUD) | – | – |
| **Safety Officer** | – | ✓ (CRUD) | ✓ (Read) | – | – |
| **Financial Analyst** | ✓ (Read) | – | – | ✓ (CRUD) | ✓ (Read) |
| **Driver** | – | – | ✓ (Active) | – | – |

---

## Getting Started

### Local Environment Setup

1. **Install Python backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Seed the local SQLite database:**
   ```bash
   python init_db.py
   ```
3. **Start the backend Flask server:**
   ```bash
   python run.py
   ```
   *The Flask API boots locally on `http://localhost:5000/`.*

4. **Install frontend dependencies & start Vite dev server:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *The Vue application starts on `http://localhost:5173/`.*

---

## Seed Credentials

All seeded profiles default to `password123` passwords:

* **Fleet Manager:** `fleetmanager@transitops.dev`
* **Driver:** `driver@transitops.dev`
* **Safety Officer:** `safety@transitops.dev`
* **Financial Analyst:** `finance@transitops.dev`
* **Admin:** `admin@transitops.dev`
