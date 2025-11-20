from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, Variation, ProductImage, Pincode


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_preview', 'image', 'alt_text', 'is_primary')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return obj.image_preview()
    image_preview.short_description = 'Preview'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'sale_price', 'stock', 'category', 'is_available', 
                   'is_featured', 'is_flash_sale', 'modified_date')
    prepopulated_fields = {'slug': ('product_name',)}
    list_filter = ('is_available', 'is_featured', 'is_flash_sale', 'category', 'created_date')
    search_fields = ('product_name', 'description')
    list_editable = ('is_available', 'is_featured', 'is_flash_sale')
    inlines = [ProductImageInline]
    readonly_fields = ('created_date', 'modified_date')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'slug', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'min_stock_alert', 'is_available')
        }),
        ('Features', {
            'fields': ('is_featured', 'is_flash_sale', 'flash_sale_start', 'flash_sale_end')
        }),
    )


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'preview', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__product_name',)
    readonly_fields = ('preview',)

    def preview(self, obj):
        return mark_safe(obj.image_preview())
    preview.short_description = 'Preview'


class PincodeAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'city', 'state', 'is_serviceable', 'delivery_days', 'cod_available')
    list_filter = ('is_serviceable', 'cod_available', 'state')
    search_fields = ('pincode', 'city', 'state')
    list_editable = ('is_serviceable', 'cod_available', 'delivery_days')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Pincode, PincodeAdmin)
