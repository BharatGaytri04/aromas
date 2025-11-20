from django.db import models
from accounts.models import Account
from orders.models import Order


class LoyaltyPoints(models.Model):
    """User loyalty points balance"""
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='loyalty_points')
    points = models.IntegerField(default=0)
    total_earned = models.IntegerField(default=0)
    total_redeemed = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.points} points"


class PointsTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earned', 'Earned'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='points_transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    points = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.points} points"


class Referral(models.Model):
    """Referral system"""
    referrer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='referrals_sent')
    referred = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='referral_received')
    referral_code = models.CharField(max_length=20, unique=True)
    is_used = models.BooleanField(default=False)
    points_awarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('referrer', 'referred')

    def __str__(self):
        return f"{self.referrer.email} referred {self.referred.email}"


class ReferralCode(models.Model):
    """User referral codes"""
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='referral_code')
    code = models.CharField(max_length=20, unique=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"
