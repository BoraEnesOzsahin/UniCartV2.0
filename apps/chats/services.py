import re
from dataclasses import dataclass
from typing import Optional

from datetime import timedelta

from django.utils import timezone
from django.utils.html import strip_tags

from .models import Conversation, ConversationMembership, Message


MESSAGE_MAX_LENGTH = 1000
COOLDOWN_SECONDS = 2
WINDOW_SECONDS = 60
MAX_MESSAGES_PER_WINDOW = 20
RECENT_DUP_SECONDS = 10 * 60
MAX_DUP_IN_RECENT = 3


_CONTACT_OR_OFFPLATFORM_PATTERNS = [
    re.compile(r"\b(whatsapp|telegram|instagram|snapchat|discord)\b", re.I),
    re.compile(r"\b(\+?\d[\d\s\-()]{8,}\d)\b"),  # phone-like
]

_CREDENTIAL_PATTERNS = [
    re.compile(r"\b(password|passcode|otp|2fa|verification code)\b", re.I),
    re.compile(r"\b(username|login)\b\s*[:=]", re.I),
]

_SCAM_PATTERNS = [
    re.compile(r"\b(bank|iban|wire transfer|crypto|gift card)\b", re.I),
    re.compile(r"\bclick\b.+\blink\b", re.I),
]

_PROFANITY = {
    # Keep this small and extend as needed; avoid false positives.
    'idiot',
    'stupid',
    'moron',
}


@dataclass
class ModerationResult:
    allowed: bool
    sanitized_text: str
    warning: Optional[str] = None
    strike: bool = False


def sanitize_text(text: str) -> str:
    text = strip_tags(text or '')
    text = text.replace('\x00', '')
    text = text.strip()
    if len(text) > MESSAGE_MAX_LENGTH:
        text = text[:MESSAGE_MAX_LENGTH]
    return text


def _contains_any(patterns, text: str) -> bool:
    return any(p.search(text) for p in patterns)


def moderate_text(text: str) -> ModerationResult:
    sanitized = sanitize_text(text)
    lowered = sanitized.lower()

    if not sanitized:
        return ModerationResult(allowed=False, sanitized_text='', warning='Message is empty.')

    if _contains_any(_CREDENTIAL_PATTERNS, lowered):
        return ModerationResult(
            allowed=False,
            sanitized_text=sanitized,
            warning='For your safety, do not share passwords, OTPs, or login details in chat.',
            strike=True,
        )

    if _contains_any(_SCAM_PATTERNS, lowered):
        return ModerationResult(
            allowed=False,
            sanitized_text=sanitized,
            warning='This message looks like a potential scam/phishing attempt and was blocked.',
            strike=True,
        )

    if _contains_any(_CONTACT_OR_OFFPLATFORM_PATTERNS, lowered):
        return ModerationResult(
            allowed=False,
            sanitized_text=sanitized,
            warning='Please keep communication on UniCart for safety. Contact/off-platform requests are blocked.',
            strike=True,
        )

    words = {w.strip(".,!?()[]{}\"'`).") for w in lowered.split()}
    if _PROFANITY.intersection(words):
        return ModerationResult(
            allowed=False,
            sanitized_text=sanitized,
            warning='Offensive language is not allowed. Please keep it respectful.',
            strike=True,
        )

    return ModerationResult(allowed=True, sanitized_text=sanitized)


def check_rate_limits(
    membership: ConversationMembership,
    conversation: Conversation,
    *,
    proposed_hash: Optional[str] = None,
) -> Optional[str]:
    now = timezone.now()

    if membership.is_muted():
        return 'You are temporarily restricted from sending messages in this chat.'

    last = (
        Message.objects
        .filter(conversation=conversation, sender=membership.user)
        .order_by('-created_at')
        .first()
    )
    if last and (now - last.created_at).total_seconds() < COOLDOWN_SECONDS:
        return 'You are sending messages too quickly. Please slow down.'

    window_start = now - timedelta(seconds=WINDOW_SECONDS)
    sent_in_window = Message.objects.filter(
        conversation=conversation,
        sender=membership.user,
        created_at__gte=window_start,
    ).count()
    if sent_in_window >= MAX_MESSAGES_PER_WINDOW:
        return 'Too many messages in a short time. Please wait a bit.'

    if proposed_hash:
        recent_start = now - timedelta(seconds=RECENT_DUP_SECONDS)
        dup_count = (
            Message.objects
            .filter(
                conversation=conversation,
                sender=membership.user,
                created_at__gte=recent_start,
                content_hash=proposed_hash,
            )
            .count()
        )
        if dup_count >= MAX_DUP_IN_RECENT:
            return 'Please do not repeatedly send the same message.'

    return None


def apply_strike(membership: ConversationMembership, reason: str) -> None:
    membership.strikes = (membership.strikes or 0) + 1
    now = timezone.now()
    if membership.strikes >= 6:
        membership.muted_until = max(membership.muted_until or now, now + timedelta(days=1))
    elif membership.strikes >= 3:
        membership.muted_until = max(membership.muted_until or now, now + timedelta(minutes=10))
    membership.save(update_fields=['strikes', 'muted_until'])
