from django.conf import settings
from django.db import models
# from accounts.models import User


class Conversation(models.Model):
    name = models.CharField(max_length=255, blank=True)  #  unique=True,
    owner = models.ForeignKey('accounts.User', related_name="conversation", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]


class ConMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    message = models.TextField(null=True, blank=True)
    emotion = models.JSONField(null=True, blank=True)
    disorder = models.JSONField(null=True, blank=True)
    validation = models.JSONField(null=True, blank=True)
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user.username if self.user else 'Server'} at {self.timestamp}"

    class Meta:
        ordering = ["timestamp"]
