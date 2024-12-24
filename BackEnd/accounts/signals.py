from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from chat.models import  Room, RoomMembership

@receiver(post_save, sender=User)
def add_user_to_rooms(sender, instance, created, **kwargs):
    """
    Automatically add a new user to all existing rooms after creation.
    """
    if created:  # Check if this is a new user
        rooms = Room.objects.all()  # Fetch all existing rooms
        for room in rooms:
            RoomMembership.objects.get_or_create(user=instance, room=room)