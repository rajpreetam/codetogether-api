from django.urls import path
from code_together.consumers.code_consumer import CodeConsumer
from code_together.consumers.chat_consumer import ChatConsumer

websocket_urlpatterns = [
    path('ws/code/<str:room_id>/<str:username>', CodeConsumer.as_asgi()),
    path('ws/chat/<str:room_id>/<str:username>', ChatConsumer.as_asgi()),
]
