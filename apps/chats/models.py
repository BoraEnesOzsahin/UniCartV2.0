import hashlib
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='conversations')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(blank=True, null=True)

    blocked_at = models.DateTimeField(blank=True, null=True)
    blocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='blocked_conversations',
    )
    block_reason = models.CharField(max_length=200, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['listing', 'buyer'], name='uniq_conversation_per_listing_buyer'),
        ]
        indexes = [
            models.Index(fields=['buyer', 'last_message_at']),
            models.Index(fields=['seller', 'last_message_at']),
        ]

    def clean(self):
        if self.listing_id and self.seller_id and self.listing.seller_id != self.seller_id:
            raise ValidationError('Conversation.seller must match listing.seller')
        if self.buyer_id and self.seller_id and self.buyer_id == self.seller_id:
            raise ValidationError('Buyer and seller cannot be the same user')

    def is_blocked(self) -> bool:
        return bool(self.blocked_at)

    def other_party(self, user):
        if user.pk == self.buyer_id:
            return self.seller
        if user.pk == self.seller_id:
            return self.buyer
        return None


class ConversationMembership(models.Model):
    ROLE_BUYER = 'buyer'
    ROLE_SELLER = 'seller'
    ROLE_CHOICES = [
        (ROLE_BUYER, 'Buyer'),
        (ROLE_SELLER, 'Seller'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    hidden_at = models.DateTimeField(blank=True, null=True)
    muted_until = models.DateTimeField(blank=True, null=True)
    strikes = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['conversation', 'user'], name='uniq_membership_per_user'),
        ]

    def is_muted(self) -> bool:
        return bool(self.muted_until and self.muted_until > timezone.now())


def _chat_image_upload_to(instance, filename: str) -> str:
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'bin'
    return f"chat_images/conversation_{instance.conversation_id}/{uuid.uuid4().hex}.{ext}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to=_chat_image_upload_to, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    content_hash = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]

    def clean(self):
        if not self.text and not self.image:
            raise ValidationError('Message must have text or an image.')

    def save(self, *args, **kwargs):
        if self.text:
            normalized = ' '.join(self.text.lower().split())
            self.content_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)


class MessageReceipt(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='receipts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_receipts')
    delivered_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['message', 'user'], name='uniq_receipt_per_user'),
        ]
        indexes = [
            models.Index(fields=['user', 'read_at']),
        ]


class ConversationReport(models.Model):
    REASON_SPAM = 'spam'
    REASON_ABUSE = 'abuse'
    REASON_SCAM = 'scam'
    REASON_OTHER = 'other'
    REASON_CHOICES = [
        (REASON_SPAM, 'Spam / flooding'),
        (REASON_ABUSE, 'Abusive / hateful language'),
        (REASON_SCAM, 'Scam / phishing attempt'),
        (REASON_OTHER, 'Other'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_reports_made')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_reports_received')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]
