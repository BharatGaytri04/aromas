from django.db import models
from accounts.models import Account
from store.models import Product


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES, help_text="Rating from 1 to 5")
    review_text = models.TextField(max_length=1000, blank=True, help_text="Review comment (optional)")
    is_approved = models.BooleanField(default=False, help_text="Approved reviews are visible to customers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        user_name = self.user.get_display_name()
        return f"{user_name} - {self.product.product_name} - {self.rating} stars"
