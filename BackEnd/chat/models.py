from django.db import models
from datetime import datetime
# مدل گروه چت
class Room(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# مدل پیام‌ها
class Message(models.Model):
    room = models.ForeignKey(Room, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.user.email}: {self.content[:20]}"


# مدل عضویت کاربران در گروه‌ها
class RoomMembership(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    can_send_messages = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.email} in {self.room.title}"
