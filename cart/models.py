from django.db import models
from store.models import Product, Variation
from accounts.models import Account


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True,
                            help_text="User if logged in, null for guest")
    date_added = models.DateField(auto_now_add=True)
    is_abandoned = models.BooleanField(default=False, help_text="True if cart is abandoned")
    abandoned_at = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    reminder_count = models.IntegerField(default=0)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.email}"
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name
