from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import  Room, RoomMembership

@receiver(post_save, sender=Room)
def add_user_to_rooms(sender, instance, created, **kwargs):
    """
    Automatically add a all user to new room after creation.
    """
    if created:  # Check if this is a new user
        users = User.objects.all()  # Fetch all existing rooms
        for user in users:
            RoomMembership.objects.get_or_create(user=user, room=instance)