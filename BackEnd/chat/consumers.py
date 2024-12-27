import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from .models import Room, Message, RoomMembership
from django.contrib.auth import get_user_model

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
        # دریافت `room_id` از آدرس
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # اعتبارسنجی وجود اتاق
        room_exists = await sync_to_async(Room.objects.filter(id=self.room_id).exists)()
        if not room_exists:
            await self.close()
            return

        token = self.scope.get('query_string', None)
        if token:
            token = token.decode()  # برای استفاده از token به صورت رشته باید decode کنید

        if not token:
            await self.close()
            return
        # بررسی عضویت کاربر در اتاق
        user = await sync_to_async(get_user_from_token)(token)
        if not user:
            await self.send(text_data=json.dumps({
                'error': 'Invalid token. User not found.'
            }))
            return

        is_member = await sync_to_async(RoomMembership.objects.filter)(
            user=user, room_id=self.room_id
        ).exists()

        if not is_member:
            await self.close()
            return

        # ارسال پیام‌های قبلی به کاربر
        room = await sync_to_async(Room.objects.get)(id=self.room_id)
        messages = await sync_to_async(list)(room.messages.order_by('created_at').all())

        for message in messages:
            await self.send(text_data=json.dumps({
                'message': message.content,
                'username': f"{message.user.firstname} {message.user.lastname}",
                'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_self': user.id == message.user.id  # بررسی اینکه آیا پیام متعلق به کاربر است
            }))

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
        # دریافت داده‌های پیام
        data = json.loads(text_data)
        message = data.get('message')
        token = data.get('token')

        # دریافت کاربر از توکن
        user = await sync_to_async(get_user_from_token)(token)
        if not user:
            await self.send(text_data=json.dumps({
                'error': 'Invalid token. User not found.'
            }))
            return

        # بررسی عضویت و مجوز ارسال پیام
        membership = await sync_to_async(RoomMembership.objects.filter)(
            user=user, room_id=self.room_id
        ).first()
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

        # ارسال پیام به بقیه کاربران گروه
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': f"{user.firstname} {user.lastname}",
                'sender_email': user.email,  # ایمیل برای بررسی مالکیت پیام ارسال می‌شود
                'timestamp': new_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )

    async def chat_message(self, event):
        # دریافت پیام برای ارسال به کاربران
        message = event['message']
        username = event['username']
        sender_email = event['sender_email']
        timestamp = event['timestamp']

        # ارسال پیام به کاربر
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp,
            'is_self': self.scope["user"].email == sender_email  # بررسی اینکه آیا پیام متعلق به کاربر است
        }))
