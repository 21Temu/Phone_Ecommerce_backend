# 📱 PhoneStore – Backend API

A RESTful e-commerce backend for a smartphone shopping platform, developed using **Python, Django REST Framework, and PostgreSQL**.

The backend provides APIs for authentication, smartphone catalog management, product variants, shopping orders, payment proof submissions, order tracking, and administration.

## 🚀 Features

### Authentication
- User registration.
- User login and authentication.
- Current user information.
- Role-based permissions.
- Admin access control.

### Product Catalog
- Smartphone brand management.
- Smartphone creation and management.
- Product descriptions and specifications.
- New, used, and refurbished conditions.
- Multiple product images.
- Primary product image selection.
- Product variant management.
- Storage, RAM, color, price, and stock management.
- Product search and filtering.

### Order Management
- Create customer orders.
- Manage order items and quantities.
- Calculate order totals.
- Submit payment proof.
- Verify submitted payments.
- Update order statuses.
- Track orders.
- Retrieve customer order history.

### Admin Management
- Admin dashboard statistics.
- Manage smartphones and brands.
- Manage product variants and images.
- View and manage customer orders.
- Verify customer payment submissions.
- Manage user accounts.
- Monitor product stock.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Backend framework |
| Django REST Framework | REST API development |
| PostgreSQL | Relational database |
| Pillow | Image processing |
| django-cors-headers | Cross-origin requests |
| django-filter | API filtering |
| Gunicorn | Production WSGI server |
| Whitenoise | Static file serving |

## 📁 Project Structure

```text
backend/
├── apps/
│   ├── accounts/
│   ├── catalog/
│   └── orders/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── admin_urls.py
│   └── wsgi.py
├── media/
├── static/
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_BACKEND_GITHUB_URL
```

### 2. Navigate to the backend directory

```bash
cd backend
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows CMD:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure PostgreSQL

Create a PostgreSQL database:

```sql
CREATE DATABASE phone_store;
```

### 7. Configure environment variables

Create a `.env` file beside `manage.py`:

```env
SECRET_KEY=your_secret_key
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=phone_store
DB_USER=postgres
DB_PASSWORD=your_postgresql_password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Use your actual database credentials. Keep `.env` private and never upload it to GitHub.

### 8. Apply database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 9. Create an administrator account

```bash
python manage.py createsuperuser
```

### 10. Start the development server

```bash
python manage.py runserver
```

Backend API:

```text
http://127.0.0.1:8000/
```

## 🔗 API Endpoints

Main API routes:

| Endpoint | Description |
|---|---|
| `/api/auth/` | Authentication |
| `/api/catalog/` | Public product catalog |
| `/api/orders/` | Customer orders |
| `/api/admin/dashboard/` | Admin dashboard |
| `/api/admin/brands/` | Brand management |
| `/api/admin/phones/` | Smartphone management |
| `/api/admin/variants/` | Product variant management |
| `/api/admin/images/` | Product image management |
| `/api/admin/orders/` | Admin order management |
| `/api/admin/users/` | User management |

## 🗄️ Database

PhoneStore uses PostgreSQL to store:

- User accounts and authentication data.
- Smartphone brands.
- Smartphone information and specifications.
- Product variants and inventory.
- Product images.
- Customer orders.
- Order items.
- Payment submissions.

## 🖼️ Media Files

Uploaded smartphone images and payment proof files are stored using Django's media file configuration.

For production deployment, configure appropriate persistent media storage.

## 🔐 Security

- Environment-based configuration.
- Role-based API permissions.
- Authentication-protected endpoints.
- Admin-only management endpoints.
- CORS configuration.
- Secure production settings.

Before deployment, set `DEBUG=False`, configure production hosts, and use secure secrets and HTTPS.

## 🚀 Production Deployment

The backend can be deployed to a suitable Python hosting platform.

Production requirements include:

- PostgreSQL database.
- Environment variables.
- Gunicorn.
- Static file configuration.
- Persistent media storage.
- CORS and allowed-host configuration.

## 👨‍💻 Developer

**PhoneStore E-commerce Project**

Backend developed using Python, Django REST Framework, and PostgreSQL.

## 📄 License

This project is developed for educational and software development purposes.
