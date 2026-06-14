from django.contrib import admin
from notifications.models import Notification
 
 
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('destinataire', 'type', 'titre', 'is_read', 'created_at')
    list_filter   = ('type', 'is_read', 'created_at')
    search_fields = ('destinataire__username', 'titre', 'message')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)