from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from listings.models import Listing

from .forms import ImageUploadForm, ReportConversationForm
from .models import Conversation, ConversationMembership, ConversationReport, Message, MessageReceipt
from .services import apply_strike, check_rate_limits, moderate_text, sanitize_text


def _get_membership_or_404(conversation: Conversation, user) -> ConversationMembership:
    membership = ConversationMembership.objects.filter(conversation=conversation, user=user).first()
    if not membership:
        raise Http404
    return membership


@login_required
def inbox(request):
    conversations = list(
        Conversation.objects
        .filter(Q(buyer=request.user) | Q(seller=request.user))
        .select_related('listing', 'buyer', 'seller')
        .order_by('-last_message_at', '-created_at')
    )

    hidden_ids = set(
        ConversationMembership.objects
        .filter(user=request.user, hidden_at__isnull=False)
        .values_list('conversation_id', flat=True)
    )
    conversations = [c for c in conversations if c.id not in hidden_ids]

    # unread counts per conversation
    unread_counts = dict(
        MessageReceipt.objects
        .filter(user=request.user, read_at__isnull=True)
        .values('message__conversation_id')
        .annotate(cnt=Count('id'))
        .values_list('message__conversation_id', 'cnt')
    )

    rows = []
    for c in conversations:
        rows.append({
            'conversation': c,
            'other_user': c.other_party(request.user),
            'unread_count': unread_counts.get(c.id, 0),
        })

    return render(request, 'chats/inbox.html', {
        'rows': rows,
    })


@login_required
@require_POST
def start_conversation(request, listing_id: int):
    listing = get_object_or_404(Listing, id=listing_id, is_active=True)
    if listing.seller_id == request.user.id:
        messages.info(request, 'You cannot message yourself about your own listing.')
        return redirect('listing_detail', pk=listing.id)

    with transaction.atomic():
        conversation, created = Conversation.objects.get_or_create(
            listing=listing,
            buyer=request.user,
            defaults={
                'seller': listing.seller,
            }
        )
        if not created and conversation.seller_id != listing.seller_id:
            conversation.seller = listing.seller
            conversation.save(update_fields=['seller'])

        ConversationMembership.objects.get_or_create(
            conversation=conversation,
            user=conversation.buyer,
            defaults={'role': ConversationMembership.ROLE_BUYER},
        )
        ConversationMembership.objects.get_or_create(
            conversation=conversation,
            user=conversation.seller,
            defaults={'role': ConversationMembership.ROLE_SELLER},
        )

        # Unhide for buyer when they start
        ConversationMembership.objects.filter(conversation=conversation, user=request.user).update(hidden_at=None)

    return redirect('chat_detail', conversation_id=conversation.id)


@login_required
def conversation_detail(request, conversation_id: int):
    conversation = get_object_or_404(Conversation.objects.select_related('listing', 'buyer', 'seller'), id=conversation_id)
    membership = _get_membership_or_404(conversation, request.user)

    # mark receipts as read
    now = timezone.now()
    MessageReceipt.objects.filter(
        user=request.user,
        read_at__isnull=True,
        message__conversation=conversation,
    ).update(read_at=now)

    # Unhide on open
    if membership.hidden_at:
        membership.hidden_at = None
        membership.save(update_fields=['hidden_at'])

    messages_qs = (
        Message.objects
        .filter(conversation=conversation)
        .select_related('sender')
        .prefetch_related('receipts')
    )
    messages_list = list(messages_qs)
    for m in messages_list:
        m.delivery_state = ''
        if m.sender_id == request.user.id:
            receipt = next((r for r in m.receipts.all() if r.user_id != request.user.id), None)
            if receipt and receipt.read_at:
                m.delivery_state = 'Read'
            elif receipt:
                m.delivery_state = 'Delivered'

    return render(request, 'chats/detail.html', {
        'conversation': conversation,
        'membership': membership,
        'chat_messages': messages_list,
        'image_form': ImageUploadForm(),
    })


@login_required
@require_POST
def hide_conversation(request, conversation_id: int):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    membership = _get_membership_or_404(conversation, request.user)
    membership.hidden_at = timezone.now()
    membership.save(update_fields=['hidden_at'])
    return redirect('chat_inbox')


@login_required
@require_POST
def block_conversation(request, conversation_id: int):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    _get_membership_or_404(conversation, request.user)
    conversation.blocked_at = timezone.now()
    conversation.blocked_by = request.user
    conversation.block_reason = sanitize_text(request.POST.get('reason', ''))[:200]
    conversation.save(update_fields=['blocked_at', 'blocked_by', 'block_reason'])
    messages.warning(request, 'You blocked this conversation. No further messages can be sent.')
    return redirect('chat_detail', conversation_id=conversation.id)


@login_required
@require_POST
def unblock_conversation(request, conversation_id: int):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    _get_membership_or_404(conversation, request.user)
    # Only the blocker can unblock
    if conversation.blocked_by_id != request.user.id:
        raise Http404
    conversation.blocked_at = None
    conversation.blocked_by = None
    conversation.block_reason = ''
    conversation.save(update_fields=['blocked_at', 'blocked_by', 'block_reason'])
    messages.success(request, 'Conversation unblocked.')
    return redirect('chat_detail', conversation_id=conversation.id)


@login_required
def report_conversation(request, conversation_id: int):
    conversation = get_object_or_404(Conversation.objects.select_related('buyer', 'seller'), id=conversation_id)
    _get_membership_or_404(conversation, request.user)

    other = conversation.other_party(request.user)
    if not other:
        raise Http404

    if request.method == 'POST':
        form = ReportConversationForm(request.POST)
        if form.is_valid():
            ConversationReport.objects.create(
                conversation=conversation,
                reporter=request.user,
                reported_user=other,
                reason=form.cleaned_data['reason'],
                details=form.cleaned_data.get('details', ''),
            )
            messages.success(request, 'Report submitted. Thank you for keeping UniCart safe.')
            return redirect('chat_detail', conversation_id=conversation.id)
    else:
        form = ReportConversationForm()

    return render(request, 'chats/report.html', {
        'conversation': conversation,
        'form': form,
        'other_user': other,
    })


@login_required
@require_POST
def upload_image(request, conversation_id: int):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    membership = _get_membership_or_404(conversation, request.user)

    if conversation.is_blocked():
        return JsonResponse({'ok': False, 'error': 'Conversation is blocked.'}, status=403)

    rate_error = check_rate_limits(membership, conversation)
    if rate_error:
        return JsonResponse({'ok': False, 'error': rate_error}, status=429)

    form = ImageUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'error': 'Invalid image.'}, status=400)

    # Pillow verify to reduce malformed image abuse
    from PIL import Image
    img = form.cleaned_data['image']
    try:
        Image.open(img).verify()
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Image failed validation.'}, status=400)

    with transaction.atomic():
        message = Message.objects.create(conversation=conversation, sender=request.user, image=img)
        recipient = conversation.other_party(request.user)
        if recipient:
            MessageReceipt.objects.create(message=message, user=recipient)

        ConversationMembership.objects.filter(conversation=conversation).update(hidden_at=None)
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=['last_message_at'])

    _broadcast_message(conversation.id, message)
    return JsonResponse({'ok': True})


def _broadcast_message(conversation_id: int, message: Message):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    payload = {
        'id': message.id,
        'sender_id': message.sender_id,
        'sender_username': getattr(message.sender, 'username', ''),
        'text': message.text or '',
        'image_url': message.image.url if message.image else '',
        'created_at': message.created_at.isoformat(),
    }
    async_to_sync(channel_layer.group_send)(
        f'chat_{conversation_id}',
        {'type': 'chat.message', 'message': payload},
    )
