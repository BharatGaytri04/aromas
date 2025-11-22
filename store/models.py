from django.db import models
from category.models import Category
from django.urls import reverse


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    # New fields for advanced features
    sale_price = models.IntegerField(null=True, blank=True, help_text="Sale price if on discount")
    is_featured = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    flash_sale_start = models.DateTimeField(null=True, blank=True)
    flash_sale_end = models.DateTimeField(null=True, blank=True)
    min_stock_alert = models.IntegerField(default=10, help_text="Alert when stock falls below this")
    gst_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=2.00, 
        help_text="GST percentage for this product (e.g., 2.00 for 2%, 5.00 for 5%, 18.00 for 18%)"
    )

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    
    def get_discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.sale_price and self.price:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount, 2)
        return 0
    
    def get_current_price(self):
        """Get current price (sale price if available, else regular price)"""
        if self.sale_price and self.is_available:
            return self.sale_price
        return self.price
    
    def is_on_sale(self):
        """Check if product is currently on sale"""
        if self.sale_price and self.is_available:
            if self.is_flash_sale:
                from django.utils import timezone
                now = timezone.now()
                if self.flash_sale_start and self.flash_sale_end:
                    return self.flash_sale_start <= now <= self.flash_sale_end
            return True
        return False
    
    def get_average_rating(self):
        """Get average rating from approved reviews"""
        from reviews.models import Review
        from django.db.models import Avg
        result = Review.objects.filter(
            product=self, 
            is_approved=True
        ).aggregate(Avg('rating'))
        return result['rating__avg'] or 0
    
    def get_review_count(self):
        """Get count of approved reviews"""
        from reviews.models import Review
        return Review.objects.filter(product=self, is_approved=True).count()
    
    def get_rating_percentage(self):
        """Get rating as percentage (for star display)"""
        avg_rating = self.get_average_rating()
        return (avg_rating / 5) * 100 if avg_rating else 0
    
    def user_can_review(self, user):
        """Check if user can review this product (must have purchased it)"""
        if not user.is_authenticated:
            return False
        from orders.models import OrderProduct
        return OrderProduct.objects.filter(
            user=user,
            product=self,
            ordered=True
        ).exists()
    
    def user_has_reviewed(self, user):
        """Check if user has already reviewed this product"""
        if not user.is_authenticated:
            return False
        from reviews.models import Review
        return Review.objects.filter(product=self, user=user).exists()
    
    def get_user_review(self, user):
        """Get user's review for this product"""
        if not user.is_authenticated:
            return None
        from reviews.models import Review
        try:
            return Review.objects.get(product=self, user=user)
        except Review.DoesNotExist:
            return None

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    """Multiple images for a product (4-6 images)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='photos/products/gallery')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['is_primary', 'created_at']
    
    def __str__(self):
        return f"{self.product.product_name} - Image {self.id}"

    def image_preview(self):
        """Return HTML preview for admin"""
        if self.image:
            return f'<img src="{self.image.url}" width="80" height="80" style="object-fit: cover; border-radius: 6px;" />'
        return "No Image"
    image_preview.short_description = 'Preview'
    image_preview.allow_tags = True


class Pincode(models.Model):
    """Pincode serviceability database"""
    pincode = models.CharField(max_length=6, unique=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    is_serviceable = models.BooleanField(default=True)
    delivery_days = models.IntegerField(default=3, help_text="Estimated delivery days")
    cod_available = models.BooleanField(default=True, help_text="Cash on Delivery available")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pincode']

    def __str__(self):
        return f"{self.pincode} - {self.city}, {self.state}"


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


variation_category_choice = (
    ('color', 'Color'),
    ('size', 'Size'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    class Meta:
        verbose_name = 'variation'
        verbose_name_plural = 'variations'

    def __str__(self):
        return f"{self.product.product_name} - {self.variation_value}"


class Banner(models.Model):
    """Homepage banner that can be managed by superuser"""
    title = models.CharField(max_length=200, help_text="Banner title (optional)")
    image = models.ImageField(upload_to='photos/banners', help_text="Recommended size: 1200x300px")
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alt text for image")
    is_active = models.BooleanField(default=True, help_text="Only one active banner will be displayed")
    link_url = models.URLField(blank=True, null=True, help_text="Optional: URL to link when banner is clicked")
    link_text = models.CharField(max_length=100, blank=True, help_text="Optional: Text for the link button")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
    
    def __str__(self):
        return self.title or f"Banner {self.id}"
    
    def image_preview(self):
        """Return HTML preview for admin"""
        if self.image:
            return f'<img src="{self.image.url}" width="200" height="50" style="object-fit: cover; border-radius: 6px;" />'
        return "No Image"
    image_preview.short_description = 'Preview'
    image_preview.allow_tags = True
    
    @classmethod
    def get_active_banner(cls):
        """Get the first active banner"""
        return cls.objects.filter(is_active=True).first()