from rest_framework import serializers
from .models import Room, Message, RoomMembership

# Serializer for Rooms
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'title', 'description', 'created_by']

# Serializer for Messages
class MessageSerializer(serializers.ModelSerializer):
    firstname = serializers.SerializerMethodField()
    lastname = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'user', 'content', 'created_at', 'firstname', 'lastname', 'is_self']

    def get_firstname(self, obj):
        return obj.user.firstname if obj.user.firstname else "مهمان"

    def get_lastname(self, obj):
        return obj.user.lastname if obj.user.lastname else "سایت"

    def get_is_self(self, obj):
        current_user = self.context.get('request').user
        return obj.user == current_user

# Serializer for Room Memberships
class RoomMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMembership
        fields = ['user', 'room', 'can_send_messages', 'is_hidden']
