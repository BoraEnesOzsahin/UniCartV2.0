from django.contrib import admin

from .models import Conversation, ConversationMembership, ConversationReport, Message, MessageReceipt


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'buyer', 'seller', 'last_message_at', 'blocked_at')
    search_fields = ('listing__title', 'buyer__username', 'seller__username')


@admin.register(ConversationMembership)
class ConversationMembershipAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'user', 'role', 'hidden_at', 'muted_until', 'strikes')
    search_fields = ('user__username',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'created_at')
    search_fields = ('text', 'sender__username')


@admin.register(MessageReceipt)
class MessageReceiptAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'delivered_at', 'read_at')


@admin.register(ConversationReport)
class ConversationReportAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'reporter', 'reported_user', 'reason', 'created_at')
    search_fields = ('details', 'reporter__username', 'reported_user__username')
