from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import Order, OrderProduct, Payment, OrderTracking, ReturnRequest
from .admin_views import admin_dashboard, export_orders_csv, get_new_orders_count


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'email', 'order_total', 'discount', 'final_total', 'status', 'is_ordered', 'created_at')
    list_filter = ('status', 'is_ordered', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'phone', 'email', 'tracking_number')
    readonly_fields = ('order_number', 'ip', 'created_at', 'updated_at', 'shipped_at', 'delivered_at')
    inlines = [OrderProductInline]
    list_editable = ('status',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'is_ordered')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'phone', 'email')
        }),
        ('Shipping Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'pincode')
        }),
        ('Order Details', {
            'fields': ('order_total', 'tax', 'discount', 'final_total', 'order_note')
        }),
        ('Payment', {
            'fields': ('payment',)
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'shipped_at', 'delivered_at')
        }),
        ('System Information', {
            'fields': ('ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('payment_id', 'user__email')


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'product_price', 'ordered', 'created_at')
    list_filter = ('ordered', 'created_at')


class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'location', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number',)
    readonly_fields = ('created_at',)


class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'status', 'refund_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'user__email')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(OrderTracking, OrderTrackingAdmin)
admin.site.register(ReturnRequest, ReturnRequestAdmin)


# Custom admin URLs
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', admin_dashboard, name='admin_dashboard'),
            path('export-orders-csv/', export_orders_csv, name='export_orders_csv'),
            path('new-orders-count/', get_new_orders_count, name='new_orders_count'),
        ]
        return custom_urls + urls
