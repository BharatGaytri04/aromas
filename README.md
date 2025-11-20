# Aromas by Harnoor - E-commerce Platform

A full-featured e-commerce platform built with Django.

## Features

- 🛒 Shopping cart and checkout
- 💳 Payment integration (Razorpay ready)
- 📦 Order management system
- ⭐ Product reviews and ratings
- 👤 User accounts and profiles
- 🎁 Coupons and discounts
- 🏪 Seller dashboard
- 📧 Email notifications
- 🔒 Secure admin panel

## Tech Stack

- Django 5.2.8
- PostgreSQL (production)
- SQLite (development)
- Gunicorn
- Nginx
- Docker & Docker Compose

## Quick Start with Docker

### Prerequisites

- Docker
- Docker Compose

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "Aromas by harnoor"
   ```

2. **Create `.env` file**
   ```bash
   cp env.example .env
   ```
   Then edit `.env` and add your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   
   # Database (PostgreSQL - handled by Docker)
   DB_NAME=aromas_db
   DB_USER=aromas_user
   DB_PASSWORD=aromas_password
   DB_HOST=db
   DB_PORT=5432
   
   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   
   # Domain
   ALLOWED_HOSTS=aromasbyharnoor.com,www.aromasbyharnoor.com
   ADMIN_URL=secure-admin/
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

4. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**
   - Website: http://localhost:8000
   - Admin Panel: http://localhost:8000/secure-admin/ (or your ADMIN_URL)
   - Seller Dashboard: http://localhost:8000/seller/dashboard/

## Development Setup (Without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Access Django shell
docker-compose exec web python manage.py shell
```

## Production Deployment

1. Update `ALLOWED_HOSTS` in `.env`
2. Set `DEBUG=False` in `.env`
3. Configure SSL certificates in `nginx.conf`
4. Update database credentials in `docker-compose.yml` and `.env`
5. Run `docker-compose up -d --build`

## Project Structure

```
aromas/
├── accounts/          # User authentication & profiles
├── store/            # Products & categories
├── cart/             # Shopping cart
├── orders/           # Order management
├── reviews/          # Product reviews
├── seller/           # Seller dashboard
├── notifications/   # Email notifications
├── coupons/          # Discount coupons
└── loyalty/          # Loyalty program
```

## Environment Variables

See `env.example` for all required environment variables.

## License

Private - All rights reserved

## Support

For support, email aromasbyharnoor@gmail.com

