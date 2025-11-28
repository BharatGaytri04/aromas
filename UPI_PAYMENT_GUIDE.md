# 📱 UPI Payment Setup Guide

## ✅ UPI is Already Enabled!

Good news! **UPI payments are automatically available** when you use Razorpay. Customers can pay using:

- **Google Pay** 📱
- **PhonePe** 💰
- **Paytm** 🏦
- **BHIM UPI** 🇮🇳
- **Any UPI app** (Amazon Pay, WhatsApp Pay, etc.)

---

## 🎯 How It Works

1. **Customer selects "Pay Online"** at checkout
2. **Razorpay payment modal opens**
3. **Customer sees all payment options** including:
   - UPI (Google Pay, PhonePe, Paytm, etc.)
   - Credit/Debit Cards
   - Net Banking
   - Wallets

4. **Customer chooses UPI** and completes payment
5. **Payment is processed** and order is confirmed

---

## 🔧 Enable UPI in Razorpay Dashboard

To ensure UPI is enabled in your Razorpay account:

1. **Log in** to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Go to **Settings** → **Payment Methods**
3. Make sure **UPI** is **enabled** (toggle should be ON)
4. Save changes

**Note:** UPI is usually enabled by default, but verify it's active.

---

## 📋 Payment Methods Available

When customers click "Pay Online", they'll see:

### UPI Options:
- ✅ Google Pay
- ✅ PhonePe
- ✅ Paytm
- ✅ BHIM UPI
- ✅ Amazon Pay UPI
- ✅ WhatsApp Pay
- ✅ Any UPI ID (customers can enter their UPI ID)

### Other Options:
- ✅ Credit/Debit Cards (Visa, Mastercard, RuPay, etc.)
- ✅ Net Banking (All major banks)
- ✅ Wallets (Paytm, Freecharge, etc.)

---

## 🧪 Testing UPI Payments

### Test Mode (Development):

1. Use **test keys** in `.env`:
   ```env
   RAZORPAY_KEY_ID=rzp_test_...
   ```

2. **Test UPI payment**:
   - Use test UPI ID: `success@razorpay`
   - Or use any test UPI ID provided by Razorpay

### Live Mode (Production):

1. Use **live keys** in `.env`:
   ```env
   RAZORPAY_KEY_ID=rzp_live_...
   ```

2. **Real UPI payments** will work automatically
3. Customers can use any UPI app they have installed

---

## 💡 Customer Experience

### On Desktop:
- Customer enters UPI ID manually
- Or scans QR code (if available)

### On Mobile:
- UPI app opens automatically (if installed)
- Customer authorizes payment in their UPI app
- Payment completes seamlessly

---

## 🔍 Verify UPI is Working

1. **Check Razorpay Dashboard**:
   - Go to **Payments** → **All Payments**
   - Look for UPI transactions

2. **Test on your site**:
   - Add items to cart
   - Go to checkout
   - Select "Pay Online"
   - You should see UPI option in the payment modal

3. **Check payment methods**:
   - In Razorpay modal, UPI should be listed as an option
   - Usually shown with UPI icon or "UPI" label

---

## ⚙️ Configuration

No special configuration needed! UPI is enabled by default in Razorpay Standard Checkout.

The checkout page already shows:
```
Pay Online (UPI, Cards, Net Banking)
```

This clearly indicates UPI is available.

---

## 🚨 Troubleshooting

### UPI option not showing?

1. **Check Razorpay Dashboard**:
   - Settings → Payment Methods → UPI should be enabled

2. **Verify account status**:
   - Make sure your Razorpay account is active
   - KYC should be completed for live mode

3. **Check payment amount**:
   - Some payment methods have minimum amount requirements
   - UPI usually works for any amount

4. **Browser/Device**:
   - UPI works best on mobile devices
   - On desktop, customers can enter UPI ID manually

### UPI payment failing?

1. **Check customer's UPI app**:
   - Make sure they have a UPI app installed
   - UPI ID should be correct

2. **Check Razorpay logs**:
   - Go to Dashboard → Payments
   - Check payment status and error messages

3. **Verify account balance**:
   - Customer's UPI account should have sufficient balance

---

## 📊 UPI Payment Flow

```
Customer → Checkout → Select "Pay Online"
    ↓
Razorpay Modal Opens
    ↓
Customer Sees Payment Options
    ↓
Customer Selects UPI
    ↓
Enters UPI ID or Opens UPI App
    ↓
Authorizes Payment
    ↓
Payment Successful
    ↓
Order Confirmed ✅
```

---

## ✅ Summary

- ✅ **UPI is already enabled** - No additional setup needed
- ✅ **Works automatically** with Razorpay integration
- ✅ **All UPI apps supported** (Google Pay, PhonePe, Paytm, etc.)
- ✅ **Mobile-friendly** - UPI apps open automatically on mobile
- ✅ **Desktop support** - Customers can enter UPI ID manually

**Your customers can now pay using UPI!** 🎉

---

## 📞 Need Help?

- **Razorpay Support**: support@razorpay.com
- **Razorpay Docs**: https://razorpay.com/docs/payments/payment-methods/upi/
- **Dashboard**: https://dashboard.razorpay.com

