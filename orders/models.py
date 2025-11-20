from django.db import models
from accounts.models import Account
from store.models import Product, Variation
import random
import string


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('UPI', 'UPI'),
        ('CARD', 'Credit/Debit Card'),
        ('NETBANKING', 'Net Banking'),
    ]
    
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10, blank=True, help_text="Pincode for delivery")
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    discount = models.FloatField(default=0, help_text="Discount from coupon")
    final_total = models.FloatField(default=0.0, help_text="Final amount after discount")
    status = models.CharField(max_length=20, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    
    # Tracking fields
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @staticmethod
    def generate_order_number(user_id):
        """
        Generate a unique order number in e-commerce format.
        
        Format: YYYYMMDD-XXXXXX-XX
        Breakdown:
        - YYYYMMDD → Date (e.g., 20251120)
        - XXXXXX → Order sequence number (padded with zeros, e.g., 000123)
        - XX → Random digits to avoid duplicates (e.g., 18)
        
        Example: 20251120-000123-18
        
        This format is:
        ✔ Unique (timestamp + sequence + random)
        ✔ Sortable (by date)
        ✔ Easy to read (with dashes)
        ✔ Good for customer support
        
        Args:
            user_id: The ID of the user placing the order
            
        Returns:
            str: A unique order number
        """
        from datetime import datetime
        
        # Get current date (YYYYMMDD)
        date_str = datetime.now().strftime('%Y%m%d')
        
        # Get the count of orders today to create sequence number
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_orders_count = Order.objects.filter(
            created_at__gte=today_start
        ).count()
        
        # Create sequence number (6 digits, padded with zeros)
        # Add 1 because this will be the next order
        sequence = str(today_orders_count + 1).zfill(6)
        
        # Add random 2 digits for uniqueness
        random_str = ''.join(random.choices(string.digits, k=2))
        
        # Combine: date-sequence-random
        order_number = f"{date_str}-{sequence}-{random_str}"
        
        # Ensure uniqueness - regenerate if exists
        max_attempts = 100
        attempts = 0
        while Order.objects.filter(order_number=order_number).exists() and attempts < max_attempts:
            random_str = ''.join(random.choices(string.digits, k=2))
            order_number = f"{date_str}-{sequence}-{random_str}"
            attempts += 1
        
        if attempts >= max_attempts:
            # Fallback: use longer random string if still not unique
            random_str = ''.join(random.choices(string.digits, k=4))
            order_number = f"{date_str}-{sequence}-{random_str}"
        
        return order_number

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def get_status_timeline(self):
        """Get order status timeline"""
        timeline = []
        if self.status in ['New', 'Accepted', 'Packed', 'Shipped', 'Out for Delivery', 'Delivered', 'Completed']:
            timeline.append({'status': 'New', 'completed': True, 'date': self.created_at})
        if self.status in ['Accepted', 'Packed', 'Shipped', 'Out for Delivery', 'Delivered', 'Completed']:
            timeline.append({'status': 'Accepted', 'completed': True})
        if self.status in ['Packed', 'Shipped', 'Out for Delivery', 'Delivered', 'Completed']:
            timeline.append({'status': 'Packed', 'completed': True})
        if self.status in ['Shipped', 'Out for Delivery', 'Delivered', 'Completed']:
            timeline.append({'status': 'Shipped', 'completed': True, 'date': self.shipped_at})
        if self.status in ['Out for Delivery', 'Delivered', 'Completed']:
            timeline.append({'status': 'Out for Delivery', 'completed': True})
        if self.status in ['Delivered', 'Completed']:
            timeline.append({'status': 'Delivered', 'completed': True, 'date': self.delivered_at})
        if self.status == 'Completed':
            timeline.append({'status': 'Completed', 'completed': True})
        
        # Add current status
        current_status = {'status': self.status, 'completed': False, 'current': True}
        if self.status not in [t['status'] for t in timeline]:
            timeline.append(current_status)
        else:
            for t in timeline:
                if t['status'] == self.status:
                    t['current'] = True
        
        return timeline

    def __str__(self):
        return f"Order #{self.order_number}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def sub_total(self):
        return self.product_price * self.quantity

    def __str__(self):
        return self.product.product_name


class OrderTracking(models.Model):
    """Track order status changes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class ReturnRequest(models.Model):
    RETURN_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('refunded', 'Refunded'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    order_product = models.ForeignKey(OrderProduct, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=RETURN_STATUS, default='pending')
    refund_amount = models.FloatField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Return request for Order #{self.order.order_number}"
