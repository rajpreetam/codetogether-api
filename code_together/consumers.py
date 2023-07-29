import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import RoomGroup
import time


class CodeConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group = None
        self.room_id = None
        self.username = None
        self.room_group_name = None

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = self.room_id
        # self.room_group, room_created = RoomGroup.objects.get_or_create(room_id=self.room_id)

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
        source_code = text_data_json['source_code']
        language_id = text_data_json['language_id']
        input_text = text_data_json['input_text']
        output_text = text_data_json['output_text']
        disable_editor = text_data_json['disable_editor']
        console_text = text_data_json['console_text']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'write.source.code',
                'source_code': source_code,
                'language_id': language_id,
                'input_text': input_text,
                'output_text': output_text,
                'disable_editor': disable_editor,
                'console_text': console_text,
                'username': self.username,
                'sender_channel_name': self.channel_name
            }
        )

    async def write_source_code(self, event):
        source_code = event['source_code']
        language_id = event['language_id']
        input_text = event['input_text']
        output_text = event['output_text']
        disable_editor = event['disable_editor']
        console_text = event['console_text']
        username = event['username']

        # Send source_code to WebSocket
        # if self.channel_name != event.get('sender_channel_name'):
        await self.send(text_data=json.dumps({
            'source_code': source_code,
            'language_id': language_id,
            'input_text': input_text,
            'output_text': output_text,
            'disable_editor': disable_editor,
            'console_text': console_text,
            'username': username
        }))

