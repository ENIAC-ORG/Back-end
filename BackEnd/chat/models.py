
# from django.db import models
# from django.contrib.auth.models import User

# class ChatRoom(models.Model):
#     name = models.CharField(max_length=255, unique=True)  
#     owner = models.ForeignKey(User, related_name="rooms", on_delete=models.CASCADE)  
#     created_at = models.DateTimeField(auto_now_add=True)  

#     def __str__(self):
#         return self.name

#     class Meta:
#         ordering = ['-created_at'] 
    

# class Message(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
#     room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)  
#     content = models.TextField()  
#     timestamp = models.DateTimeField(auto_now_add=True)  
#     is_server_message = models.BooleanField(default=False)  

#     def __str__(self):
#         return f"Message by {self.user.username if self.user else 'Server'} at {self.timestamp}"

#     class Meta:
#         ordering = ['timestamp']  