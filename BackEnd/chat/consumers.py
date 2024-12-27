import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

# Helper function to get user from token
def get_user_from_token(token):
    try:
        decoded_data = AccessToken(token)
        user_id = decoded_data['user_id']
        user = User.objects.get(id=user_id)
        return user
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

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
        token = data['token']  # Receive token from the frontend

        # Fetch user details asynchronously
        user = await sync_to_async(get_user_from_token)(token)

        if user:
            username = f"{user.firstname} {user.lastname}"  # Construct username as fullname

            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'sender_email': user.email  # Add sender email for is_self check
                }
            )
        else:
            # If user is not found, send an error message
            await self.send(text_data=json.dumps({
                'error': 'Invalid token. User not found.'
            }))

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        sender_email = event['sender_email']

        # Check if the message belongs to the current user
        is_self = self.scope["user"].email == sender_email if self.scope["user"].is_authenticated else False

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'is_self': is_self  # Add the flag to the response
        }))
