from rest_framework import serializers
from .models import Room, Message, RoomMembership

# Serializer برای گروه‌ها
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'title', 'description', 'created_by']


# Serializer برای پیام‌ها
class MessageSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # نمایش نام کاربر

    class Meta:
        model = Message
        fields = ['id', 'user', 'content', 'created_at', 'room']


# Serializer برای عضویت در گروه‌ها
class RoomMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMembership
        fields = ['user', 'room', 'can_send_messages', 'is_hidden']
