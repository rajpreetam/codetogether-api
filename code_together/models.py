from django.db import models


class RoomGroup(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.CharField(max_length=36)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.room_id
