from .models import MessageReceipt


def unread_chat_count(request):
    if not request.user.is_authenticated:
        return {'unread_chat_count': 0}

    unread = MessageReceipt.objects.filter(user=request.user, read_at__isnull=True).count()
    return {'unread_chat_count': unread}
