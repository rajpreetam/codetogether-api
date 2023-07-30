import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from accounts.serializers import UserSerializer


@database_sync_to_async
def get_user(username):
    try:
        user = User.objects.get(username=username)
        serializer = UserSerializer(user, many=False)
        return serializer.data
    except Exception as e:
        print(e)
        return None


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.username = None
        self.room_id = None

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f"chatroom_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        chat_message = text_data_json.get('chat_message')
        user = await get_user(self.username)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'write.chat',
                'chat_message': chat_message,
                'user': user
            }
        )

    async def write_chat(self, event):
        chat_message = event.get('chat_message')
        user = event.get('user')

        await self.send(
            text_data=json.dumps({
                'chat_message': chat_message,
                'user': user
            })
        )

