from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.
    
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'display_variations', 'quantity', 'is_active')
    list_filter = ('is_active',)

    def display_variations(self, obj):
        return ", ".join([f"{var.variation_category}: {var.variation_value}" for var in obj.variations.all()])
    display_variations.short_description = 'Variations'


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
