from rest_framework import serializers
from .models import Conversation ,ConMessage

class ConMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConMessage
        fields = ['id', 'message', 'response']

class ConversionSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.email", read_only=True)
    class Meta:
        model = Conversation
        fields = ["id", "owner", "owner_username", "created_at", "name"]
