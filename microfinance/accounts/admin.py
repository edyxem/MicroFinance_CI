from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User, LoginHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ('username', 'email', 'role', 'phone', 'region', 'is_active', 'created_at')
    list_filter     = ('role', 'is_active', 'region')
    search_fields   = ('username', 'email', 'phone')
    ordering        = ('-created_at',)
    fieldsets       = BaseUserAdmin.fieldsets + (
        ('Infos COFINANCE', {'fields': ('role', 'phone', 'region')}),
    )
    add_fieldsets   = BaseUserAdmin.add_fieldsets + (
        ('Infos COFINANCE', {'fields': ('role', 'phone', 'region')}),
    )


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display    = ('user', 'ip_address', 'logged_at')
    list_filter     = ('logged_at',)
    search_fields   = ('user__username', 'ip_address')
    readonly_fields = ('user', 'ip_address', 'logged_at')