#!/usr/bin/env python
"""
Quick script to check Razorpay configuration status.
Run this on your VPS to diagnose Razorpay setup issues.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aromas.settings')
django.setup()

from django.conf import settings
from orders.payment_utils import is_razorpay_enabled

print("=" * 60)
print("RAZORPAY CONFIGURATION CHECK")
print("=" * 60)
print()

# Check environment variables
print("1. Environment Variables:")
print(f"   RAZORPAY_ENABLED (from env): {os.environ.get('RAZORPAY_ENABLED', 'NOT SET')}")
print(f"   RAZORPAY_KEY_ID (from env): {os.environ.get('RAZORPAY_KEY_ID', 'NOT SET')[:20]}..." if os.environ.get('RAZORPAY_KEY_ID') else "   RAZORPAY_KEY_ID (from env): NOT SET")
print(f"   RAZORPAY_KEY_SECRET (from env): {'SET' if os.environ.get('RAZORPAY_KEY_SECRET') else 'NOT SET'}")
print()

# Check Django settings
print("2. Django Settings:")
print(f"   RAZORPAY_ENABLED: {getattr(settings, 'RAZORPAY_ENABLED', 'NOT FOUND')}")
print(f"   RAZORPAY_KEY_ID: {getattr(settings, 'RAZORPAY_KEY_ID', 'NOT FOUND')[:20]}..." if getattr(settings, 'RAZORPAY_KEY_ID', None) else "   RAZORPAY_KEY_ID: NOT FOUND")
print(f"   RAZORPAY_KEY_SECRET: {'SET' if getattr(settings, 'RAZORPAY_KEY_SECRET', None) else 'NOT FOUND'}")
print(f"   RAZORPAY_CURRENCY: {getattr(settings, 'RAZORPAY_CURRENCY', 'NOT FOUND')}")
print()

# Check if Razorpay is enabled via utility function
print("3. Payment Utility Check:")
print(f"   is_razorpay_enabled(): {is_razorpay_enabled()}")
print()

# Check if razorpay package is installed
print("4. Package Check:")
try:
    import razorpay
    print(f"   razorpay package: INSTALLED (version: {razorpay.__version__ if hasattr(razorpay, '__version__') else 'unknown'})")
except ImportError:
    print("   razorpay package: NOT INSTALLED")
    print("   → Run: pip install razorpay==1.4.2")
print()

# Final status
print("=" * 60)
print("STATUS:")
if is_razorpay_enabled() and getattr(settings, 'RAZORPAY_KEY_ID', None):
    print("✅ Razorpay is ENABLED and configured correctly!")
    print("   The payment option should appear on checkout page.")
else:
    print("❌ Razorpay is NOT enabled or misconfigured.")
    print()
    print("FIXES NEEDED:")
    if not getattr(settings, 'RAZORPAY_ENABLED', False):
        print("   1. Set RAZORPAY_ENABLED=True in .env file")
    if not getattr(settings, 'RAZORPAY_KEY_ID', None):
        print("   2. Set RAZORPAY_KEY_ID in .env file")
    if not getattr(settings, 'RAZORPAY_KEY_SECRET', None):
        print("   3. Set RAZORPAY_KEY_SECRET in .env file")
    try:
        import razorpay
    except ImportError:
        print("   4. Install razorpay package: pip install razorpay==1.4.2")
    print()
    print("   After fixing, restart Gunicorn:")
    print("   sudo systemctl restart aromas")
print("=" * 60)

