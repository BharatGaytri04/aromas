"""
Script to send a notification email to aromasbyharnoor@gmail.com
Run this with: python send_notification.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aromas.settings')
django.setup()

from notifications.utils import send_email_notification
from django.conf import settings

def send_notification():
    """Send notification email to aromasbyharnoor@gmail.com"""
    
    recipient_email = "aromasbyharnoor@gmail.com"
    subject = "Seller Dashboard Notification - Aromas by Harnoor"
    message = """
Hello!

This is a notification from your Aromas by Harnoor e-commerce system.

Your Seller Dashboard is now ready and fully functional!

📊 Seller Dashboard Features:
- View all orders
- Update order status (New → Accepted → Packed → Shipped → Delivered)
- Filter orders by status, date, and search
- View detailed order information
- Track order history

🔗 Access Your Seller Dashboard:
1. Login to your account at: http://127.0.0.1:8000/accounts/login/
2. Click "Seller Dashboard" in the navbar (visible only to staff users)
3. Or go directly to: http://127.0.0.1:8000/seller/dashboard/

🔐 To Access Seller Dashboard:
- You need a staff account (is_staff = True)
- Create one with: python manage.py createsuperuser
- Or make existing account staff via admin panel

📝 Quick Start:
1. Create superuser: python manage.py createsuperuser
2. Login: http://127.0.0.1:8000/accounts/login/
3. Access dashboard: http://127.0.0.1:8000/seller/dashboard/

If you have any questions or need assistance, feel free to reach out.

Best regards,
Aromas by Harnoor System
    """
    
    print(f"📧 Sending notification to {recipient_email}...")
    
    try:
        result = send_email_notification(
            recipient_email=recipient_email,
            subject=subject,
            message=message,
            notification_type='admin_notification'
        )
        
        if result:
            print("✅ Notification sent successfully!")
            print(f"   Recipient: {recipient_email}")
            print(f"   Subject: {subject}")
        else:
            print("❌ Failed to send notification. Check email settings.")
            print("   Make sure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are configured in .env file")
            
    except Exception as e:
        print(f"❌ Error sending notification: {str(e)}")
        print("\n💡 Make sure:")
        print("   1. Email settings are configured in .env file")
        print("   2. EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set")
        print("   3. For Gmail, use App Password (not regular password)")
        print("   4. Check your .env file for email configuration")

if __name__ == "__main__":
    send_notification()

