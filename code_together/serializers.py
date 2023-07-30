from rest_framework.serializers import ModelSerializer
from .models import ActiveUser, RoomGroup, ChatMassage
from accounts.serializers import UserSerializer


class ActiveUsersSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ActiveUser
        fields = ['user']
