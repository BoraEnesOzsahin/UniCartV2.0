import json
import hashlib

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import Conversation, ConversationMembership, Message, MessageReceipt
from .services import apply_strike, check_rate_limits, moderate_text


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.conversation_id = int(self.scope['url_route']['kwargs']['conversation_id'])
        allowed = await self._is_member(user.id, self.conversation_id)
        if not allowed:
            await self.close(code=4403)
            return

        self.group_name = f'chat_{self.conversation_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Mark messages read on connect
        await self._mark_read(user.id, self.conversation_id)
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'chat.read', 'user_id': user.id, 'read_at': timezone.now().isoformat()},
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            return

        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except Exception:
            return

        msg_type = data.get('type')
        if msg_type == 'send_message':
            text = (data.get('text') or '')
            result = await self._create_text_message(user.id, self.conversation_id, text)
            await self.send(text_data=json.dumps({'type': 'send_result', 'ok': result.get('ok', False), 'error': result.get('error', '')}))
            if result.get('ok') and result.get('payload'):
                await self.channel_layer.group_send(
                    self.group_name,
                    {'type': 'chat.message', 'message': result['payload']},
                )
        elif msg_type == 'mark_read':
            await self._mark_read(user.id, self.conversation_id)
            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'chat.read', 'user_id': user.id, 'read_at': timezone.now().isoformat()},
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({'type': 'message', 'message': event['message']}))

    async def chat_read(self, event):
        await self.send(text_data=json.dumps({'type': 'read', 'user_id': event['user_id'], 'read_at': event['read_at']}))

    @sync_to_async
    def _is_member(self, user_id: int, conversation_id: int) -> bool:
        return ConversationMembership.objects.filter(conversation_id=conversation_id, user_id=user_id).exists()

    @sync_to_async
    def _mark_read(self, user_id: int, conversation_id: int) -> None:
        MessageReceipt.objects.filter(
            user_id=user_id,
            read_at__isnull=True,
            message__conversation_id=conversation_id,
        ).update(read_at=timezone.now())

    @sync_to_async
    def _create_text_message(self, user_id: int, conversation_id: int, text: str):
        conversation = Conversation.objects.select_related('buyer', 'seller').get(id=conversation_id)
        membership = ConversationMembership.objects.get(conversation=conversation, user_id=user_id)
        if conversation.is_blocked():
            return {'ok': False, 'error': 'Conversation is blocked.'}

        proposed_hash = ''
        if text:
            normalized = ' '.join(text.lower().split())
            proposed_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()

        rate_error = check_rate_limits(membership, conversation, proposed_hash=proposed_hash or None)
        if rate_error:
            return {'ok': False, 'error': rate_error}

        mod = moderate_text(text)
        if not mod.allowed:
            if mod.strike:
                apply_strike(membership, mod.warning or 'policy')
            return {'ok': False, 'error': mod.warning or 'Message blocked.'}

        message = Message.objects.create(conversation=conversation, sender_id=user_id, text=mod.sanitized_text)

        recipient = conversation.other_party(membership.user)
        if recipient:
            MessageReceipt.objects.create(message=message, user=recipient)

        ConversationMembership.objects.filter(conversation=conversation).update(hidden_at=None)
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=['last_message_at'])

        payload = {
            'id': message.id,
            'sender_id': message.sender_id,
            'sender_username': membership.user.username,
            'text': message.text,
            'image_url': '',
            'created_at': message.created_at.isoformat(),
        }

        return {'ok': True, 'payload': payload}
