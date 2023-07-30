from django.contrib import admin
from .models import RoomGroup, ActiveUser, ChatMassage

admin.site.register(RoomGroup)
admin.site.register(ActiveUser)
admin.site.register(ChatMassage)
