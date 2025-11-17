# ⚡ Quick Deployment Checklist for treandy.in

## 🎯 Choose Your Deployment Method

### Option A: VPS (Full Control) - Recommended
- **Cost**: $5-10/month
- **Difficulty**: Medium
- **Follow**: `DEPLOYMENT_GUIDE.md` → Option 1

### Option B: Platform Service (Easier)
- **Cost**: Free tier available
- **Difficulty**: Easy
- **Follow**: `DEPLOYMENT_GUIDE.md` → Option 2

---

## 📋 Pre-Deployment Checklist

### 1. Update Settings for Production

Before deploying, update `aromas/settings.py`:

```python
# Change these:
DEBUG = False
ALLOWED_HOSTS = ['treandy.in', 'www.treandy.in']

# Generate new SECRET_KEY (don't use the development one!)
# Run: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Install Production Dependencies

```bash
pip install -r requirements.txt
```

### 3. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

---

## 🚀 Quick Deploy Commands

### For VPS Deployment:

```bash
# 1. Generate environment file
python deploy_setup.py

# 2. Update .env with your actual values

# 3. Run migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Test locally first
python manage.py runserver

# 6. Deploy to server (see DEPLOYMENT_GUIDE.md)
```

### For Platform Services (Railway/Render):

1. Push code to GitHub
2. Connect repository to platform
3. Set environment variables:
   - `SECRET_KEY` (generate new one)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=treandy.in,www.treandy.in`
4. Add custom domain: `treandy.in`
5. Configure DNS as instructed

---

## 🔐 Security Reminders

- ✅ Never commit `.env` file to Git
- ✅ Use strong SECRET_KEY (different from development)
- ✅ Set `DEBUG=False` in production
- ✅ Use HTTPS (SSL certificate)
- ✅ Keep dependencies updated
- ✅ Use strong database passwords

---

## 📝 DNS Configuration

At your domain registrar (where you bought treandy.in):

**For VPS:**
- Type: A Record
- Name: `@` (or blank)
- Value: Your server IP address

- Type: A Record  
- Name: `www`
- Value: Your server IP address

**For Platform Services:**
- Follow their DNS instructions (usually CNAME records)

---

## ✅ Post-Deployment

1. Test your site: `https://treandy.in`
2. Test admin: `https://treandy.in/admin`
3. Check static files are loading
4. Test all pages work
5. Set up monitoring (optional)

---

## 🆘 Common Issues

**Site shows "DisallowedHost" error:**
→ Update `ALLOWED_HOSTS` in settings.py

**Static files not loading:**
→ Run `python manage.py collectstatic --noinput`

**Database errors:**
→ Check database credentials in `.env`

**SSL certificate issues:**
→ Make sure DNS is properly configured first

---

**Need detailed instructions?** See `DEPLOYMENT_GUIDE.md`

