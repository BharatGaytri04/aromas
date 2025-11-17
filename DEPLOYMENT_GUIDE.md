# 🚀 Deployment Guide for treandy.in

This guide will help you deploy your Django application to your domain **treandy.in**.

## 📋 Prerequisites

1. **Domain**: You have `treandy.in` registered
2. **Hosting**: Choose one of these options:
   - **VPS** (DigitalOcean, Linode, AWS EC2, etc.) - Recommended
   - **Platform as a Service** (Heroku, Railway, Render, etc.) - Easier
   - **Shared Hosting** (if it supports Python/Django)

## 🎯 Option 1: VPS Deployment (Recommended)

### Step 1: Set Up Your Server

1. **Get a VPS** (Ubuntu 22.04 recommended):
   - DigitalOcean: $6/month
   - Linode: $5/month
   - AWS EC2: Pay as you go

2. **Connect to your server**:
   ```bash
   ssh root@your_server_ip
   ```

3. **Update system**:
   ```bash
   apt update && apt upgrade -y
   ```

### Step 2: Install Required Software

```bash
# Install Python and pip
apt install python3 python3-pip python3-venv nginx -y

# Install PostgreSQL (recommended for production)
apt install postgresql postgresql-contrib -y

# Install Certbot for SSL
apt install certbot python3-certbot-nginx -y
```

### Step 3: Set Up Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE aromas_db;
CREATE USER aromas_user WITH PASSWORD 'your_secure_password';
ALTER ROLE aromas_user SET client_encoding TO 'utf8';
ALTER ROLE aromas_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE aromas_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE aromas_db TO aromas_user;
\q
```

### Step 4: Deploy Your Code

```bash
# Create a directory for your app
mkdir -p /var/www/aromas
cd /var/www/aromas

# Clone your repository or upload files
# If using Git:
git clone your_repository_url .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Django Settings

1. **Create environment file**:
   ```bash
   nano /var/www/aromas/.env
   ```

2. **Add these variables**:
   ```env
   SECRET_KEY=your_new_secret_key_here
   DEBUG=False
   DB_NAME=aromas_db
   DB_USER=aromas_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. **Update settings.py** to use environment variables:
   ```python
   import os
   from pathlib import Path
   from dotenv import load_dotenv  # pip install python-dotenv
   
   load_dotenv()
   
   SECRET_KEY = os.environ.get('SECRET_KEY')
   DEBUG = os.environ.get('DEBUG', 'False') == 'True'
   ALLOWED_HOSTS = ['treandy.in', 'www.treandy.in']
   ```

### Step 6: Run Migrations and Collect Static Files

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Step 7: Set Up Gunicorn

1. **Create Gunicorn service file**:
   ```bash
   nano /etc/systemd/system/aromas.service
   ```

2. **Add this content**:
   ```ini
   [Unit]
   Description=Gunicorn daemon for aromas
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/aromas
   ExecStart=/var/www/aromas/venv/bin/gunicorn \
       --access-logfile - \
       --workers 3 \
       --bind unix:/var/www/aromas/aromas.sock \
       aromas.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start the service**:
   ```bash
   systemctl daemon-reload
   systemctl start aromas
   systemctl enable aromas
   ```

### Step 8: Configure Nginx

1. **Create Nginx configuration**:
   ```bash
   nano /etc/nginx/sites-available/treandy.in
   ```

2. **Add this configuration**:
   ```nginx
   server {
       listen 80;
       server_name treandy.in www.treandy.in;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /var/www/aromas;
       }
       
       location /media/ {
           root /var/www/aromas;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/aromas/aromas.sock;
       }
   }
   ```

3. **Enable the site**:
   ```bash
   ln -s /etc/nginx/sites-available/treandy.in /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

### Step 9: Set Up SSL Certificate (HTTPS)

```bash
certbot --nginx -d treandy.in -d www.treandy.in
```

### Step 10: Configure DNS

In your domain registrar (where you bought treandy.in):

1. Add **A Record**:
   - Name: `@` or blank
   - Value: Your server IP address
   - TTL: 3600

2. Add **A Record** for www:
   - Name: `www`
   - Value: Your server IP address
   - TTL: 3600

Wait 5-30 minutes for DNS propagation, then your site should be live!

---

## 🎯 Option 2: Platform as a Service (Easier)

### Railway.app (Recommended for beginners)

1. **Sign up** at [railway.app](https://railway.app)
2. **Create new project** → Deploy from GitHub
3. **Add environment variables**:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=treandy.in,www.treandy.in`
4. **Add custom domain**: Settings → Domains → Add `treandy.in`
5. **Configure DNS** at your registrar:
   - Add CNAME: `treandy.in` → `your-app.railway.app`

### Render.com

1. **Sign up** at [render.com](https://render.com)
2. **Create Web Service** → Connect GitHub
3. **Build command**: `pip install -r requirements.txt`
4. **Start command**: `gunicorn aromas.wsgi:application`
5. **Add custom domain** in settings
6. **Configure DNS** as instructed

### Heroku

1. **Install Heroku CLI**
2. **Login**: `heroku login`
3. **Create app**: `heroku create aromas-treandy`
4. **Set config vars**:
   ```bash
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=treandy.in,www.treandy.in
   ```
5. **Deploy**: `git push heroku main`
6. **Add domain**: `heroku domains:add treandy.in`

---

## 🔒 Security Checklist

Before going live, make sure:

- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` is in environment variables (not in code)
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] SSL certificate is installed (HTTPS)
- [ ] Database password is strong
- [ ] Static files are collected (`collectstatic`)
- [ ] Media files are properly configured
- [ ] Firewall is configured (only allow 80, 443, 22)

---

## 📝 Quick Commands Reference

```bash
# Restart Gunicorn
sudo systemctl restart aromas

# Check Gunicorn status
sudo systemctl status aromas

# View Gunicorn logs
sudo journalctl -u aromas -f

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx configuration
sudo nginx -t

# Renew SSL certificate
sudo certbot renew
```

---

## 🆘 Troubleshooting

### Site not loading?
- Check DNS propagation: `nslookup treandy.in`
- Check server status: `systemctl status aromas`
- Check Nginx logs: `tail -f /var/log/nginx/error.log`

### Static files not loading?
- Run: `python manage.py collectstatic`
- Check Nginx static file configuration
- Check file permissions

### Database errors?
- Check PostgreSQL is running: `systemctl status postgresql`
- Verify database credentials in `.env`
- Run migrations: `python manage.py migrate`

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Need help?** Check Django logs, server logs, and ensure all services are running.

