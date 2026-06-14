from django.contrib import admin
from chat.models import Conversation, Message
 
 
class MessageInline(admin.TabularInline):
    model         = Message
    extra         = 0
    readonly_fields = ('expediteur', 'contenu', 'fichier', 'is_auto', 'created_at')
    can_delete    = False
 
 
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display  = ('id', 'client', 'agent', 'status', 'created_at', 'updated_at')
    list_filter   = ('status',)
    search_fields = ('client__username', 'agent__username')
    ordering      = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    inlines       = [MessageInline]
 
 
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('id', 'conversation', 'expediteur', 'contenu', 'is_auto', 'created_at')
    list_filter   = ('is_auto', 'created_at')
    search_fields = ('expediteur__username', 'contenu')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at',)