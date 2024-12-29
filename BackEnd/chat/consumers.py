import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import Room, RoomMembership

        # دریافت `room_id` از آدرس
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # اعتبارسنجی وجود اتاق
        room_exists = await sync_to_async(Room.objects.filter(id=self.room_id).exists)()
        if not room_exists:
            await self.close()
            return

        u_email = self.scope.get('query_string', None)
        if u_email:
            u_email = u_email.decode()  # برای استفاده از ایمیل به صورت رشته باید decode کنید

        if not u_email:
            await self.close()
            return

        # Fetch user details asynchronously
        user = await sync_to_async(User.objects.get)(email=u_email)
        
        # بررسی عضویت کاربر در اتاق
        if not user:
            await self.send(text_data=json.dumps({
                'error': 'Invalid token. User not found.'
            }))
            return

        is_member = await sync_to_async(
            lambda: RoomMembership.objects.filter(user=user, room_id=self.room_id).exists()
        )()

        if not is_member:
            await self.close()
            return

        # ارسال پیام‌های قبلی به کاربر
        room = await sync_to_async(Room.objects.get)(id=self.room_id)
        messages = await sync_to_async(list)(room.messages.order_by('created_at').select_related('user').all())
        # اضافه کردن کاربر به گروه
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # حذف کاربر از گروه
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from .models import Room, Message, RoomMembership
        
        data = json.loads(text_data)
        message = data.get('message')
        user_email = data.get('email')

        # Fetch user details asynchronously
        user = await sync_to_async(User.objects.get)(email=user_email)

        if not user:
            await self.send(text_data=json.dumps({
                'error': 'Invalid email. User not found.'
            }))
            return

        # بررسی عضویت و مجوز ارسال پیام
     
        membership = await sync_to_async(RoomMembership.objects.filter(
            user=user, room_id=self.room_id).first()
        )()
        
        if not membership or not membership.can_send_messages:
            await self.send(text_data=json.dumps({
                'error': 'You do not have permission to send messages in this room.'
            }))
            return

        # ذخیره پیام در دیتابیس
        room = await sync_to_async(Room.objects.get)(id=self.room_id)
        new_message = await sync_to_async(Message.objects.create)(
            room=room,
            user=user,
            content=message
        )

        # ارسال پیام به بقیه کاربران گروه (Broadcast to the group)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': new_message.id,
                'content': new_message.content,
                'created_at': new_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'firstname': user.firstname,
                'lastname': user.lastname,
                'is_self': user.id == new_message.user.id
            }
        )

    async def chat_message(self, event):
        # دریافت پیام برای ارسال به کاربران
        message = event['content']
        username = f"{event['firstname']} {event['lastname']}"
        timestamp = event['created_at']
        is_self = event['is_self']

        # ارسال پیام به همه کاربران در گروه
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'content': message,
            'created_at': timestamp,
            'firstname': event['firstname'],
            'lastname': event['lastname'],
            'is_self': is_self
        }))


# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async

# #from .models import Room, Message, RoomMembership
# from django.contrib.auth import get_user_model

# User = get_user_model()

# # Helper function to get user from token
# # def get_user_from_token(token):
# #     try:
# #         from rest_framework_simplejwt.tokens import AccessToken
# #         decoded_data = AccessToken(token)
# #         user_id = decoded_data['user_id']
# #         user = User.objects.get(id=user_id)
# #         return user
# #     except Exception as e:
# #         print(f"Error decoding token: {e}")
# #         return None


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         from .models import Room, Message, RoomMembership
#         # دریافت `room_id` از آدرس
#         self.room_id = self.scope['url_route']['kwargs']['room_id']
#         self.room_group_name = f'chat_{self.room_id}'

#         # اعتبارسنجی وجود اتاق
#         room_exists = await sync_to_async(Room.objects.filter(id=self.room_id).exists)()
#         if not room_exists:
#             await self.close()
#             return

#         u_email = self.scope.get('query_string', None)
#         if u_email:
#             u_email = u_email.decode()  # برای استفاده از ایمیل به صورت رشته باید decode کنید

#         if not u_email:
#             await self.close()
#             return
#         User = get_user_model()
#         # Fetch user details asynchronously
#         user = await sync_to_async(User.objects.get)(email=u_email)
#         # بررسی عضویت کاربر در اتاق
#         if not user:
#             await self.send(text_data=json.dumps({
#                 'error': 'Invalid token. User not found.'
#             }))
#             return

#         is_member = await sync_to_async(
#             lambda: RoomMembership.objects.filter(
#             user=user, room_id=self.room_id).exists()
#             )()

#         if not is_member:
#             await self.close()
#             return

#         # ارسال پیام‌های قبلی به کاربر
#         room = await sync_to_async(Room.objects.get)(id=self.room_id)
#         messages = await sync_to_async(list)(room.messages.order_by('created_at').select_related('user').all())

#         for message in messages:
#             if message:  # Ensure the message exists
#                 # Ensure user is accessed in a sync-to-async manner
#                 firstname = await sync_to_async(lambda: message.user.firstname if message.user else None)()
#                 lastname = await sync_to_async(lambda: message.user.lastname if message.user else None)()

#                 await self.send(text_data=json.dumps({
#                     'id': message.id if message.id else None,  # Check if message ID exists
#                     'content': message.content if message.content else '',  # Fallback to empty string if content is None
#                     'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S') if message.created_at else None,  # Check if created_at exists
#                     'firstname': firstname,  # Fetched using sync_to_async
#                     'lastname': lastname,  # Fetched using sync_to_async
#                     'is_self': user.id == message.user.id if message.user else False  # Validate user association
#                 }))

#         # اضافه کردن کاربر به گروه
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         # حذف کاربر از گروه
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         # دریافت داده‌های پیام
#         from .models import Room, Message, RoomMembership
#         data = json.loads(text_data)
#         message = data.get('message')
#         user_email = data.get('email')
#         User = get_user_model()
#         # Fetch user details asynchronously
#         user = await sync_to_async(User.objects.get)(email=user_email)

#         # دریافت کاربر از توکن
#         print( " this user   : " , user )
#         print( " this message : " , message )
#         if not user:
#             await self.send(text_data=json.dumps({
#                 'error': 'Invalid email. User not found.'
#             }))
#             return

#         # بررسی عضویت و مجوز ارسال پیام
#         membership = await sync_to_async(RoomMembership.objects.filter)(
#             user=user, room_id=self.room_id
#         ).first()
#         if not membership or not membership.can_send_messages:
#             await self.send(text_data=json.dumps({
#                 'error': 'You do not have permission to send messages in this room.'
#             }))
#             return

#         # ذخیره پیام در دیتابیس
#         room = await sync_to_async(Room.objects.get)(id=self.room_id)
#         new_message = await sync_to_async(Message.objects.create)(
#             room=room,
#             user=user,
#             content=message
#         )

#         # ارسال پیام به بقیه کاربران گروه
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'id': new_message.id,  # شناسه پیام
#                 'content': new_message.content,  # محتوای پیام
#                 'created_at': new_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # زمان ایجاد
#                 'firstname': user.firstname,  # نام کاربر
#                 'lastname': user.lastname,  # نام خانوادگی کاربر
#                 'is_self': user.id == new_message.user.id  # بررسی اینکه آیا پیام متعلق به کاربر است
#             }
#         )


#     async def chat_message(self, event):
#         # دریافت پیام برای ارسال به کاربران
#         message = event['content']
#         username = f"{event['firstname']} {event['lastname']}"
#         timestamp = event['created_at']
#         is_self = event['is_self']

#         # ارسال پیام به کاربر
#         await self.send(text_data=json.dumps({
#             'id': event['id'],  # شناسه پیام
#             'content': message,  # محتوای پیام
#             'created_at': timestamp,  # زمان ایجاد
#             'firstname': event['firstname'],  # نام کاربر
#             'lastname': event['lastname'],  # نام خانوادگی کاربر
#             'is_self': is_self  # بررسی اینکه آیا پیام متعلق به کاربر است
#         }))

