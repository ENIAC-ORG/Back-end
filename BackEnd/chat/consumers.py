
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
# from accounts.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user_email = data['email']
        User = get_user_model()
        # Fetch user details asynchronously
        user = await sync_to_async(User.objects.get)(email=user_email)
        username = f"{user.firstname} {user.lastname}"  # Construct username as fullname

        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'sender_email': user_email  # Add sender email for is_self check
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        sender_email = event['sender_email']

        # Check if the message belongs to the current user
        is_self = self.scope["user"].email == sender_email

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'is_self': is_self  # Add the flag to the response
        }))
