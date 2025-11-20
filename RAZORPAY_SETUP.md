# 💳 Razorpay Payment Gateway Setup Guide

This guide will help you enable Razorpay payment gateway on your site.

## 📋 Current Status

- ✅ **Cash on Delivery (COD)** is currently active
- ⏳ **Razorpay** is ready but disabled (waiting for API keys)

## 🚀 How to Enable Razorpay

### Step 1: Get Razorpay Account

1. Go to [https://razorpay.com](https://razorpay.com)
2. Sign up for a free account
3. Complete KYC verification (required for live payments)

### Step 2: Get Your API Keys

1. Login to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Go to **Settings** → **API Keys**
3. Click **Generate Key** if you don't have keys yet
4. Copy your **Key ID** (starts with `rzp_`)
5. Copy your **Key Secret** (keep this secure!)

### Step 3: Install Razorpay Package

```bash
pip install razorpay==1.4.2
```

Or add to `requirements.txt`:
```
razorpay==1.4.2
```

### Step 4: Add Keys to Settings

Open `aromas/settings.py` and update:

```python
# Razorpay Settings
RAZORPAY_ENABLED = True  # Change from False to True
RAZORPAY_KEY_ID = 'rzp_test_xxxxxxxxxxxxx'  # Your Key ID
RAZORPAY_KEY_SECRET = 'your_secret_key_here'  # Your Key Secret
RAZORPAY_CURRENCY = 'INR'  # Currency code
```

### Step 5: Test Mode vs Live Mode

- **Test Mode**: Use test keys (start with `rzp_test_`)
  - No real money transactions
  - Perfect for testing
  - Use test card: `4111 1111 1111 1111`

- **Live Mode**: Use live keys (start with `rzp_live_`)
  - Real money transactions
  - Requires KYC verification
  - Use only after testing

### Step 6: Restart Server

After adding keys, restart your Django server:

```bash
python manage.py runserver
```

## ✅ Verification

1. Go to checkout page
2. You should now see **"Pay Online (Razorpay)"** option
3. Select it and place an order
4. You'll be redirected to Razorpay payment page

## 🔒 Security Notes

- ⚠️ **Never commit API keys to Git!**
- ✅ Use environment variables for production
- ✅ Keep Key Secret secure
- ✅ Use test keys for development

## 📝 Environment Variables (Recommended for Production)

Instead of hardcoding keys, use environment variables:

```python
# In settings.py
import os

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
```

Then set in your `.env` file:
```
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_secret_key_here
```

## 🧪 Testing

### Test Cards (Test Mode Only)

- **Success**: `4111 1111 1111 1111`
- **Failure**: `4000 0000 0000 0002`
- **CVV**: Any 3 digits
- **Expiry**: Any future date

### Test UPI IDs

- `success@razorpay`
- `failure@razorpay`

## 📞 Support

- Razorpay Docs: [https://razorpay.com/docs](https://razorpay.com/docs)
- Razorpay Support: [support@razorpay.com](mailto:support@razorpay.com)

## 🎯 What Happens After Payment?

1. Customer selects Razorpay payment
2. Order is created (with `is_ordered=False`)
3. Razorpay payment page opens
4. Customer completes payment
5. Payment is verified
6. Order status updated to `is_ordered=True`
7. Customer redirected to order success page
8. Admin gets notification

---

**Note**: The code is already set up and ready. Just add your keys and enable it! 🚀

