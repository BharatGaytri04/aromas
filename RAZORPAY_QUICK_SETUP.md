# ⚡ Razorpay Quick Setup Checklist

## 🚀 5-Minute Setup Guide

### Step 1: Get API Keys (2 minutes)

1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. **Settings** → **API Keys**
3. Click **Generate Test Key** (for testing) or **Generate Live Key** (for production)
4. Copy **Key ID** and **Key Secret**

### Step 2: Install Package (1 minute)

**On VPS:**
```bash
cd /var/www/aromas
source venv/bin/activate
pip install razorpay==1.4.2
```

### Step 3: Configure .env (1 minute)

**On VPS:**
```bash
cd /var/www/aromas
nano .env
```

**Add these lines:**
```env
RAZORPAY_ENABLED=True
RAZORPAY_KEY_ID=rzp_test_YOUR_KEY_ID_HERE
RAZORPAY_KEY_SECRET=YOUR_KEY_SECRET_HERE
RAZORPAY_CURRENCY=INR
```

**Save:** `Ctrl+X`, then `Y`, then `Enter`

### Step 4: Restart Service (30 seconds)

```bash
sudo systemctl restart aromas
sudo systemctl status aromas
```

### Step 5: Verify (30 seconds)

```bash
cat .env | grep RAZORPAY
```

Should show:
```
RAZORPAY_ENABLED=True
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_CURRENCY=INR
```

---

## ✅ Done! 

Now test the payment:
1. Go to your website
2. Add items to cart
3. Checkout → Select "Pay Online (Razorpay)"
4. Complete payment

---

## 🔄 Switch to Live Keys (When Ready)

1. Complete KYC on Razorpay
2. Generate Live Keys in dashboard
3. Update `.env` with live keys:
   ```env
   RAZORPAY_KEY_ID=rzp_live_YOUR_LIVE_KEY_ID
   RAZORPAY_KEY_SECRET=YOUR_LIVE_KEY_SECRET
   ```
4. Restart: `sudo systemctl restart aromas`

---

## 🐛 Quick Troubleshooting

**Payment not working?**
```bash
# Check if package installed
pip list | grep razorpay

# Check .env file
cat .env | grep RAZORPAY

# Check service logs
sudo journalctl -u aromas -f
```

**Need more details?** See `RAZORPAY_SETUP_GUIDE.md`

