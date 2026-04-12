# Createch Backend API

A Django REST Framework backend for **Createch** — a creative services marketplace that connects clients with creators for design, development, writing, and other creative work.

Built with **Django 6.0**, **PostgreSQL (Supabase)**, and **JWT authentication**.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Server](#running-the-server)
- [Seeding Sample Data](#seeding-sample-data)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Users](#users)
  - [Creators](#creators)
  - [Services](#services)
  - [Orders](#orders)
  - [Other Resources](#other-resources)
- [Testing with HTTPie](#testing-with-httpie)
- [Testing with Python Script](#testing-with-python-script)
- [Admin Dashboard](#admin-dashboard)
- [Models Overview](#models-overview)

---

## Features

- **JWT Authentication** — Register, Login, and protected profile endpoint
- **User Management** — Full CRUD for users with role-based profiles (client, creator, admin)
- **Creator Profiles** — Extended profiles with bio, skills, portfolio, and verification status
- **Services Marketplace** — Creators can list services; clients can browse by category
- **Order Management** — Complete order lifecycle (pending → in_progress → completed) with delivery and escrow tracking
- **Messaging** — Direct messaging between clients and creators
- **Reviews & Ratings** — Post-order reviews with star ratings
- **Smart Matching** — Client-creator matching with scored recommendations
- **Social Features** — Follow, block, and report users
- **Payment & Wallets** — Payment methods, creator wallets, and withdrawal tracking
- **Support Tickets** — User-submitted support tickets with admin response
- **Daily Analytics** — Creator profile views and service click tracking
- **Admin Panel** — Full Django admin interface for managing all models

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.13** | Programming language |
| **Django 6.0** | Web framework |
| **Django REST Framework 3.17** | REST API toolkit |
| **PostgreSQL (Supabase)** | Database |
| **PyJWT** | JWT token generation & verification |
| **psycopg2-binary** | PostgreSQL adapter |
| **django-cors-headers** | Cross-Origin Resource Sharing |
| **HTTPie** | API testing tool |

---

## Project Structure

```
Createch-backend/
├── createch/                  # Django project settings
│   ├── settings.py            # Main configuration
│   ├── urls.py                # Root URL routing
│   ├── wsgi.py                # WSGI entry point
│   └── asgi.py                # ASGI entry point
│
├── marketplace/               # Main application
│   ├── models.py              # 19 database models
│   ├── views.py               # 18 ViewSet classes
│   ├── serializers.py         # DRF serializers
│   ├── urls.py                # API URL routing
│   ├── admin.py               # Django admin configuration
│   ├── authentication.py      # Custom JWT authentication backend
│   └── auth_views.py          # Register, Login, Me views
│
├── seed.py                    # Database seeding script
├── test_api.py                # Python-based API test script
├── test_httpie.bat            # HTTPie CLI test commands
├── manage.py                  # Django management CLI
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in version control)
└── .gitignore
```

---

## Prerequisites

- **Python 3.10+** (tested with Python 3.13)
- **pip** (Python package manager)
- **PostgreSQL** database (or a [Supabase](https://supabase.com) project)
- **Git**

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Createch-backend.git
cd Createch-backend
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your-django-secret-key

# Supabase PostgreSQL
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_HOST=db.your-project-id.supabase.co
DB_PORT=5432
```

> **Note:** The `.env` file is excluded from version control via `.gitignore`. Never commit credentials.

---

## Database Setup

### Apply migrations

```bash
python manage.py migrate
```

This creates the Django-managed tables (`auth_credentials`, Django admin tables) in your PostgreSQL database. The marketplace models (users, orders, services, etc.) are **unmanaged** — they map to existing Supabase tables.

---

## Running the Server

```bash
python manage.py runserver
```

The API will be available at **http://127.0.0.1:8000/api/**

---

## Seeding Sample Data

Populate the database with test accounts and sample data:

```bash
python seed.py
```

This creates:

| Account | Email | Password | Role |
|---------|-------|----------|------|
| Admin | `admin@createch.com` | `Admin@1234` | admin |
| Creator | `creator@createch.com` | `Creator@1234` | creator |
| Client | `client@createch.com` | `Client@1234` | client |

Plus sample categories, services, orders, and a creator profile.

---

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/`

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/register/` | Register a new user | No |
| `POST` | `/api/auth/login/` | Login and get JWT token | No |
| `GET` | `/api/auth/me/` | Get authenticated user's profile | Yes |

#### Register

```json
POST /api/auth/register/
{
    "email": "user@example.com",
    "password": "SecurePass@123",
    "confirm_password": "SecurePass@123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "09123456789",
    "role": "client"
}
```

**Response (201):**
```json
{
    "message": "Registration successful.",
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "firebase_uid": "django_abc123def456",
    "email": "user@example.com",
    "role": "client",
    "full_name": "John Doe"
}
```

#### Login

```json
POST /api/auth/login/
{
    "email": "creator@createch.com",
    "password": "Creator@1234"
}
```

**Response (200):**
```json
{
    "message": "Login successful.",
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "firebase_uid": "django_abc123def456",
    "email": "creator@createch.com",
    "role": "creator",
    "full_name": "Juan Dela Cruz"
}
```

#### Authenticated Request

Include the JWT token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/` | List all users |
| `POST` | `/api/users/` | Create a user |
| `GET` | `/api/users/{id}/` | Get a user by ID or firebase_uid |
| `PUT` | `/api/users/{id}/` | Update a user |
| `DELETE` | `/api/users/{id}/` | Delete a user |

---

### Creators

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/creators/` | List all creator profiles |
| `POST` | `/api/creators/` | Create a creator profile |
| `GET` | `/api/creators/{id}/` | Get a creator by ID |
| `GET` | `/api/creators/by-uid/{firebase_uid}/` | Get creator by firebase UID |

---

### Services

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/services/` | List all services |
| `GET` | `/api/services/?category=Design` | Filter by category |
| `GET` | `/api/services/?creator_id={uid}` | Filter by creator |
| `POST` | `/api/services/` | Create a service |
| `GET` | `/api/services/{id}/` | Get a service by ID |
| `PUT` | `/api/services/{id}/` | Update a service |
| `DELETE` | `/api/services/{id}/` | Delete a service |

---

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/orders/` | List all orders |
| `GET` | `/api/orders/?client_id={uid}` | Filter by client  |
| `GET` | `/api/orders/?creator_id={uid}` | Filter by creator |
| `POST` | `/api/orders/` | Create an order |
| `GET` | `/api/orders/{id}/` | Get an order by ID |
| `POST` | `/api/orders/{id}/update_status/` | Update order status |

---

### Other Resources

All resources follow standard REST conventions (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`):

| Endpoint | Description | Query Filters |
|----------|-------------|---------------|
| `/api/categories/` | Service categories | — |
| `/api/reviews/` | Order reviews | `?reviewee_id=` |
| `/api/messages/` | Direct messages | `?user_id=` |
| `/api/follows/` | Follow relationships | `?follower_id=`, `?following_id=` |
| `/api/blocks/` | Block relationships | `?blocker_id=` |
| `/api/reports/` | User reports | — |
| `/api/matches/` | Smart matches | `?client_id=`, `?creator_id=` |
| `/api/payment-methods/` | Payment methods | `?user_id=` |
| `/api/support-tickets/` | Support tickets | `?user_id=` |
| `/api/wallets/` | User wallets | `?user_id=` |
| `/api/withdrawals/` | Withdrawal requests | `?user_id=` |
| `/api/order-timeline/` | Order event logs | `?order_id=` |
| `/api/deadline-notifications/` | Deadline alerts | — |
| `/api/daily-analytics/` | Creator analytics | `?creator_id=` |

---

## Testing with HTTPie

[HTTPie](https://httpie.io) is installed as a project dependency. Run individual commands:

```bash
# Register a new user
http POST http://127.0.0.1:8000/api/auth/register/ \
  email=test@example.com \
  password=Test@1234 \
  confirm_password=Test@1234 \
  first_name=Test \
  last_name=User \
  role=client

# Login
http POST http://127.0.0.1:8000/api/auth/login/ \
  email=creator@createch.com \
  password=Creator@1234

# Authenticated request (paste token from login response)
http GET http://127.0.0.1:8000/api/auth/me/ \
  "Authorization:Bearer eyJhbGciOiJIUzI1NiIs..."

# List services (public)
http GET http://127.0.0.1:8000/api/services/

# List orders
http GET http://127.0.0.1:8000/api/orders/

# List categories
http GET http://127.0.0.1:8000/api/categories/

# List users
http GET http://127.0.0.1:8000/api/users/
```

Or run the batch script for all tests at once:

```bash
test_httpie.bat
```

---

## Testing with Python Script

A Python test script is also included that tests all major endpoints:

```bash
# Make sure the server is running first
python manage.py runserver

# In another terminal
python test_api.py
```

**Expected output:**

```
============================================================
CREATECH API — ENDPOINT TESTING
============================================================

[1] POST /api/auth/register/    → 201 or 409
[2] POST /api/auth/login/       → 200
[3] GET  /api/auth/me/          → 200
[4] GET  /api/services/         → 200
[5] GET  /api/orders/           → 200
[6] GET  /api/users/            → 200

============================================================
All tests complete!
============================================================
```

---

## Admin Dashboard

Access the Django admin panel at **http://127.0.0.1:8000/admin/**

To create an admin superuser for the Django admin:

```bash
python manage.py createsuperuser
```

The admin panel provides full management for all 19 models with search, filtering, and list views.

---

## Models Overview

The backend contains **19 models** mapped to a Supabase PostgreSQL database:

| Model | Table | Description |
|-------|-------|-------------|
| `User` | `users` | User accounts (Firebase Auth backed) |
| `AuthCredential` | `auth_credentials` | Login credentials (email + hashed password) |
| `Creator` | `creators` | Extended creator profiles |
| `Category` | `categories` | Service categories |
| `Service` | `services` | Services offered by creators |
| `Order` | `orders` | Client orders with full lifecycle tracking |
| `OrderTimeline` | `order_timeline` | Event log for order status changes |
| `Review` | `reviews` | Client reviews and ratings |
| `Message` | `messages` | Direct messages between users |
| `Follow` | `follows` | Follow relationships |
| `Block` | `blocks` | Block relationships |
| `Report` | `reports` | User reports |
| `Match` | `matches` | Smart client-creator matching |
| `PaymentMethod` | `payment_methods` | Saved payment methods |
| `SupportTicket` | `support_tickets` | Support tickets |
| `UserWallet` | `user_wallets` | Creator payout wallets |
| `Withdrawal` | `withdrawals` | Withdrawal requests |
| `DeadlineNotification` | `deadline_notifications` | Order deadline alerts |
| `DailyAnalytics` | `daily_analytics` | Creator daily analytics |

> All models except `AuthCredential` use `managed = False` — they map to existing Supabase tables and are not created by Django migrations.

---

## License

This project is for academic purposes.
