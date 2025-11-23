# Error Handling Guide - Hide Errors on Production

This guide explains how to control error display: **show detailed errors locally** (http://127.0.0.1:8000) but **hide them on production** (aromasbyharnoor.com).

## ✅ Method 1: Using .env File (RECOMMENDED)

This is the **easiest and most reliable** method.

### For Local Development (http://127.0.0.1:8000):
In your local `.env` file, add:
```env
DEBUG=True
```

### For Production Server (aromasbyharnoor.com):
On your VPS, in `/var/www/aromas/.env`, set:
```env
DEBUG=False
```

**How it works:**
- When `DEBUG=True`: Shows detailed error pages with full stack traces (for development)
- When `DEBUG=False`: Shows user-friendly error pages (for production)

---

## ✅ Method 2: Automatic Detection (Already Implemented)

The settings are already configured to read from `.env`:
- If `DEBUG` is set in `.env`, it uses that value
- Default is `True` (safe for development)

**Current Setup:**
```python
# In aromas/settings.py
DEBUG = env_bool('DEBUG', True)  # Reads from .env, defaults to True
```

---

## 📋 Steps to Configure

### Step 1: Local Development (.env file)
Your local `.env` should have:
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*
```

### Step 2: Production Server (.env file)
On VPS (`/var/www/aromas/.env`), set:
```env
DEBUG=False
ALLOWED_HOSTS=aromasbyharnoor.com,www.aromasbyharnoor.com,193.203.162.238
```

### Step 3: Restart Services
After changing `.env` on VPS:
```bash
sudo systemctl restart aromas
```

---

## 🎨 Custom Error Pages

Custom error pages have been created:
- `templates/404.html` - Page Not Found
- `templates/500.html` - Server Error

These will automatically show when `DEBUG=False` in production.

---

## 🔍 How to Verify

### Check Current DEBUG Status:
```bash
# On VPS
cd /var/www/aromas
source venv/bin/activate
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)
False  # Should be False on production
```

### Test Error Pages:
1. **Local (DEBUG=True)**: Visit a non-existent page → See detailed error
2. **Production (DEBUG=False)**: Visit a non-existent page → See friendly 404 page

---

## ⚠️ Important Notes

1. **Never set DEBUG=True in production** - It exposes sensitive information
2. **Always use .env file** - Never hardcode DEBUG in settings.py
3. **Restart after changes** - Always restart Gunicorn after changing .env
4. **Check .env file** - Make sure `.env` file exists and has correct values

---

## 🛠️ Troubleshooting

### Problem: Still seeing detailed errors on production
**Solution:**
```bash
# On VPS, check .env file
cat /var/www/aromas/.env | grep DEBUG

# Should show: DEBUG=False
# If not, edit it:
nano /var/www/aromas/.env
# Set: DEBUG=False
# Save and restart:
sudo systemctl restart aromas
```

### Problem: Not seeing errors locally
**Solution:**
```bash
# Check local .env file
# Should have: DEBUG=True
```

---

## 📝 Summary

| Location | DEBUG Value | Error Display |
|----------|-------------|---------------|
| Local (127.0.0.1:8000) | `True` | Detailed errors with stack traces |
| Production (aromasbyharnoor.com) | `False` | User-friendly error pages |

**Remember:** Always check your `.env` file on both local and production!

