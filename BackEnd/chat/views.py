from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Room, Message, RoomMembership
from .serializers import RoomSerializer, MessageSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view

# API View برای لیست کردن و ایجاد گروه‌ها
class RoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        # تنها ادمین می‌تواند گروه جدید ایجاد کند
        if not request.user.is_staff:
            return Response({"error": "Only admin can create rooms."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(created_by=request.user)
            RoomMembership.objects.create(user=request.user, room=room, can_send_messages=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# لیست کردن و ارسال پیام‌ها
class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        messages = Message.objects.filter(room=room)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        if not RoomMembership.objects.filter(room=room, user=request.user).exists():
            return Response({"error": "User not a member of this room."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, room=room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# حذف پیام‌ها
class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        if message.user != request.user and not request.user.is_staff:
            return Response({"error": "You do not have permission to delete this message."}, status=status.HTTP_403_FORBIDDEN)
        message.delete()
        return Response({"message": "Message deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# حذف گروه‌ها
class DeleteRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        if room.created_by != request.user and not request.user.is_staff:
            return Response({"error": "You do not have permission to delete this room."}, status=status.HTTP_403_FORBIDDEN)
        room.delete()
        return Response({"message": "Room deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ویرایش عنوان و توضیحات گروه
class UpdateRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        if room.created_by != request.user and not request.user.is_staff:
            return Response({"error": "You do not have permission to edit this room."}, status=status.HTTP_403_FORBIDDEN)

        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# مخفی کردن یا نمایش گروه‌ها برای کاربر
class ToggleRoomVisibilityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        room_membership, created = RoomMembership.objects.get_or_create(user=request.user, room=room)
        room_membership.is_hidden = not room_membership.is_hidden
        room_membership.save()

        return Response({"message": "Room visibility toggled."}, status=status.HTTP_200_OK)
