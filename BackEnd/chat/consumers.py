# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# from channels.db import database_sync_to_async

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         from .models import Message, ChatRoom
#         from django.contrib.auth.models import User
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'chat_{self.room_name}'

#         self.room = await database_sync_to_async(ChatRoom.objects.get)(name=self.room_name)

#         if self.room.owner != self.scope['user']:
#             await self.close()  
            
#         welcome_message = f"خوش اومدی. چطور میتونم کمکت کنم؟"
#         await database_sync_to_async(self.save_server_message)(welcome_message)

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()

#     async def disconnect(self, close_code):

#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message_content = text_data_json['message']
#         user = self.scope["user"]

#         await database_sync_to_async(self.save_message)(user, message_content)

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message_content,
#             }
#         )

#         server_response = await database_sync_to_async(self.generate_server_response)(message_content)

#         await database_sync_to_async(self.save_server_message)(server_response)

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': server_response,
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']

#         await self.send(text_data=json.dumps({
#             'message': message
#         }))

#     def save_message(self, user, message_content):
#         from .models import Message, ChatRoom
#         from django.contrib.auth.models import User
#         Message.objects.create(user=user, room=self.room, content=message_content)

#     def save_server_message(self, message_content):
#         from .models import Message, ChatRoom
#         from django.contrib.auth.models import User
#         Message.objects.create(user=None, room=self.room, content=message_content, is_server_message=True)

#     def generate_server_response(self, user_message):
#         return f"Server Response to: {user_message}"

