# 🔐 How to Login to Seller Dashboard

## Step 1: Create a Staff/Superuser Account

You need a staff account to access the seller dashboard. There are two ways:

### Option A: Create Superuser (Recommended)

Run this command in your terminal:

```powershell
python manage.py createsuperuser
```

You'll be asked for:
- **First Name**: Enter your first name
- **Last Name**: Enter your last name  
- **Email**: Enter your email (this will be your login username)
- **Username**: Enter a username
- **Password**: Enter a secure password

This creates an account with:
- ✅ `is_staff = True` (can access seller dashboard)
- ✅ `is_admin = True` (can access admin panel)
- ✅ `is_superadmin = True` (full admin privileges)
- ✅ `is_active = True` (account is active)

### Option B: Make Existing User a Staff Member

If you already have an account, you can make it a staff account:

1. **Via Django Admin Panel:**
   - Go to: `http://127.0.0.1:8000/secure-admin/` (or your custom admin URL)
   - Login with superuser account
   - Go to **Accounts** → **Accounts**
   - Find your user account
   - Check the **Staff status** checkbox
   - Check the **Active** checkbox
   - Click **Save**

2. **Via Django Shell:**
   ```powershell
   python manage.py shell
   ```
   Then run:
   ```python
   from accounts.models import Account
   user = Account.objects.get(email='your-email@example.com')
   user.is_staff = True
   user.is_active = True
   user.save()
   exit()
   ```

---

## Step 2: Login to Your Account

1. **Go to Login Page:**
   - Visit: `http://127.0.0.1:8000/accounts/login/`

2. **Enter Credentials:**
   - **Email**: Your email address (this is your username)
   - **Password**: Your password

3. **Click "Login"**

---

## Step 3: Access Seller Dashboard

After logging in as a staff user, you have **3 ways** to access the seller dashboard:

### Method 1: Via Navbar Link (Easiest)
- Once logged in as staff, you'll see **"Seller Dashboard"** link in the navbar
- Click on it to go to `/seller/dashboard/`

### Method 2: Direct URL
- Type in browser: `http://127.0.0.1:8000/seller/dashboard/`

### Method 3: Via Admin Panel
- Go to admin panel: `http://127.0.0.1:8000/secure-admin/`
- Look for seller dashboard link (if added to admin)

---

## 🔒 Security Notes

- **Normal users** (non-staff) **CANNOT** see the "Seller Dashboard" link in navbar
- **Normal users** **CANNOT** access `/seller/dashboard/` even if they know the URL
- Only users with `is_staff = True` can access seller dashboard
- The `@staff_member_required` decorator protects all seller views

---

## ✅ Quick Test

To verify everything works:

1. **Create superuser:**
   ```powershell
   python manage.py createsuperuser
   ```

2. **Start server:**
   ```powershell
   python manage.py runserver
   ```

3. **Login:**
   - Go to: `http://127.0.0.1:8000/accounts/login/`
   - Login with superuser credentials

4. **Access seller dashboard:**
   - Click "Seller Dashboard" in navbar OR
   - Go to: `http://127.0.0.1:8000/seller/dashboard/`

---

## 🆘 Troubleshooting

### "You don't have permission to access this page"
- **Solution**: Your account doesn't have `is_staff = True`
- **Fix**: Make your account staff via admin panel or shell

### "Seller Dashboard" link not showing
- **Solution**: You're not logged in as staff user
- **Fix**: Login with a staff account

### Can't login
- **Check**: Email and password are correct
- **Check**: Account has `is_active = True`
- **Check**: You're using email (not username) to login

---

## 📝 Summary

1. **Create superuser**: `python manage.py createsuperuser`
2. **Login**: `http://127.0.0.1:8000/accounts/login/`
3. **Access dashboard**: Click "Seller Dashboard" in navbar or go to `/seller/dashboard/`

That's it! 🎉

