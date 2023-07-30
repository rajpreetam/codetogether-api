import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from code_together.models import RoomGroup, ActiveUser, ChatMassage
from django.contrib.auth.models import User
from ..serializers import ActiveUsersSerializer
import time


@database_sync_to_async
def create_room_in_db(room_id, username):
    try:
        room_group, _ = RoomGroup.objects.get_or_create(room_id=room_id)
        user = User.objects.get(username=username)
        active_user, _ = ActiveUser.objects.get_or_create(user=user, room=room_group)
        active_users = room_group.active_users.all()
        active_users = ActiveUsersSerializer(active_users, many=True).data
        return room_group, active_users
    except Exception as e:
        print(e)
        return None, None


@database_sync_to_async
def handle_disconnect_for_db(room_id, username):
    try:
        room_group = RoomGroup.objects.get(room_id=room_id)
        room_group.active_users.filter(user__username=username).delete()
        if room_group.active_users.all().count() == 0:
            room_group.delete()
    except Exception as e:
        print(e)


class CodeConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.active_users = None
        self.room_group = None
        self.room_id = None
        self.username = None
        self.room_group_name = None

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'code_room_{self.room_id}'
        self.room_group, self.active_users = await create_room_in_db(self.room_id, self.username)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user.joined',
                'new_username': self.username,
                'source_code': '',
                'language_id': '',
                'input_text': '',
                'output_text': '',
                'disable_editor': False,
                'console_text': '',
            }
        )
        await self.accept()

    async def disconnect(self, code):
        await handle_disconnect_for_db(self.room_id, self.username)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'write.source.code',
                'source_code': text_data_json['source_code'],
                'language_id': text_data_json['language_id'],
                'input_text': text_data_json['input_text'],
                'output_text': text_data_json['output_text'],
                'disable_editor': text_data_json['disable_editor'],
                'console_text': text_data_json['console_text'],
                'username': self.username,
                'active_users': self.active_users
            }
        )

    async def write_source_code(self, event):

        # Send source_code to WebSocket
        # if self.channel_name != event.get('sender_channel_name'):
        await self.send(text_data=json.dumps({
            'source_code': event['source_code'],
            'language_id': event['language_id'],
            'input_text': event['input_text'],
            'output_text': event['output_text'],
            'disable_editor': event['disable_editor'],
            'console_text': event['console_text'],
            'username': event['username'],
            'active_users': event['active_users']
        }))

    async def user_joined(self, event):
        await self.send(json.dumps({
            'new_username': event['new_username'],
            'source_code': event['source_code'],
            'language_id': event['language_id'],
            'input_text': event['input_text'],
            'output_text': event['output_text'],
            'disable_editor': event['disable_editor'],
            'console_text': event['console_text']
        }))
