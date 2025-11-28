# 🔧 Fix Razorpay "Authentication failed" Error

## Problem
The logs show: `Razorpay order creation error: Authentication failed`

This means your Razorpay API keys are either:
1. ❌ Incorrect (wrong keys)
2. ❌ Not loaded from .env file
3. ❌ Have extra spaces or formatting issues
4. ❌ Test keys used in live mode (or vice versa)

---

## Quick Fix Steps

### Step 1: Navigate to Project Directory

On your VPS, run:
```bash
cd /var/www/aromas
```

### Step 2: Check Your .env File

```bash
nano /var/www/aromas/.env
```

**Verify these lines exist and are correct:**
```env
RAZORPAY_ENABLED=True
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_secret_key_here
RAZORPAY_CURRENCY=INR
```

**Important:**
- ✅ No spaces around `=` sign
- ✅ No quotes around values
- ✅ Use LIVE keys for production (starts with `rzp_live_`)
- ✅ Use TEST keys only for testing (starts with `rzp_test_`)

### Step 3: Run Diagnostic Script

```bash
cd /var/www/aromas
source venv/bin/activate
python3 check_razorpay_auth.py
```

This will:
- ✅ Check if keys are loaded
- ✅ Verify key format
- ✅ Test authentication with Razorpay
- ✅ Show specific error if authentication fails

### Step 4: If Keys Are Wrong

1. **Go to Razorpay Dashboard:**
   - Login: https://dashboard.razorpay.com
   - Go to: Settings → API Keys

2. **Copy the correct keys:**
   - For **LIVE** mode: Use "Key ID" and "Key Secret" from "Live Mode" section
   - For **TEST** mode: Use "Key ID" and "Key Secret" from "Test Mode" section

3. **Update .env file:**
   ```bash
   nano /var/www/aromas/.env
   ```
   
   Update these lines:
   ```env
   RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
   RAZORPAY_KEY_SECRET=your_actual_secret_key
   ```

4. **Restart the service:**
   ```bash
   sudo systemctl restart aromas
   ```

5. **Test again:**
   ```bash
   python3 check_razorpay_auth.py
   ```

---

## Common Issues

### Issue 1: "Command 'python' not found"
**Solution:** Use `python3` instead of `python`
```bash
python3 check_razorpay_auth.py
```

### Issue 2: "venv/bin/activate: No such file or directory"
**Solution:** Navigate to project directory first
```bash
cd /var/www/aromas
source venv/bin/activate
```

### Issue 3: Keys have extra spaces
**Solution:** The code now automatically trims spaces, but check your .env file:
```env
# ❌ WRONG (has spaces)
RAZORPAY_KEY_ID = rzp_live_xxxxx

# ✅ CORRECT (no spaces)
RAZORPAY_KEY_ID=rzp_live_xxxxx
```

### Issue 4: Using Test Keys in Production
**Solution:** Make sure you're using LIVE keys for production:
- Test keys start with: `rzp_test_`
- Live keys start with: `rzp_live_`

### Issue 5: Keys Not Loading
**Solution:** Check if .env file is in correct location:
```bash
ls -la /var/www/aromas/.env
cat /var/www/aromas/.env | grep RAZORPAY
```

---

## Verify Keys Are Loaded

Run this command to check if Django can see the keys:
```bash
cd /var/www/aromas
source venv/bin/activate
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aromas.settings')
django.setup()
from django.conf import settings
key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
print('Key ID:', key_id[:20] + '...' if key_id else 'NOT SET')
print('Key Secret:', 'SET' if getattr(settings, 'RAZORPAY_KEY_SECRET', '') else 'NOT SET')
"
```

---

## After Fixing

1. **Restart the service:**
   ```bash
   sudo systemctl restart aromas
   ```

2. **Check logs:**
   ```bash
   sudo journalctl -u aromas -f
   ```

3. **Test payment on your website:**
   - Go to checkout
   - Click "Place Order"
   - Razorpay payment modal should open

---

## Still Not Working?

If authentication still fails after checking everything:

1. **Double-check keys in Razorpay Dashboard:**
   - Make sure you copied the FULL key (no truncation)
   - Verify you're using the correct mode (Live vs Test)

2. **Check .env file syntax:**
   ```bash
   cat /var/www/aromas/.env | grep RAZORPAY
   ```

3. **Verify service is reading .env:**
   ```bash
   sudo systemctl restart aromas
   sudo journalctl -u aromas -n 50
   ```

4. **Contact Razorpay Support:**
   - If keys are correct but still failing
   - Check if your Razorpay account is active
   - Verify account KYC status

---

## Quick Reference Commands

```bash
# Navigate to project
cd /var/www/aromas

# Activate virtual environment
source venv/bin/activate

# Run diagnostic
python3 check_razorpay_auth.py

# Check .env file
nano /var/www/aromas/.env

# Restart service
sudo systemctl restart aromas

# Check logs
sudo journalctl -u aromas -f
```

