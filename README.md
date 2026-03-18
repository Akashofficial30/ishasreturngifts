# 🎁 Isha Return Gifts – Django eCommerce Website

A production-ready Django 5 eCommerce website for a premium return gifts business.
Styled with a luxury South Indian wedding aesthetic — rich golds, deep maroon, and cream tones.

---

## 📋 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.0 |
| Database | PostgreSQL |
| Frontend | HTML5 + CSS3 + Bootstrap 5 |
| Fonts | Cormorant Garamond + Jost (Google Fonts) |
| Payment | Razorpay |
| Admin | Django Admin |
| Media | Pillow (image handling) |

---

## 🗂️ Project Structure

```
isha_return_gifts/
├── manage.py
├── requirements.txt
├── setup.py                  ← Seed script (creates admin + sample data)
├── setup_db.sql              ← PostgreSQL setup SQL
├── .env.example              ← Environment variables template
│
├── isha_return_gifts/        ← Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── products/                 ← Product catalog, cart
│   ├── models.py             ← Category, Product, Cart, CartItem, Testimonial
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── context_processors.py
│
├── orders/                   ← Checkout & order management
│   ├── models.py             ← Order, OrderItem
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── payments/                 ← Razorpay integration
│   ├── models.py             ← Payment
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── users/                    ← Authentication
│   ├── models.py             ← UserProfile
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── templates/
│   ├── base.html             ← Header, footer, nav
│   ├── home.html             ← Homepage with hero, featured, categories
│   ├── products/
│   │   ├── product_list.html
│   │   ├── product_detail.html
│   │   └── cart.html
│   ├── orders/
│   │   ├── checkout.html
│   │   └── order_confirmation.html
│   ├── payments/
│   │   ├── payment.html      ← Razorpay checkout
│   │   └── payment_failed.html
│   └── users/
│       ├── login.html
│       └── register.html
│
└── static/
    ├── css/style.css         ← Full custom CSS (1000+ lines)
    └── js/main.js            ← Animations, interactions
```

---

## ⚡ Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 13+
- pip

### 2. Clone / Extract Project

```bash
cd isha_return_gifts
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Setup PostgreSQL Database

Option A – using psql:
```bash
psql -U postgres -f setup_db.sql
```

Option B – manually:
```sql
CREATE DATABASE isha_return_gifts;
CREATE USER isha_user WITH PASSWORD 'isha@2025';
GRANT ALL PRIVILEGES ON DATABASE isha_return_gifts TO isha_user;
```

### 6. Configure Environment Variables

Create a `.env` file in the project root:
```
DB_NAME=isha_return_gifts
DB_USER=isha_user
DB_PASSWORD=isha@2025
DB_HOST=localhost
DB_PORT=5432

RAZORPAY_KEY_ID=rzp_test_YourKeyId
RAZORPAY_KEY_SECRET=YourKeySecret
```

Or update `settings.py` directly with your credentials.

### 7. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Seed Sample Data

```bash
python setup.py
```

This creates:
- ✅ Admin user: `admin` / `admin@12345`
- ✅ 6 product categories
- ✅ 12 sample products
- ✅ 6 customer testimonials

### 9. Collect Static Files

```bash
python manage.py collectstatic
```

### 10. Run the Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 🔑 Admin Panel

URL: **http://127.0.0.1:8000/admin/**

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin@12345` |

### Admin Capabilities:
- ➕ Add / edit / delete products with image upload
- 📦 View and manage all orders
- 💳 Track payment status (Pending / Paid / Failed)
- 🏷️ Update order status (Pending → Confirmed → Shipped → Delivered)
- 📂 Manage categories
- ⭐ Manage testimonials
- 👥 View customers

---

## 💳 Razorpay Integration

### Test Mode Setup

1. Create a free account at [razorpay.com](https://razorpay.com)
2. Go to **Settings → API Keys → Generate Test Key**
3. Copy your **Key ID** and **Key Secret**
4. Update in `settings.py` or `.env`:

```python
RAZORPAY_KEY_ID = 'rzp_test_xxxxxxxxxx'
RAZORPAY_KEY_SECRET = 'xxxxxxxxxxxxxxxxxx'
```

### Test Card Details (Razorpay)

| Field | Value |
|-------|-------|
| Card Number | 4111 1111 1111 1111 |
| Expiry | Any future date |
| CVV | Any 3 digits |
| OTP | 1234 5678 |

### UPI Test
- Use UPI ID: `success@razorpay`

### Payment Flow

```
User browses products
    ↓
Add to Cart
    ↓
Checkout (Enter delivery details)
    ↓
Place Order (Order created in DB with status: Pending)
    ↓
Razorpay Payment Page
    ↓
Payment Success → Signature Verified → Order Confirmed
    ↓
Order Confirmation Page (Order ID, Payment ID shown)
    ↓
Admin can view in /admin/orders/order/
```

---

## 🌐 Website Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Hero, featured products, categories, testimonials |
| Products | `/products/` | All products with category filter & search |
| Product Detail | `/products/<slug>/` | Images, description, add to cart |
| Cart | `/cart/` | Items, quantities, order summary |
| Checkout | `/orders/checkout/` | Delivery address form |
| Payment | `/payments/initiate/<id>/` | Razorpay payment gateway |
| Confirmation | `/orders/confirmation/<id>/` | Order success page |
| Login | `/users/login/` | User login |
| Register | `/users/register/` | User registration |
| Admin | `/admin/` | Django admin panel |

---

## 🗃️ Database Models

### Category
```
name, slug, image, description, created_at
```

### Product
```
category (FK), name, slug, description,
price, offer_price, image,
stock_quantity, is_featured, is_active,
created_at, updated_at
```

### Cart / CartItem
```
Cart: session_key, timestamps
CartItem: cart (FK), product (FK), quantity
```

### Order
```
order_id (UUID), customer_name, customer_email,
customer_phone, address, city, state, pincode,
total_price, payment_id, razorpay_order_id,
payment_status, order_status, created_at
```

### OrderItem
```
order (FK), product (FK), product_name,
product_price, quantity
```

### Payment
```
order (OneToOne), razorpay_order_id,
razorpay_payment_id, razorpay_signature,
amount, status, timestamps
```

---

## 🔒 Security Features

- ✅ Django CSRF protection on all forms
- ✅ Razorpay signature verification (HMAC-SHA256)
- ✅ Session-based cart (no login required to shop)
- ✅ Django's built-in XSS protection
- ✅ Parameterized queries (ORM, no raw SQL injection risk)
- ✅ Admin panel restricted with authentication

---

## 📱 Responsive Design

- ✅ Mobile-first Bootstrap 5 grid
- ✅ Hamburger navigation on mobile
- ✅ Fluid product grids (4-col → 2-col → 1-col)
- ✅ Touch-friendly cart quantity controls
- ✅ Readable checkout form on all screen sizes

---

## 🚀 Production Deployment

### Environment Variables for Production

```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-very-long-secret-key-here
DB_NAME=isha_return_gifts
DB_USER=db_user
DB_PASSWORD=strong_password
DB_HOST=your-db-host
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxx
```

### With Gunicorn + Nginx

```bash
# Install gunicorn (already in requirements.txt)
gunicorn isha_return_gifts.wsgi:application --bind 0.0.0.0:8000

# Serve static files with Nginx or WhiteNoise
python manage.py collectstatic
```

---

## 📞 Support Contact

**Isha Return Gifts**
- 📍 123, Gandhi Nagar, Chennai – 600001, Tamil Nadu
- 📞 +91 98765 43210
- 📧 hello@ishareturnGifts.com

---

*Built with ❤️ for beautiful celebrations across India*
