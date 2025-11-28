#!/usr/bin/env python3
"""
Diagnostic script to check Razorpay authentication.
Run this on your VPS to verify API keys are correct.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aromas.settings')
django.setup()

from django.conf import settings
import razorpay

print("=" * 60)
print("Razorpay Authentication Diagnostic")
print("=" * 60)

# Check if Razorpay is enabled
razorpay_enabled = getattr(settings, 'RAZORPAY_ENABLED', False)
print(f"\n1. RAZORPAY_ENABLED: {razorpay_enabled}")

if not razorpay_enabled:
    print("   ❌ Razorpay is not enabled in settings!")
    print("   Set RAZORPAY_ENABLED=True in .env file")
    sys.exit(1)

# Check Key ID
key_id = getattr(settings, 'RAZORPAY_KEY_ID', '').strip()
if key_id:
    print(f"\n2. RAZORPAY_KEY_ID: {key_id[:10]}...{key_id[-5:] if len(key_id) > 15 else key_id}")
    print(f"   Length: {len(key_id)} characters")
    if len(key_id) < 20:
        print("   ⚠️  WARNING: Key ID seems too short (should be ~20+ characters)")
else:
    print("\n2. RAZORPAY_KEY_ID: ❌ NOT SET")
    print("   Add RAZORPAY_KEY_ID=your_key_id to .env file")
    sys.exit(1)

# Check Key Secret
key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '').strip()
if key_secret:
    print(f"\n3. RAZORPAY_KEY_SECRET: {'*' * min(20, len(key_secret))}...")
    print(f"   Length: {len(key_secret)} characters")
    if len(key_secret) < 30:
        print("   ⚠️  WARNING: Key Secret seems too short (should be ~30+ characters)")
else:
    print("\n3. RAZORPAY_KEY_SECRET: ❌ NOT SET")
    print("   Add RAZORPAY_KEY_SECRET=your_key_secret to .env file")
    sys.exit(1)

# Check for extra spaces
if key_id != key_id.strip() or key_secret != key_secret.strip():
    print("\n   ⚠️  WARNING: Keys have extra spaces! They will be trimmed automatically.")

# Check Currency
currency = getattr(settings, 'RAZORPAY_CURRENCY', 'INR')
print(f"\n4. RAZORPAY_CURRENCY: {currency}")

# Try to initialize Razorpay client
print("\n5. Testing Razorpay Client Initialization...")
try:
    client = razorpay.Client(auth=(key_id, key_secret))
    print("   ✅ Client initialized successfully")
except Exception as e:
    print(f"   ❌ Client initialization failed: {str(e)}")
    sys.exit(1)

# Try to create a test order (this will test authentication)
print("\n6. Testing Razorpay Authentication (creating test order)...")
try:
    # Create a minimal test order (1 rupee = 100 paise)
    test_order = client.order.create({
        'amount': 100,  # 1 rupee in paise
        'currency': currency,
        'receipt': 'test_auth_check',
        'notes': {
            'test': 'authentication_check'
        }
    })
    print(f"   ✅ Authentication SUCCESSFUL!")
    print(f"   Test Order ID: {test_order.get('id')}")
    print(f"   Amount: {test_order.get('amount')} {test_order.get('currency')}")
    print("\n   ✅ Your Razorpay API keys are correct and working!")
except razorpay.errors.BadRequestError as e:
    print(f"   ❌ BadRequestError: {str(e)}")
    print("\n   Possible issues:")
    print("   - Invalid API key format")
    print("   - Keys are from test mode but trying to use live mode (or vice versa)")
    print("   - Check your Razorpay dashboard for correct keys")
    sys.exit(1)
except razorpay.errors.UnauthorizedError as e:
    print(f"   ❌ UnauthorizedError: {str(e)}")
    print("\n   This means your API keys are INCORRECT!")
    print("   Please check:")
    print("   1. Go to Razorpay Dashboard → Settings → API Keys")
    print("   2. Make sure you're using the correct keys (Test vs Live)")
    print("   3. Copy the keys exactly (no extra spaces)")
    print("   4. Update your .env file with correct keys")
    sys.exit(1)
except razorpay.errors.ServerError as e:
    print(f"   ⚠️  ServerError: {str(e)}")
    print("   This might be a temporary Razorpay server issue.")
    print("   Try again in a few minutes.")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Unexpected error: {type(e).__name__}: {str(e)}")
    print("\n   Check your internet connection and try again.")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All checks passed! Razorpay is configured correctly.")
print("=" * 60)

