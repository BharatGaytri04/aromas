# Docker Deployment Guide

This guide will help you deploy your Aromas by Harnoor e-commerce platform using Docker on your server.

## Prerequisites

- Server with Docker and Docker Compose installed
- Domain name (optional, but recommended)
- SSH access to your server

## Step 1: Install Docker on Your Server

### For Ubuntu/Debian:
```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install -y docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
```

### For CentOS/RHEL:
```bash
# Install Docker
sudo yum install -y docker docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

## Step 2: Clone Repository on Server

```bash
# Navigate to your desired directory
cd /var/www  # or wherever you want to deploy

# Clone your repository
git clone https://github.com/BharatGaytri04/aromas.git
cd aromas
```

## Step 3: Configure Environment Variables

```bash
# Copy the example env file
cp env.example .env

# Edit the .env file with your settings
nano .env
```

### Required .env Configuration:

```env
# Django Settings
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False

# Database (PostgreSQL - handled by Docker)
DB_NAME=aromas_db
DB_USER=aromas_user
DB_PASSWORD=change-this-to-strong-password
DB_HOST=db
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=aromasbyharnoor@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=aromasbyharnoor@gmail.com

# Domain Configuration
ALLOWED_HOSTS=aromasbyharnoor.com,www.aromasbyharnoor.com,server-ip-address
ADMIN_URL=secure-admin/

# Optional: Razorpay (if enabled)
RAZORPAY_ENABLED=False
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
```

**Important:**
- Generate a strong SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- Use Gmail App Password (not regular password) for EMAIL_HOST_PASSWORD
- Domain is configured as `aromasbyharnoor.com` (update if needed)
- Use a strong database password

## Step 4: Update Docker Compose for Production

Edit `docker-compose.yml` and update the database password to match your `.env` file:

```yaml
db:
  environment:
    - POSTGRES_PASSWORD=your-strong-password-here  # Match DB_PASSWORD in .env
```

## Step 5: Build and Start Containers

```bash
# Build and start all services
docker-compose up -d --build

# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f
```

## Step 6: Run Migrations and Create Superuser

```bash
# Run database migrations
docker-compose exec web python manage.py migrate

# Create superuser (admin account)
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## Step 7: Configure DNS for Your Domain

Before your domain works, you need to configure DNS records:

### DNS Configuration at Your Domain Registrar

1. **A Record** (for `aromasbyharnoor.com`):
   - Type: `A`
   - Name: `@` or `aromasbyharnoor.com`
   - Value: Your server's IP address
   - TTL: 3600 (or default)

2. **A Record** (for `www.aromasbyharnoor.com`):
   - Type: `A`
   - Name: `www`
   - Value: Your server's IP address
   - TTL: 3600 (or default)

3. **Wait for DNS propagation** (can take 24-48 hours, usually faster)

### Verify DNS is Working

```bash
# Check if DNS is pointing to your server
nslookup aromasbyharnoor.com
ping aromasbyharnoor.com
```

## Step 8: Configure Nginx for Your Domain

The nginx configuration is already set for `aromasbyharnoor.com`. To enable HTTPS:

1. Uncomment the HTTPS server block in `nginx.conf`
2. The `server_name` is already set to `aromasbyharnoor.com www.aromasbyharnoor.com`
3. Add SSL certificates to `./ssl/` directory (use Let's Encrypt/Certbot)
4. Restart nginx: `docker-compose restart nginx`

### Setting up SSL with Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate SSL certificate
sudo certbot certonly --standalone -d aromasbyharnoor.com -d www.aromasbyharnoor.com

# Copy certificates to your project
sudo mkdir -p ./ssl
sudo cp /etc/letsencrypt/live/aromasbyharnoor.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/aromasbyharnoor.com/privkey.pem ./ssl/key.pem
sudo chown $USER:$USER ./ssl/*.pem

# Uncomment HTTPS server block in nginx.conf
# Restart nginx
docker-compose restart nginx
```

## Step 9: Access Your Application

- **Website:** http://aromasbyharnoor.com (or http://your-server-ip:8000)
- **Admin Panel:** http://aromasbyharnoor.com/secure-admin/
- **Seller Dashboard:** http://aromasbyharnoor.com/seller/dashboard/

## Common Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f web

# Access Django shell
docker-compose exec web python manage.py shell

# Run management commands
docker-compose exec web python manage.py <command>

# Update code (after git pull)
docker-compose up -d --build

# Backup database
docker-compose exec db pg_dump -U aromas_user aromas_db > backup.sql

# Restore database
docker-compose exec -T db psql -U aromas_user aromas_db < backup.sql
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs web

# Check if port 8000 is already in use
sudo netstat -tulpn | grep 8000
```

### Database connection errors
- Verify DB_PASSWORD in `.env` matches docker-compose.yml
- Check if database container is running: `docker-compose ps`
- Wait for database to be ready: `docker-compose logs db`

### Static files not loading
```bash
# Collect static files again
docker-compose exec web python manage.py collectstatic --noinput
```

### Permission errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## Security Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong `SECRET_KEY`
- [ ] Use strong database password
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use Gmail App Password (not regular password)
- [ ] Change default `ADMIN_URL` (already set to `secure-admin/`)
- [ ] Set up SSL/HTTPS for production
- [ ] Regularly update Docker images: `docker-compose pull`

## Updating Your Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Run migrations if needed
docker-compose exec web python manage.py migrate
```

## Backup Strategy

### Daily Database Backup (Add to crontab)
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * cd /var/www/aromas && docker-compose exec -T db pg_dump -U aromas_user aromas_db > backups/backup_$(date +\%Y\%m\%d).sql
```

## Support

For issues or questions, contact: aromasbyharnoor@gmail.com

