from django.contrib import admin
from .models import Notification, EmailNotification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'user', 'is_admin_notification', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_admin_notification', 'created_at')
    search_fields = ('title', 'message', 'user__email')
    list_editable = ('is_read',)
    readonly_fields = ('created_at', 'read_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'order')


class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient_email', 'subject', 'notification_type', 'is_sent', 'sent_at')
    list_filter = ('is_sent', 'notification_type', 'sent_at')
    search_fields = ('recipient_email', 'subject')
    readonly_fields = ('sent_at',)


admin.site.register(Notification, NotificationAdmin)
admin.site.register(EmailNotification, EmailNotificationAdmin)
