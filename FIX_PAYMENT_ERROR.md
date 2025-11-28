# 🔧 Fix Razorpay Payment Not Opening - Step by Step

## Problem
When customers click "Place Order", the Razorpay payment page is not opening and shows "Failed to initialize payment" error.

## ✅ Solution Steps (Run on Your VPS)

### Step 1: Pull Latest Code
```bash
cd /var/www/aromas
git pull origin main
```

### Step 2: Verify Razorpay Configuration
```bash
# Check if keys are set
cat .env | grep RAZORPAY

# Should show:
# RAZORPAY_ENABLED=True
# RAZORPAY_KEY_ID=rzp_live_...
# RAZORPAY_KEY_SECRET=...
# RAZORPAY_CURRENCY=INR
```

### Step 3: Run Diagnostic Script
```bash
source venv/bin/activate
python check_razorpay.py
```

This will show you exactly what's wrong.

### Step 4: Restart Gunicorn Service
```bash
sudo systemctl restart aromas
sudo systemctl status aromas
```

### Step 5: Check Service Logs
```bash
# Watch logs in real-time
sudo journalctl -u aromas -f
```

Then try to make a payment and watch for errors.

### Step 6: Test Payment Flow

1. Go to your website: `https://aromasbyharnoor.com`
2. Add items to cart
3. Go to checkout
4. Click "Place Order"
5. **Open browser console** (F12) and check for errors
6. Check the Network tab to see if the API call to `/orders/razorpay/create/` is successful

---

## 🔍 Common Issues & Fixes

### Issue 1: "Razorpay is not enabled"
**Fix:**
```bash
nano .env
# Make sure this line exists:
RAZORPAY_ENABLED=True
# Save and restart:
sudo systemctl restart aromas
```

### Issue 2: "Order not found"
**Fix:** This means the order creation is failing. Check:
- Database connection
- Cart has items
- User is logged in

### Issue 3: "Failed to create payment order"
**Fix:** This means Razorpay API call is failing. Check:
- Razorpay keys are correct
- Internet connection on server
- Razorpay account is active

### Issue 4: JavaScript Error "Razorpay is not defined"
**Fix:** The Razorpay SDK is not loading. Check:
- Browser console for script loading errors
- HTTPS is working (Razorpay requires HTTPS)
- No ad blockers interfering

---

## 🧪 Debug Steps

### Check Browser Console
1. Open your website
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Try to make a payment
5. Look for red error messages
6. Share the error message

### Check Network Requests
1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Try to make a payment
4. Look for request to `/orders/razorpay/create/ORDER_NUMBER/`
5. Click on it and check:
   - **Status**: Should be 200
   - **Response**: Should have `"success": true`

### Check Server Logs
```bash
# Real-time logs
sudo journalctl -u aromas -f --lines=50

# Look for errors when payment is attempted
```

---

## ✅ Quick Fix Checklist

- [ ] Code pulled from GitHub (`git pull origin main`)
- [ ] `.env` file has `RAZORPAY_ENABLED=True`
- [ ] Razorpay keys are correct in `.env`
- [ ] Service restarted (`sudo systemctl restart aromas`)
- [ ] Service is running (`sudo systemctl status aromas`)
- [ ] Browser console checked (F12)
- [ ] Network tab checked for API calls
- [ ] Server logs checked for errors

---

## 🚨 If Still Not Working

1. **Check Razorpay Dashboard:**
   - Go to https://dashboard.razorpay.com
   - Check if account is active
   - Verify API keys match

2. **Test with curl:**
   ```bash
   # Test if order creation endpoint works
   curl -X GET "https://aromasbyharnoor.com/orders/razorpay/create/TEST_ORDER/" \
     -H "Cookie: sessionid=YOUR_SESSION_ID"
   ```

3. **Check Django Settings:**
   ```bash
   cd /var/www/aromas
   source venv/bin/activate
   python manage.py shell
   ```
   Then in shell:
   ```python
   from django.conf import settings
   from orders.payment_utils import is_razorpay_enabled
   print("Enabled:", is_razorpay_enabled())
   print("Key ID:", settings.RAZORPAY_KEY_ID[:15] + "...")
   ```

---

## 📞 Need More Help?

Share these details:
1. Browser console errors (F12 → Console)
2. Network tab response for `/orders/razorpay/create/`
3. Server logs (`sudo journalctl -u aromas -n 50`)
4. Output of `python check_razorpay.py`

