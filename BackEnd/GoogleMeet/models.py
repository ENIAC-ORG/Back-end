from django.db import models
from counseling.models import Psychiatrist  

class OAuthToken(models.Model):
    psychiatrist = models.ForeignKey(Psychiatrist, on_delete=models.CASCADE, related_name='oauth_tokens')
    user_email = models.EmailField(unique=True)
    token_data = models.JSONField()

    def __str__(self):
        return f"OAuthToken for {self.psychiatrist.get_fullname()} ({self.user_email})"
