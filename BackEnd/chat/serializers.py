from rest_framework import serializers
from .models import Room, Message, RoomMembership

# Serializer برای گروه‌ها
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'title', 'description', 'created_by']


# Serializer برای پیام‌ها
class MessageSerializer(serializers.ModelSerializer):
    firstname = serializers.SerializerMethodField()
    lastname = serializers.SerializerMethodField()
    user = serializers.StringRelatedField() 
    class Meta:
        model = Message
        fields = ['id','user', 'content', 'created_at', 'firstname', 'lastname']

    def get_firstname(self, obj):
        return obj.user.firstname if obj.user.firstname else "مهمان"

    def get_lastname(self, obj):
        return obj.user.lastname if obj.user.lastname else "سایت"


# Serializer برای عضویت در گروه‌ها
class RoomMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMembership
        fields = ['user', 'room', 'can_send_messages', 'is_hidden']
