from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, LoginAttempt


class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name','last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'ip_address', 'success', 'attempted_at')
    list_filter = ('success', 'attempted_at')
    search_fields = ('email', 'user__email', 'ip_address', 'user_agent')
    readonly_fields = ('user', 'email', 'ip_address', 'user_agent', 'success', 'attempted_at')
    ordering = ('-attempted_at',)


admin.site.register(Account, AccountAdmin)
admin.site.register(LoginAttempt, LoginAttemptAdmin)
