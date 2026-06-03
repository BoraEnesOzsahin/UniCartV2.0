from django.contrib import admin

from .models import Conversation, Message, MessageReceipt


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'buyer', 'seller', 'last_message_at', 'blocked_at')
    search_fields = ('listing__title', 'buyer__username', 'seller__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'created_at')
    search_fields = ('text', 'sender__username')


@admin.register(MessageReceipt)
class MessageReceiptAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'delivered_at', 'read_at')
