from django.contrib import admin
from .models import Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'product', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'product__product_name', 'review_text')
    
    def get_user_name(self, obj):
        """Display user's name instead of email for privacy"""
        return obj.user.get_display_name()
    get_user_name.short_description = 'Customer Name'
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_approved',)
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'product', 'rating', 'review_text')
        }),
        ('Status', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Review, ReviewAdmin)
