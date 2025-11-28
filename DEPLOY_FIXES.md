# 🚀 Deploy Payment Fixes to VPS

## ✅ What Was Fixed

1. **Removed Cash on Delivery (COD) completely**
   - COD option removed from checkout page
   - Only Razorpay payment available now
   - All error messages updated (no COD mentions)

2. **Improved Payment Flow**
   - Razorpay is automatically selected
   - Better error handling
   - Improved debugging

## 📋 Steps to Deploy on VPS

### Step 1: Pull Latest Code
```bash
cd /var/www/aromas
git pull origin main
```

### Step 2: Clear Browser Cache
**Important:** The old page might be cached. Clear cache:
- Press `Ctrl + Shift + Delete` (or `Cmd + Shift + Delete` on Mac)
- Select "Cached images and files"
- Click "Clear data"

OR use **Hard Refresh**:
- Press `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)

### Step 3: Restart Service
```bash
sudo systemctl restart aromas
sudo systemctl status aromas
```

### Step 4: Verify Changes
1. Go to: `https://aromasbyharnoor.com/cart/checkout/`
2. **Hard refresh** the page (`Ctrl + F5`)
3. You should see:
   - ✅ Only "Pay Online (UPI, Cards, Net Banking)" option
   - ❌ NO "Cash on Delivery" option

### Step 5: Test Payment
1. Add items to cart
2. Go to checkout
3. Click "Place Order"
4. Razorpay payment modal should open

---

## 🔍 If COD Still Shows

### Option 1: Clear Browser Cache Completely
1. Open browser settings
2. Clear browsing data
3. Select "All time"
4. Check "Cached images and files"
5. Clear data

### Option 2: Use Incognito/Private Mode
- Open incognito/private window
- Go to your website
- Check if COD is gone

### Option 3: Check if Code is Updated
```bash
# On VPS, check the checkout template
cat /var/www/aromas/templates/store/checkout.html | grep -i "cash on delivery"
# Should return NOTHING (no results)
```

If it shows results, the code wasn't pulled. Run:
```bash
cd /var/www/aromas
git pull origin main
sudo systemctl restart aromas
```

---

## ✅ Verification Checklist

- [ ] Code pulled from GitHub
- [ ] Service restarted
- [ ] Browser cache cleared
- [ ] Hard refresh done (Ctrl + F5)
- [ ] COD option is gone
- [ ] Only Razorpay option shows
- [ ] Payment modal opens when clicking "Place Order"

---

## 🐛 Still Having Issues?

1. **Check browser console** (F12 → Console tab)
   - Look for errors
   - Check if old JavaScript is cached

2. **Check server logs:**
   ```bash
   sudo journalctl -u aromas -f
   ```

3. **Verify template file:**
   ```bash
   grep -i "cash on delivery" /var/www/aromas/templates/store/checkout.html
   # Should return nothing
   ```

4. **Force reload static files:**
   ```bash
   cd /var/www/aromas
   source venv/bin/activate
   python manage.py collectstatic --noinput
   sudo systemctl restart aromas
   ```

---

## 📝 Summary

All COD references have been removed from the code. The issue is likely:
1. **Browser cache** - Clear it or use incognito mode
2. **Code not pulled** - Run `git pull origin main` on VPS
3. **Service not restarted** - Run `sudo systemctl restart aromas`

After these steps, COD should be completely gone! ✅

