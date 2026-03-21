from django.contrib import admin
from .models import ChatMessage, ManualRequest


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'user', 'role', 'content', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'session_key')


@admin.register(ManualRequest)
class ManualRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'closed_at')
    list_filter = ('status',)
