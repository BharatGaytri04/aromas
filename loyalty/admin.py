from django.contrib import admin
from .models import LoyaltyPoints, PointsTransaction, Referral, ReferralCode


class LoyaltyPointsAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'total_earned', 'total_redeemed', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('updated_at',)


class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'points', 'order', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__email', 'order__order_number')
    readonly_fields = ('created_at',)


class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred', 'referral_code', 'is_used', 'points_awarded', 'created_at')
    list_filter = ('is_used', 'points_awarded', 'created_at')
    search_fields = ('referrer__email', 'referred__email', 'referral_code')
    readonly_fields = ('created_at',)


class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'usage_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at',)


admin.site.register(LoyaltyPoints, LoyaltyPointsAdmin)
admin.site.register(PointsTransaction, PointsTransactionAdmin)
admin.site.register(Referral, ReferralAdmin)
admin.site.register(ReferralCode, ReferralCodeAdmin)
