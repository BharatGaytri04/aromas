# 💳 Complete Razorpay Payment Gateway Setup Guide

This guide will walk you through setting up Razorpay payment gateway for your Django e-commerce site.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Create Razorpay Account](#step-1-create-razorpay-account)
3. [Step 2: Get API Keys](#step-2-get-api-keys)
4. [Step 3: Install Razorpay Package](#step-3-install-razorpay-package)
5. [Step 4: Configure Environment Variables](#step-4-configure-environment-variables)
6. [Step 5: Verify Configuration](#step-5-verify-configuration)
7. [Step 6: Test Payment Flow](#step-6-test-payment-flow)
8. [Step 7: Go Live](#step-7-go-live)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Django project is set up and running
- You have access to your VPS/server
- Domain is configured with SSL (HTTPS)

---

## Step 1: Create Razorpay Account

1. **Sign up** at [https://razorpay.com](https://razorpay.com)
2. **Complete KYC** (Know Your Customer) verification:
   - Business details
   - Bank account information
   - Identity verification documents
3. **Wait for approval** (usually 24-48 hours)

---

## Step 2: Get API Keys

### For Testing (Test Mode)

1. Log in to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Go to **Settings** → **API Keys**
3. Click **Generate Test Key**
4. Copy the **Key ID** and **Key Secret**
   - Key ID starts with `rzp_test_...`
   - Key Secret is a long string

### For Production (Live Mode)

1. After KYC approval, go to **Settings** → **API Keys**
2. Click **Generate Live Key**
3. Copy the **Key ID** and **Key Secret**
   - Key ID starts with `rzp_live_...`
   - Key Secret is a long string

⚠️ **Important**: 
- **Test keys** are for development/testing only (no real money)
- **Live keys** process real payments
- Never share your keys publicly
- Keep keys secure in `.env` file (never commit to Git)

---

## Step 3: Install Razorpay Package

### On Local Development Machine

```bash
# Navigate to your project directory
cd "D:\Aromas by harnoor"

# Activate virtual environment (if using one)
# For Windows:
venv\Scripts\activate

# Install razorpay package
pip install razorpay==1.4.2

# Or install all requirements
pip install -r requirements.txt
```

### On VPS/Server

```bash
# SSH into your server
ssh root@your_server_ip

# Navigate to project directory
cd /var/www/aromas

# Activate virtual environment
source venv/bin/activate

# Install razorpay package
pip install razorpay==1.4.2

# Verify installation
pip list | grep razorpay
# Should show: razorpay 1.4.2
```

---

## Step 4: Configure Environment Variables

### On Local Development (Windows)

1. **Open `.env` file** in your project root:
   ```bash
   # In your project root: D:\Aromas by harnoor\.env
   ```

2. **Add these lines**:
   ```env
   # Razorpay Configuration (Test Mode for Development)
   RAZORPAY_ENABLED=True
   RAZORPAY_KEY_ID=rzp_test_YOUR_TEST_KEY_ID_HERE
   RAZORPAY_KEY_SECRET=YOUR_TEST_KEY_SECRET_HERE
   RAZORPAY_CURRENCY=INR
   ```

3. **Replace** `YOUR_TEST_KEY_ID_HERE` and `YOUR_TEST_KEY_SECRET_HERE` with your actual test keys

### On VPS/Server (Production)

1. **SSH into your server**:
   ```bash
   ssh root@your_server_ip
   ```

2. **Navigate to project directory**:
   ```bash
   cd /var/www/aromas
   ```

3. **Edit `.env` file**:
   ```bash
   nano .env
   ```

4. **Add these lines** (use **LIVE keys** for production):
   ```env
   # Razorpay Configuration (Live Mode for Production)
   RAZORPAY_ENABLED=True
   RAZORPAY_KEY_ID=rzp_live_YOUR_LIVE_KEY_ID_HERE
   RAZORPAY_KEY_SECRET=YOUR_LIVE_KEY_SECRET_HERE
   RAZORPAY_CURRENCY=INR
   ```

5. **Save and exit**:
   - Press `Ctrl + X`
   - Press `Y` to confirm
   - Press `Enter` to save

6. **Verify the configuration**:
   ```bash
   cat .env | grep RAZORPAY
   ```

   You should see:
   ```
   RAZORPAY_ENABLED=True
   RAZORPAY_KEY_ID=rzp_live_...
   RAZORPAY_KEY_SECRET=...
   RAZORPAY_CURRENCY=INR
   ```

---

## Step 5: Verify Configuration

### Check Django Settings

The Razorpay settings are already configured in `aromas/settings.py`:

```python
# Razorpay Settings
RAZORPAY_ENABLED = env_bool('RAZORPAY_ENABLED', False)
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
RAZORPAY_CURRENCY = os.environ.get('RAZORPAY_CURRENCY', 'INR')
```

### Verify on VPS

1. **Restart Gunicorn service** (to load new environment variables):
   ```bash
   sudo systemctl restart aromas
   ```

2. **Check service status**:
   ```bash
   sudo systemctl status aromas
   ```

3. **Test in Django shell** (optional):
   ```bash
   cd /var/www/aromas
   source venv/bin/activate
   python manage.py shell
   ```

   Then in the shell:
   ```python
   from django.conf import settings
   print("Razorpay Enabled:", settings.RAZORPAY_ENABLED)
   print("Key ID:", settings.RAZORPAY_KEY_ID[:10] + "..." if settings.RAZORPAY_KEY_ID else "Not set")
   print("Currency:", settings.RAZORPAY_CURRENCY)
   ```

   Expected output:
   ```
   Razorpay Enabled: True
   Key ID: rzp_live_...
   Currency: INR
   ```

---

## Step 6: Test Payment Flow

### Test on Local Development

1. **Start Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Open browser**: `http://127.0.0.1:8000`

3. **Test checkout flow**:
   - Add products to cart
   - Go to checkout
   - Select **"Pay Online (Razorpay)"**
   - Fill in shipping details
   - Click **"Place Order"**

4. **Razorpay test card** (for test mode):
   - **Card Number**: `4111 1111 1111 1111`
   - **Expiry**: Any future date (e.g., `12/25`)
   - **CVV**: Any 3 digits (e.g., `123`)
   - **Name**: Any name

5. **Verify payment**:
   - Payment should complete successfully
   - Order should be created in database
   - You should see order success page

### Test on Production (VPS)

1. **Visit your live site**: `https://aromasbyharnoor.com`

2. **Test with small amount first** (if using live keys)

3. **Use real payment method** (if using live keys) or test card (if still in test mode)

4. **Check order in admin panel**:
   - Go to: `https://aromasbyharnoor.com/admin/`
   - Navigate to **Orders** → **Orders**
   - Verify order is created with payment status

---

## Step 7: Go Live

### Switch from Test to Live Keys

1. **Complete KYC** on Razorpay dashboard

2. **Generate Live Keys**:
   - Go to Razorpay Dashboard → Settings → API Keys
   - Click **Generate Live Key**
   - Copy Key ID and Key Secret

3. **Update `.env` on VPS**:
   ```bash
   cd /var/www/aromas
   nano .env
   ```

   Update to:
   ```env
   RAZORPAY_ENABLED=True
   RAZORPAY_KEY_ID=rzp_live_YOUR_ACTUAL_LIVE_KEY_ID
   RAZORPAY_KEY_SECRET=YOUR_ACTUAL_LIVE_KEY_SECRET
   RAZORPAY_CURRENCY=INR
   ```

4. **Restart service**:
   ```bash
   sudo systemctl restart aromas
   ```

5. **Test with real payment** (small amount first)

---

## Troubleshooting

### Issue: "Failed to initialize payment"

**Possible causes:**
1. Razorpay package not installed
2. Keys not configured in `.env`
3. Service not restarted after configuration change

**Solutions:**
```bash
# 1. Check if package is installed
pip list | grep razorpay

# 2. Verify .env file
cat .env | grep RAZORPAY

# 3. Restart service
sudo systemctl restart aromas

# 4. Check logs
sudo journalctl -u aromas -f
```

### Issue: "Razorpay is not enabled"

**Solution:**
- Check `.env` file has `RAZORPAY_ENABLED=True`
- Restart Gunicorn service

### Issue: Payment succeeds but order not created

**Solution:**
- Check Gunicorn logs: `sudo journalctl -u aromas -f`
- Verify database connection
- Check order creation in `orders/views.py`

### Issue: "Invalid API key"

**Solution:**
- Verify keys are correct (no extra spaces)
- Check if using test keys in production (or vice versa)
- Regenerate keys in Razorpay dashboard if needed

### Issue: Payment modal doesn't open

**Solution:**
- Check browser console for JavaScript errors (F12)
- Verify Razorpay SDK is loaded: `https://checkout.razorpay.com/v1/checkout.js`
- Check network tab for failed requests

### Check Payment Status in Razorpay Dashboard

1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Navigate to **Payments** → **All Payments**
3. You should see all payment attempts
4. Check payment status and details

---

## Security Best Practices

1. ✅ **Never commit `.env` file to Git**
   - Add `.env` to `.gitignore`
   - Use different keys for development and production

2. ✅ **Use HTTPS in production**
   - Razorpay requires HTTPS for live payments
   - SSL certificate must be valid

3. ✅ **Keep keys secure**
   - Don't share keys publicly
   - Rotate keys if compromised
   - Use environment variables, not hardcoded values

4. ✅ **Verify payment signatures**
   - Always verify payment on server side
   - Don't trust client-side payment data

5. ✅ **Monitor payments**
   - Regularly check Razorpay dashboard
   - Set up webhooks for payment notifications
   - Review failed payments

---

## Payment Flow Overview

1. **Customer selects Razorpay** at checkout
2. **Order is created** (but not finalized)
3. **Razorpay order is created** via API
4. **Payment modal opens** with Razorpay checkout
5. **Customer completes payment** on Razorpay
6. **Payment callback** verifies payment signature
7. **Order is finalized** and marked as paid
8. **Invoice email** is sent to customer
9. **Admin is notified** of new order

---

## Additional Resources

- **Razorpay Documentation**: https://razorpay.com/docs/
- **Razorpay Dashboard**: https://dashboard.razorpay.com
- **Support**: support@razorpay.com
- **API Reference**: https://razorpay.com/docs/api/

---

## Quick Reference Commands

### Check Razorpay Status
```bash
# On VPS
cd /var/www/aromas
source venv/bin/activate
python manage.py shell
```

```python
from django.conf import settings
from orders.payment_utils import is_razorpay_enabled
print("Enabled:", is_razorpay_enabled())
print("Key ID:", settings.RAZORPAY_KEY_ID[:15] + "..." if settings.RAZORPAY_KEY_ID else "Not set")
```

### View Recent Payments
```bash
# In Django shell
from orders.models import Payment
recent_payments = Payment.objects.filter(payment_method='RAZORPAY').order_by('-created_at')[:5]
for p in recent_payments:
    print(f"{p.payment_id} - {p.status} - ₹{p.amount_paid}")
```

---

## ✅ Setup Checklist

- [ ] Razorpay account created and KYC completed
- [ ] API keys generated (test and live)
- [ ] Razorpay package installed (`pip install razorpay==1.4.2`)
- [ ] Environment variables configured in `.env`
- [ ] Service restarted on VPS
- [ ] Test payment completed successfully
- [ ] Live keys configured (for production)
- [ ] Payment flow tested end-to-end
- [ ] Order creation verified
- [ ] Email notifications working

---

**Need Help?** Check the troubleshooting section or review the code in:
- `orders/payment_utils.py` - Payment utilities
- `orders/views.py` - Payment views
- `cart/views.py` - Checkout flow
- `templates/store/checkout.html` - Checkout template

