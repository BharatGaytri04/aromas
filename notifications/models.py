from django.db import models
from accounts.models import Account
from orders.models import Order
from django.utils import timezone


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_order', 'New Order'),
        ('low_stock', 'Low Stock Alert'),
        ('order_status', 'Order Status Update'),
        ('abandoned_cart', 'Abandoned Cart'),
        ('coupon_reminder', 'Coupon Reminder'),
        ('refund_request', 'Refund Request'),
    ]
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True,
                            help_text="Null for admin notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_admin_notification = models.BooleanField(default=False, 
                                                help_text="True for admin dashboard notifications")
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['is_admin_notification', 'is_read']),
        ]

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.notification_type} - {self.title}"


class EmailNotification(models.Model):
    """Track email notifications sent"""
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email to {self.recipient_email} - {self.subject}"
